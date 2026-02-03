/**
 * MCP-specific error classes.
 */

import { MirascopeError } from "@/llm/exceptions";

/**
 * Base error for MCP-related failures.
 */
export class MCPError extends MirascopeError {
  constructor(message: string) {
    super(message);
  }
}

/**
 * Raised when the MCP SDK is not installed.
 */
export class MCPNotInstalledError extends MCPError {
  constructor() {
    super(
      "The @modelcontextprotocol/sdk package is required for MCP support. " +
        "Install it with: npm install @modelcontextprotocol/sdk",
    );
  }
}

/**
 * Raised when MCP connection fails.
 */
export class MCPConnectionError extends MCPError {
  readonly originalError?: Error;

  constructor(message: string, originalError?: Error) {
    super(message);
    this.originalError = originalError;
    if (originalError) {
      this.cause = originalError;
    }
  }
}

/**
 * Raised when MCP tool execution fails.
 */
export class MCPToolError extends MCPError {
  readonly toolName: string;
  readonly originalError?: Error;

  constructor(toolName: string, message: string, originalError?: Error) {
    super(`MCP tool '${toolName}' failed: ${message}`);
    this.toolName = toolName;
    this.originalError = originalError;
    if (originalError) {
      this.cause = originalError;
    }
  }
}
