/**
 * MCP SDK type definitions for optional dependency support.
 *
 * These types mirror the @modelcontextprotocol/sdk types to allow
 * type-safe usage without requiring the SDK as a direct dependency.
 */

/**
 * MCP Tool definition from the SDK.
 */
export interface MCPTool {
  readonly name: string;
  readonly description?: string;
  readonly inputSchema: MCPInputSchema;
}

/**
 * MCP input schema - JSON Schema format.
 */
export interface MCPInputSchema {
  readonly type?: string;
  readonly properties?: Record<string, unknown>;
  readonly required?: readonly string[];
  readonly additionalProperties?: boolean;
  readonly $defs?: Record<string, unknown>;
}

/**
 * MCP CallToolResult from the SDK.
 */
export interface MCPCallToolResult {
  readonly content: readonly MCPContentBlock[];
  readonly isError?: boolean;
}

/**
 * MCP content block types.
 */
export interface MCPContentBlock {
  readonly type: string;
  readonly text?: string;
  readonly data?: string;
  readonly mimeType?: string;
  readonly annotations?: unknown;
  readonly meta?: unknown;
}

/**
 * MCP ClientSession interface (duck-typed for the SDK).
 */
export interface MCPClientSession {
  initialize(): Promise<unknown>;
  listTools(): Promise<{ tools: readonly MCPTool[] }>;
  callTool(
    name: string,
    args: Record<string, unknown>,
  ): Promise<MCPCallToolResult>;
  close?(): Promise<void>;
}

/**
 * Stdio server parameters matching MCP SDK's StdioServerParameters.
 */
export interface StdioServerParameters {
  readonly command: string;
  readonly args?: readonly string[];
  readonly env?: Record<string, string> | null;
  readonly cwd?: string;
}
