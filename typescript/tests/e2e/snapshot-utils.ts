/**
 * Snapshot utility functions for E2E test snapshots.
 *
 * These functions convert response objects to dictionaries suitable for
 * snapshot testing, matching Python's snapshot utilities pattern.
 */

import type { Format } from "@/llm/formatting";
import type {
  Response,
  StreamResponse,
  ContextResponse,
  ContextStreamResponse,
  Usage,
} from "@/llm/responses";
import type { ToolSchema } from "@/llm/tools/tool-schema";

import { isProviderTool, type ProviderTool } from "@/llm/tools/provider-tool";

/**
 * Format snapshot for a Format object.
 */
export function formatSnapshot(
  format: Format | null,
): Record<string, unknown> | null {
  if (format === null) {
    return null;
  }

  return {
    name: format.name,
    description: format.description,
    schema: format.schema,
    mode: format.mode,
    formattingInstructions: format.formattingInstructions,
  };
}

/**
 * Tool snapshot for a tool schema or provider tool.
 */
export function toolSnapshot(
  tool: ToolSchema | ProviderTool,
): Record<string, unknown> {
  if (isProviderTool(tool)) {
    return { name: tool.name };
  }

  const schema = tool as ToolSchema;
  return {
    name: schema.name,
    description: schema.description,
    parameters: JSON.stringify(schema.parameters, null, 2),
    strict: schema.strict,
  };
}

/**
 * Usage snapshot for usage statistics.
 */
export function usageSnapshot(
  usage: Usage | null,
): Record<string, unknown> | null {
  if (!usage) {
    return null;
  }

  return {
    inputTokens: usage.inputTokens,
    outputTokens: usage.outputTokens,
    cacheReadTokens: usage.cacheReadTokens,
    cacheWriteTokens: usage.cacheWriteTokens,
    reasoningTokens: usage.reasoningTokens,
    totalTokens: usage.inputTokens + usage.outputTokens,
    raw: String(usage.raw),
  };
}

/**
 * Response snapshot dict for non-streaming responses.
 *
 * Excludes raw response and derived properties (content, texts, thoughts,
 * toolCalls) since they're redundant with the final assistant message.
 */
export function responseSnapshotDict(
  response: Response | ContextResponse,
): Record<string, unknown> {
  return {
    providerId: response.providerId,
    modelId: response.modelId,
    providerModelName: response.providerModelName,
    finishReason: response.finishReason,
    messages: response.messages,
    format: formatSnapshot(response.format),
    tools: response.toolkit.tools.map(toolSnapshot),
    usage: usageSnapshot(response.usage),
  };
}

/**
 * Stream response snapshot dict.
 *
 * Only snapshots the number of chunks (not full chunks) to minimize bloat.
 */
export function streamResponseSnapshotDict(
  response: StreamResponse | ContextStreamResponse,
): Record<string, unknown> {
  return {
    providerId: response.providerId,
    modelId: response.modelId,
    providerModelName: response.providerModelName,
    finishReason: response.finishReason,
    messages: [...response.messages],
    format: formatSnapshot(response.format),
    tools: response.toolkit.tools.map(toolSnapshot),
    usage: usageSnapshot(response.usage),
    nChunks: response.chunks.length,
  };
}

/**
 * Exception snapshot dict for error cases.
 *
 * Converts an exception to a dictionary for snapshot testing.
 * Re-throws connection errors and cassette errors that indicate test setup issues.
 */
export function exceptionSnapshotDict(
  exception: Error,
): Record<string, unknown> {
  // Check for connection errors or cassette errors that should be re-thrown
  if (exception.message) {
    if (
      exception.message.includes("Connection error") ||
      exception.message.includes("Can't overwrite existing cassette")
    ) {
      throw exception;
    }
  }

  // Build snapshot from non-private, non-function properties
  const result: Record<string, unknown> = {
    type: exception.constructor.name,
  };

  // Add all non-private properties
  for (const key of Object.keys(exception)) {
    if (!key.startsWith("_")) {
      const value = (exception as unknown as Record<string, unknown>)[key];
      if (typeof value !== "function") {
        result[key] = String(value);
      }
    }
  }

  // Also include common Error properties
  if (exception.message) {
    result.message = exception.message;
  }
  if (exception.name) {
    result.name = exception.name;
  }

  return result;
}

/**
 * Type for any response type (streaming or non-streaming).
 */
export type AnyResponse =
  | Response
  | StreamResponse
  | ContextResponse
  | ContextStreamResponse;

/**
 * Check if a response is a streaming response.
 */
export function isStreamResponse(
  response: AnyResponse,
): response is StreamResponse | ContextStreamResponse {
  // StreamResponse and ContextStreamResponse have a 'chunks' property and 'consumed' property
  return "chunks" in response && "consumed" in response;
}

/**
 * SnapshotDict class with convenience method for setting response.
 */
export class SnapshotDict {
  private data: Record<string, unknown> = {};

  /**
   * Set the response snapshot, auto-detecting streaming vs non-streaming.
   */
  setResponse(response: AnyResponse): void {
    if (isStreamResponse(response)) {
      this.data.response = streamResponseSnapshotDict(response);
    } else {
      this.data.response = responseSnapshotDict(response);
    }
  }

  /**
   * Set the exception snapshot.
   */
  setException(exception: Error): void {
    this.data.exception = exceptionSnapshotDict(exception);
  }

  /**
   * Set logs captured during the test.
   */
  setLogs(logs: string[]): void {
    if (logs.length > 0) {
      this.data.logs = logs;
    }
  }

  /**
   * Get a value from the snapshot.
   */
  get(key: string): unknown {
    return this.data[key];
  }

  /**
   * Set a value in the snapshot.
   */
  set(key: string, value: unknown): void {
    this.data[key] = value;
  }

  /**
   * Convert to plain object for comparison.
   */
  toObject(): Record<string, unknown> {
    return { ...this.data };
  }
}
