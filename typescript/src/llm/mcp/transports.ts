/**
 * MCP Transport implementations for TypeScript.
 *
 * Provides factory functions for creating MCPClient instances with
 * different transport modes: stdio, SSE, and streamable HTTP.
 *
 * Uses a resource pattern since TypeScript doesn't have native
 * async context managers like Python.
 */

import type { StdioServerParameters, MCPClientSession } from "./types";

import { MCPNotInstalledError, MCPConnectionError } from "./errors";
import { MCPClient } from "./mcp-client";

/**
 * Resource holder for MCP client with cleanup function.
 *
 * This pattern allows for both callback-style usage (using `using()`)
 * and manual lifecycle management.
 */
export interface MCPResource {
  /** The connected MCP client. */
  readonly client: MCPClient;
  /** Close the connection and clean up resources. */
  close(): Promise<void>;
}

/**
 * Execute a function with an MCP client resource, ensuring cleanup.
 *
 * This is the recommended pattern for TypeScript MCP usage,
 * similar to Python's async context manager.
 *
 * @param resource - A promise that resolves to an MCPResource.
 * @param fn - The function to execute with the client.
 * @returns The result of the function.
 *
 * @example
 * ```typescript
 * const result = await using(stdioClient(params), async (client) => {
 *   const tools = await client.listTools();
 *   const model = new Model({ model: 'openai/gpt-4', tools });
 *   let response = await model.call([{ role: 'user', content: 'Hello' }]);
 *   while (response.toolCalls.length > 0) {
 *     const toolOutputs = await response.executeTools();
 *     response = await response.resume(toolOutputs);
 *   }
 *   return response.content;
 * });
 * ```
 */
export async function using<T>(
  resource: Promise<MCPResource>,
  fn: (client: MCPClient) => Promise<T>,
): Promise<T> {
  const { client, close } = await resource;
  try {
    return await fn(client);
  } finally {
    await close();
  }
}

// Type for the MCP SDK's Client class
interface MCPClientClass {
  new (
    info: { name: string; version: string },
    options?: { capabilities?: Record<string, unknown> },
  ): {
    connect(transport: unknown): Promise<void>;
    close(): Promise<void>;
    listTools(): Promise<{
      tools: readonly {
        name: string;
        description?: string;
        inputSchema: Record<string, unknown>;
      }[];
    }>;
    callTool(request: {
      name: string;
      arguments: Record<string, unknown>;
    }): Promise<{
      content: readonly {
        type: string;
        text?: string;
        data?: string;
        mimeType?: string;
      }[];
    }>;
  };
}

// Cached MCP SDK module
let mcpClientClass: MCPClientClass | null = null;

async function getMCPClient(): Promise<MCPClientClass> {
  if (mcpClientClass) return mcpClientClass;

  try {
    const module = await import("@modelcontextprotocol/sdk/client/index.js");
    mcpClientClass = module.Client as MCPClientClass;
    return mcpClientClass;
  } catch {
    throw new MCPNotInstalledError();
  }
}

/**
 * Create an MCP client using stdio transport.
 *
 * This starts a subprocess and communicates via stdin/stdout.
 *
 * @param serverParameters - Configuration for the subprocess.
 * @returns A promise that resolves to an MCPResource.
 *
 * @example
 * ```typescript
 * const result = await using(
 *   stdioClient({ command: 'python', args: ['-m', 'my_mcp_server'] }),
 *   async (client) => {
 *     const tools = await client.listTools();
 *     const model = new Model({ model: 'openai/gpt-4', tools });
 *     let response = await model.call([{ role: 'user', content: 'Hello' }]);
 *     while (response.toolCalls.length > 0) {
 *       const toolOutputs = await response.executeTools();
 *       response = await response.resume(toolOutputs);
 *     }
 *     return response.content;
 *   }
 * );
 * ```
 */
