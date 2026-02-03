/**
 * MCP Client for Mirascope TypeScript SDK.
 *
 * Wraps an MCP ClientSession and provides methods to list and convert
 * MCP tools to Mirascope-compatible Tool objects.
 */

import type { ToolCall } from "@/llm/content/tool-call";
import type { ToolParameterSchema } from "@/llm/tools/tool-schema";
import type { BaseTool } from "@/llm/tools/tools";
import type { Jsonable } from "@/llm/types/jsonable";

import { ToolOutput } from "@/llm/content/tool-output";
import { ToolExecutionError } from "@/llm/exceptions";
import { TOOL_TYPE } from "@/llm/tools/tools";

import type { MCPClientSession, MCPTool, MCPContentBlock } from "./types";

/**
 * Serialized MCP content block structure.
 */
interface SerializedContentBlock {
  readonly type: string;
  readonly text: string | null;
  readonly data: string | null;
  readonly mimeType: string | null;
  readonly annotations: unknown;
  readonly meta: unknown;
}

/**
 * Serialize MCP content blocks to Jsonable format.
 *
 * @param content - The MCP content blocks to serialize.
 * @returns JSON-serializable representation of the content.
 */
export function serializeMCPContent(
  content: readonly MCPContentBlock[],
): readonly SerializedContentBlock[] {
  return content.map(
    (block): SerializedContentBlock => ({
      type: block.type,
      text: block.text ?? null,
      data: block.data ?? null,
      mimeType: block.mimeType ?? null,
      annotations: block.annotations ?? null,
      meta: block.meta ?? null,
    }),
  );
}

/**
 * Mirascope wrapper around an MCP ClientSession.
 *
 * Provides a way to get MCP tools that are pre-converted into Mirascope-friendly
 * types. The underlying MCP ClientSession may be accessed via .session if needed.
 *
 * @example
 * ```typescript
 * // All operations including tool execution must happen within the callback
 * const result = await using(stdioClient(serverParams), async (client) => {
 *   const tools = await client.listTools();
 *   const model = new Model({ model: 'openai/gpt-4', tools });
 *   let response = await model.call([{ role: 'user', content: 'Help me with a task' }]);
 *   // Tool execution loop must be inside the callback
 *   while (response.toolCalls.length > 0) {
 *     const toolOutputs = await response.executeTools();
 *     response = await response.resume(toolOutputs);
 *   }
 *   return response.content;
 * });
 * ```
 */
export class MCPClient {
  private readonly _session: MCPClientSession;

  constructor(session: MCPClientSession) {
    this._session = session;
  }

  /**
   * Access the underlying MCP ClientSession if needed.
   */
  get session(): MCPClientSession {
    return this._session;
  }

  /**
   * List all tools available on the MCP server.
   *
   * @returns A list of dynamically created Mirascope tools.
   */
  async listTools(): Promise<BaseTool[]> {
    const result = await this._session.listTools();
    return result.tools.map((tool) => this.convertMCPToolToBaseTool(tool));
  }

  /**
   * Convert an MCP Tool to a Mirascope BaseTool.
   *
   * @param mcpTool - The MCP tool to convert.
   * @returns A BaseTool that wraps the MCP tool.
   */
  private convertMCPToolToBaseTool(mcpTool: MCPTool): BaseTool {
    const session = this._session;
    const toolName = mcpTool.name;

    // Convert MCP tool's inputSchema to Mirascope's ToolParameterSchema
    const inputSchema = mcpTool.inputSchema;
    const parameters: ToolParameterSchema = {
      type: "object",
      properties: (inputSchema.properties ??
        {}) as ToolParameterSchema["properties"],
      required: (inputSchema.required ?? []) as readonly string[],
      additionalProperties: false,
      ...(inputSchema.$defs && {
        $defs: inputSchema.$defs as ToolParameterSchema["$defs"],
      }),
    };

    // Create the execute function that calls the MCP tool
    const execute = async (
      toolCall: ToolCall,
    ): Promise<ToolOutput<Jsonable>> => {
      try {
        const args = JSON.parse(toolCall.args) as Record<string, unknown>;
        const toolResult = await session.callTool(toolName, args);

        // Convert ContentBlock objects to JSON-serializable format
        // Matches Python's [content.model_dump() for content in tool_result.content]
        const serializedContent = serializeMCPContent(
          toolResult.content,
        ) as unknown as Jsonable;

        return ToolOutput.success(toolCall.id, toolName, serializedContent);
      } catch (error) {
        const err = error instanceof Error ? error : new Error(String(error));
        return ToolOutput.failure(
          toolCall.id,
          toolName,
          new ToolExecutionError(err),
        );
      }
    };

    // Create the BaseTool object
    // Note: MCP tools are always async and don't support direct invocation
    // so we create a minimal tool object that satisfies the interface
    const baseTool: BaseTool = {
      __toolType: TOOL_TYPE,
      name: toolName,
      description: mcpTool.description ?? toolName,
      parameters,
      strict: false,
      execute,
      validator: undefined,
    };

    return baseTool;
  }
}
