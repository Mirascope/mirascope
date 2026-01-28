/**
 * ContextStreamResponse class for context-based streaming LLM calls.
 *
 * Extends BaseStreamResponse with context-aware functionality including:
 * - executeTools(): Execute tool calls with context dependency injection
 * - resume(): Continue the conversation with additional user content
 */

import type { Context } from '@/llm/context';
import type { UserContent } from '@/llm/messages';
import type { ContextResponse } from '@/llm/responses/context-response';
import {
  BaseStreamResponse,
  type BaseStreamResponseInit,
} from '@/llm/responses/base-stream-response';

/**
 * Arguments for constructing a ContextStreamResponse.
 */
export type ContextStreamResponseInit = BaseStreamResponseInit;

/**
 * A streaming response from a context-based LLM call.
 *
 * This class provides context-aware functionality on top of the standard streaming response:
 * - `executeTools()`: Execute all tool calls with context dependency injection
 * - `resume()`: Continue the conversation with additional user content
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
 *
 * // Continue the conversation
 * const followUp = await response.resume(ctx, 'Tell me more');
 * ```
 */
export class ContextStreamResponse<DepsT = unknown> extends BaseStreamResponse {
  constructor(args: ContextStreamResponseInit) {
    super(args);
  }

  /**
   * Generate a new ContextResponse using this response's messages with additional user content.
   *
   * Uses this response's tools and format type. Also uses this response's provider,
   * model, and params.
   *
   * Note: The stream must be consumed before calling resume() to ensure
   * the assistant message is complete.
   *
   * @param ctx - A Context with the required deps type.
   * @param content - The new user message content to append to the message history.
   * @returns A new ContextResponse instance generated from the extended message history.
   *
   * @example
   * ```typescript
   * const response = await myPrompt.stream(model, ctx);
   *
   * // Consume the stream first
   * for await (const text of response.textStream()) {
   *   process.stdout.write(text);
   * }
   *
   * // Then resume with a non-streaming response
   * const followUp = await response.resume(ctx, 'Tell me more about that');
   * console.log(followUp.text());
   * ```
   */
  async resume(
    ctx: Context<DepsT>,
    content: UserContent
  ): Promise<ContextResponse<DepsT>> {
    const model = await this.model;
    return model.contextResume(ctx, this, content);
  }

  /**
   * Generate a new ContextStreamResponse using this response's messages with additional user content.
   *
   * Uses this response's tools and format type. Also uses this response's provider,
   * model, and params. Returns a streaming response for incremental consumption.
   *
   * Note: The current stream must be consumed before calling resumeStream() to ensure
   * the assistant message is complete.
   *
   * @param ctx - A Context with the required deps type.
   * @param content - The new user message content to append to the message history.
   * @returns A new ContextStreamResponse instance generated from the extended message history.
   *
   * @example
   * ```typescript
   * const response = await myPrompt.stream(model, ctx);
   *
   * // Consume the stream first
   * for await (const text of response.textStream()) {
   *   process.stdout.write(text);
   * }
   *
   * // Then resume with streaming
   * const followUp = await response.resumeStream(ctx, 'Tell me more about that');
   * for await (const text of followUp.textStream()) {
   *   process.stdout.write(text);
   * }
   * ```
   */
  async resumeStream(
    ctx: Context<DepsT>,
    content: UserContent
  ): Promise<ContextStreamResponse<DepsT>> {
    const model = await this.model;
    return model.contextResumeStream(ctx, this, content);
  }

  // Note: execute_tools() method is not implemented yet as it requires Tools infrastructure.
}
