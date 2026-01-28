/**
 * ContextStreamResponse class for context-based streaming LLM calls.
 *
 * Extends StreamResponse with context-aware functionality including:
 * - executeTools(): Execute tool calls with context dependency injection
 */

import type { Context } from '@/llm/context';
import {
  StreamResponse,
  type StreamResponseInit,
} from '@/llm/responses/stream-response';

/**
 * Arguments for constructing a ContextStreamResponse.
 */
export type ContextStreamResponseInit = StreamResponseInit;

/**
 * A streaming response from a context-based LLM call.
 *
 * This class provides context-aware functionality on top of the standard streaming response:
 * - `executeTools()`: Execute all tool calls with context dependency injection
 *
 * @template DepsT - The type of dependencies in the context.
 *
 * @example
 * ```typescript
 * interface MyDeps { userId: string; }
 *
 * const ctx = createContext<MyDeps>({ userId: '123' });
 * const response = await myPrompt.stream(model, ctx);
 *
 * for await (const text of response.textStream()) {
 *   process.stdout.write(text);
 * }
 * ```
 */
export class ContextStreamResponse<DepsT = unknown> extends StreamResponse {
  constructor(args: ContextStreamResponseInit) {
    super(args);
  }

  /* v8 ignore start - tools not yet implemented */
  /**
   * Execute and return all of the tool calls in the response.
   *
   * Note: The stream must be consumed before tool calls are available.
   *
   * @param _ctx - A Context with the required deps type.
   * @returns A sequence containing a ToolOutput for every tool call.
   *
   * @throws ToolNotFoundError if one of the response's tool calls has no matching tool.
   * @throws Error if one of the tools throws an exception.
   *
   * @example
   * ```typescript
   * const response = await myPrompt.stream(model, ctx);
   * await response.consume(); // Must consume stream first
   * const outputs = response.executeTools(ctx);
   * for (const output of outputs) {
   *   console.log(output);
   * }
   * ```
   */
  executeTools(_ctx: Context<DepsT>): unknown[] {
    // Note: Tool execution is not yet implemented.
    // When implemented, this will:
    // 1. Iterate through this.toolCalls
    // 2. For each tool call, find the matching tool in the toolkit
    // 3. Execute the tool with the context and tool call arguments
    // 4. Return an array of ToolOutput objects
    return [];
  }
  /* v8 ignore stop */
}