export async function stdioClient(
  serverParameters: StdioServerParameters,
): Promise<MCPResource> {
  const Client = await getMCPClient();

  let StdioClientTransport: new (params: {
    command: string;
    args?: string[];
    env?: Record<string, string>;
    cwd?: string;
  }) => { close(): Promise<void> };

  try {
    const stdioModule =
      await import("@modelcontextprotocol/sdk/client/stdio.js");
    StdioClientTransport = stdioModule.StdioClientTransport;
  } catch {
    throw new MCPNotInstalledError();
  }

  try {
    const transport = new StdioClientTransport({
      command: serverParameters.command,
      args: serverParameters.args as string[] | undefined,
      env: serverParameters.env ?? undefined,
      cwd: serverParameters.cwd,
    });

    const mcpClient = new Client(
      { name: "mirascope", version: "1.0.0" },
      { capabilities: {} },
    );
    await mcpClient.connect(transport);

    // Create a session adapter that matches our MCPClientSession interface
    const session: MCPClientSession = {
      initialize: async () => {
        // Connection already initialized in connect()
      },
      listTools: async () => {
        const result = await mcpClient.listTools();
        return {
          tools: result.tools.map((t) => ({
            name: t.name,
            description: t.description,
            inputSchema: t.inputSchema as Record<string, unknown>,
          })),
        };
      },
      callTool: async (name, args) => {
        const result = await mcpClient.callTool({ name, arguments: args });
        return {
          content: result.content.map((c) => {
            // Cast to access annotations/meta which exist in protocol but not SDK types
            const block = c as {
              type: string;
              text?: string;
              data?: string;
              mimeType?: string;
              annotations?: unknown;
              meta?: unknown;
            };
            return {
              type: block.type,
              text: block.text,
              data: block.data,
              mimeType: block.mimeType,
              annotations: block.annotations,
              meta: block.meta,
            };
          }),
        };
      },
      close: async () => {
        await mcpClient.close();
      },
    };

    const client = new MCPClient(session);

    return {
      client,
      close: async () => {
        await mcpClient.close();
        await transport.close();
      },
    };
  } catch (error) {
    if (error instanceof MCPNotInstalledError) throw error;
    const err = error instanceof Error ? error : new Error(String(error));
    throw new MCPConnectionError(
      `Failed to connect to MCP server via stdio: ${err.message}`,
      err,
    );
  }
}

/**
 * Create an MCP client using SSE (Server-Sent Events) transport.
 *
 * Connects to an HTTP server that uses SSE for streaming.
 *
 * @param url - The SSE endpoint URL.
 * @param options - Optional configuration.
 * @returns A promise that resolves to an MCPResource.
 *
 * @example
 * ```typescript
 * const result = await using(
 *   sseClient('http://localhost:8000/sse'),
 *   async (client) => {
 *     const tools = await client.listTools();
 *     const model = new Model({ model: 'openai/gpt-4', tools });
 *     let response = await model.call([{ role: 'user', content: 'Hello' }]);
 *     while (response.toolCalls.length > 0) {
 *       const toolOutputs = await response.executeTools();
 *       response = await response.resume(toolOutputs);
 *     }
 *     return response.content;
 *   }
 * );
 * ```
 */
