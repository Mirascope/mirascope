/**
 * StreamResponse class for handling streaming LLM responses.
 *
 * Extends BaseStreamResponse with resume methods for continuing conversations.
 */

import type { UserContent } from '@/llm/messages';
import {
  BaseStreamResponse,
  type BaseStreamResponseInit,
} from '@/llm/responses/base-stream-response';
import type { Response } from '@/llm/responses/response';

/**
 * Arguments for constructing a StreamResponse.
 */
export type StreamResponseInit = BaseStreamResponseInit;

/**
 * Streaming response that consumes chunks from an async iterator.
 *
 * Extends BaseStreamResponse to provide the standard streaming interface,
 * adding resume methods for continuing conversations.
 *
 * @example
 * ```typescript
 * const response = await model.stream('Hello!');
 *
 * for await (const text of response.textStream()) {
 *   process.stdout.write(text);
 * }
 *
 * // Continue the conversation
 * const followUp = await response.resume('Tell me more');
 * ```
 */
export class StreamResponse extends BaseStreamResponse {
  constructor(args: StreamResponseInit) {
    super(args);
  }

  // ===== Resume Methods =====

  /**
   * Generate a new Response using this response's messages with additional user content.
   *
   * Uses this response's tools and format type. Also uses this response's provider,
   * model, and params.
   *
   * Note: The stream must be consumed before calling resume() to ensure
   * the assistant message is complete.
   *
   * @param content - The new user message content to append to the message history.
   * @returns A new Response instance generated from the extended message history.
   *
   * @example
   * ```typescript
   * const response = await model.stream('Hello!');
   *
   * // Consume the stream first
   * for await (const text of response.textStream()) {
   *   process.stdout.write(text);
   * }
   *
   * // Then resume with a non-streaming response
   * const followUp = await response.resume('Tell me more about that');
   * console.log(followUp.text());
   * ```
   */
  async resume(content: UserContent): Promise<Response> {
    const model = await this.model;
    return model.resume(this, content);
  }

  /**
   * Generate a new StreamResponse using this response's messages with additional user content.
   *
   * Uses this response's tools and format type. Also uses this response's provider,
   * model, and params. Returns a streaming response for incremental consumption.
   *
   * Note: The current stream must be consumed before calling resumeStream() to ensure
   * the assistant message is complete.
   *
   * @param content - The new user message content to append to the message history.
   * @returns A new StreamResponse instance generated from the extended message history.
   *
   * @example
   * ```typescript
   * const response = await model.stream('Hello!');
   *
   * // Consume the stream first
   * for await (const text of response.textStream()) {
   *   process.stdout.write(text);
   * }
   *
   * // Then resume with streaming
   * const followUp = await response.resumeStream('Tell me more about that');
   * for await (const text of followUp.textStream()) {
   *   process.stdout.write(text);
   * }
   * ```
   */
  async resumeStream(content: UserContent): Promise<StreamResponse> {
    const model = await this.model;
    return model.resumeStream(this, content);
  }

  // Note: execute_tools() method is not implemented yet as it requires Tools infrastructure.
}
