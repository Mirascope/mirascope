/**
 * StreamResponse class for handling streaming LLM responses.
 *
 * Extends BaseStreamResponse with resume methods for continuing conversations.
 */

import type { ToolOutput } from '@/llm/content/tool-output';
import type { Jsonable } from '@/llm/types/jsonable';
import type { UserContent } from '@/llm/messages';
import {
  BaseStreamResponse,
  type BaseStreamResponseInit,
} from '@/llm/responses/base-stream-response';
import { Toolkit, type Tools } from '@/llm/tools';

/**
 * Arguments for constructing a StreamResponse.
 *
 * Accepts `tools` as either a Toolkit or a list of tools, which gets
 * converted to a Toolkit before passing to BaseStreamResponse.
 */
export interface StreamResponseInit
  extends Omit<BaseStreamResponseInit, 'toolkit'> {
  /**
   * The tools available for this response.
   * Can be a Toolkit instance or an array of tools.
   */
  tools?: Tools | Toolkit;
}

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
  /**
   * Override base toolkit with correct type for execute() support.
   */
  declare readonly toolkit: Toolkit;

  constructor(args: StreamResponseInit) {
    // Convert tools to toolkit (matching Python's pattern)
    const toolkit =
      args.tools instanceof Toolkit
        ? args.tools
        : new Toolkit(args.tools ?? []);

    super({ ...args, toolkit });
  }

  // ===== Tool Execution =====

  /**
   * Execute all tool calls in this response using the registered tools.
   *
   * Note: The stream must be consumed before calling executeTools() to ensure
   * all tool calls have been received.
   *
   * @returns An array of ToolOutput objects, one for each tool call.
   *
   * @example
   * ```typescript
   * const response = await model.stream('What is the weather?', [weatherTool]);
   *
   * // Consume the stream first
   * for await (const text of response.textStream()) {
   *   process.stdout.write(text);
   * }
   *
   * // Then execute tools
   * if (response.toolCalls.length > 0) {
   *   const outputs = await response.executeTools();
   *   const followUp = await response.resume(outputs);
   * }
   * ```
   */
  async executeTools(): Promise<ToolOutput<Jsonable>[]> {
    return Promise.all(
      this.toolCalls.map((call) => this.toolkit.execute(call))
    );
  }

  // ===== Resume Methods =====

  /**
   * Generate a new StreamResponse using this response's messages with additional user content.
   *
   * Uses this response's tools and format type. Also uses this response's provider,
   * model, and params.
   *
   * Note: The stream must be consumed before calling resume() to ensure
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
   * const followUp = await response.resume('Tell me more about that');
   * for await (const text of followUp.textStream()) {
   *   process.stdout.write(text);
   * }
   * ```
   */
  async resume(content: UserContent): Promise<StreamResponse> {
    const model = await this.model;
    return model.resumeStream(this, content);
  }
}