export async function sseClient(
  url: string,
  _options?: { readTimeoutMs?: number },
): Promise<MCPResource> {
  const Client = await getMCPClient();

  let SSEClientTransport: new (url: URL) => { close(): Promise<void> };

  try {
    const sseModule = await import("@modelcontextprotocol/sdk/client/sse.js");
    SSEClientTransport = sseModule.SSEClientTransport;
  } catch {
    throw new MCPNotInstalledError();
  }

  try {
    const transport = new SSEClientTransport(new URL(url));

    const mcpClient = new Client(
      { name: "mirascope", version: "1.0.0" },
      { capabilities: {} },
    );
    await mcpClient.connect(transport);

    // Create a session adapter that matches our MCPClientSession interface
    const session: MCPClientSession = {
      initialize: async () => {
        // Connection already initialized in connect()
      },
      listTools: async () => {
        const result = await mcpClient.listTools();
        return {
          tools: result.tools.map((t) => ({
            name: t.name,
            description: t.description,
            inputSchema: t.inputSchema as Record<string, unknown>,
          })),
        };
      },
      callTool: async (name, args) => {
        const result = await mcpClient.callTool({ name, arguments: args });
        return {
          content: result.content.map((c) => {
            // Cast to access annotations/meta which exist in protocol but not SDK types
            const block = c as {
              type: string;
              text?: string;
              data?: string;
              mimeType?: string;
              annotations?: unknown;
              meta?: unknown;
            };
            return {
              type: block.type,
              text: block.text,
              data: block.data,
              mimeType: block.mimeType,
              annotations: block.annotations,
              meta: block.meta,
            };
          }),
        };
      },
      close: async () => {
        await mcpClient.close();
      },
    };

    const client = new MCPClient(session);

    return {
      client,
      close: async () => {
        await mcpClient.close();
        await transport.close();
      },
    };
  } catch (error) {
    if (error instanceof MCPNotInstalledError) throw error;
    const err = error instanceof Error ? error : new Error(String(error));
    throw new MCPConnectionError(
      `Failed to connect to MCP server via SSE: ${err.message}`,
      err,
    );
  }
}

/**
 * Create an MCP client using streamable HTTP transport.
 *
 * Connects to an HTTP server that supports MCP's streamable HTTP protocol.
 *
 * @param url - The HTTP endpoint URL.
 * @returns A promise that resolves to an MCPResource.
 *
 * @example
 * ```typescript
 * const result = await using(
 *   streamableHttpClient('http://localhost:8000/mcp'),
 *   async (client) => {
 *     const tools = await client.listTools();
 *     const model = new Model({ model: 'openai/gpt-4', tools });
 *     let response = await model.call([{ role: 'user', content: 'Hello' }]);
 *     while (response.toolCalls.length > 0) {
 *       const toolOutputs = await response.executeTools();
 *       response = await response.resume(toolOutputs);
 *     }
 *     return response.content;
 *   }
 * );
 * ```
 */
export async function streamableHttpClient(url: string): Promise<MCPResource> {
  const Client = await getMCPClient();

  let StreamableHTTPClientTransport: new (url: URL) => {
    close(): Promise<void>;
  };

  try {
    const httpModule =
      await import("@modelcontextprotocol/sdk/client/streamableHttp.js");
    StreamableHTTPClientTransport = httpModule.StreamableHTTPClientTransport;
  } catch {
    throw new MCPNotInstalledError();
  }

  try {
    const transport = new StreamableHTTPClientTransport(new URL(url));

    const mcpClient = new Client(
      { name: "mirascope", version: "1.0.0" },
      { capabilities: {} },
    );
    await mcpClient.connect(transport);

    // Create a session adapter that matches our MCPClientSession interface
    const session: MCPClientSession = {
      initialize: async () => {
        // Connection already initialized in connect()
      },
      listTools: async () => {
        const result = await mcpClient.listTools();
        return {
          tools: result.tools.map((t) => ({
            name: t.name,
            description: t.description,
            inputSchema: t.inputSchema as Record<string, unknown>,
          })),
        };
      },
      callTool: async (name, args) => {
        const result = await mcpClient.callTool({ name, arguments: args });
        return {
          content: result.content.map((c) => {
            // Cast to access annotations/meta which exist in protocol but not SDK types
            const block = c as {
              type: string;
              text?: string;
              data?: string;
              mimeType?: string;
              annotations?: unknown;
              meta?: unknown;
            };
            return {
              type: block.type,
              text: block.text,
              data: block.data,
              mimeType: block.mimeType,
              annotations: block.annotations,
              meta: block.meta,
            };
          }),
        };
      },
      close: async () => {
        await mcpClient.close();
      },
    };

    const client = new MCPClient(session);

    return {
      client,
      close: async () => {
        await mcpClient.close();
        await transport.close();
      },
    };
  } catch (error) {
    if (error instanceof MCPNotInstalledError) throw error;
    const err = error instanceof Error ? error : new Error(String(error));
    throw new MCPConnectionError(
      `Failed to connect to MCP server via HTTP: ${err.message}`,
      err,
    );
  }
}
