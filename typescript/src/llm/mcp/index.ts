/**
 * MCP (Model Context Protocol) support for Mirascope TypeScript SDK.
 *
 * This module provides integration with MCP servers, allowing you to
 * use MCP tools as Mirascope tools.
 *
 * @example
 * ```typescript
 * import { mcp, defineCall } from 'mirascope';
 *
 * // Connect to an MCP server and get tools
 * const tools = await mcp.using(
 *   mcp.stdioClient({
 *     command: 'python',
 *     args: ['-m', 'my_mcp_server'],
 *   }),
 *   async (client) => client.listTools()
 * );
 *
 * // Use the tools with defineCall
 * const call = defineCall({
 *   model: 'openai/gpt-4',
 *   tools: tools,
 *   template: () => 'Help the user with their request',
 * });
 * ```
 *
 * @packageDocumentation
 */

// Client
export { MCPClient, serializeMCPContent } from "./mcp-client";

// Transports
export {
  using,
  stdioClient,
  sseClient,
  streamableHttpClient,
  type MCPResource,
} from "./transports";

// Types
export type {
  MCPTool,
  MCPInputSchema,
  MCPCallToolResult,
  MCPContentBlock,
  MCPClientSession,
  StdioServerParameters,
} from "./types";

// Errors
export {
  MCPError,
  MCPNotInstalledError,
  MCPConnectionError,
  MCPToolError,
} from "./errors";
