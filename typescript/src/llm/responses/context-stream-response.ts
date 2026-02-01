/**
 * ContextStreamResponse class for context-based streaming LLM calls.
 *
 * Extends BaseStreamResponse with context-aware functionality including:
 * - executeTools(): Execute tool calls with context dependency injection
 * - resume(): Continue the conversation with additional user content
 */

import type { ToolOutput } from "@/llm/content/tool-output";
import type { Context } from "@/llm/context";
import type { UserContent } from "@/llm/messages";
import type { Jsonable } from "@/llm/types/jsonable";

import {
  BaseStreamResponse,
  type BaseStreamResponseInit,
} from "@/llm/responses/base-stream-response";
import { ContextToolkit, type ContextTools } from "@/llm/tools";

/**
 * Arguments for constructing a ContextStreamResponse.
 *
 * Accepts `tools` as either a ContextToolkit or a list of tools, which gets
 * converted to a ContextToolkit before passing to BaseStreamResponse.
 *
 * Supports both regular tools (BaseTool) and context tools (BaseContextTool),
 * matching Python's `ContextTools[DepsT]` pattern.
 *
 * @template DepsT - The type of dependencies in the context.
 */
export interface ContextStreamResponseInit<DepsT = unknown> extends Omit<
  BaseStreamResponseInit,
  "toolkit"
> {
  /**
   * The tools available for this response.
   * Can be a ContextToolkit instance or an array of tools.
   * Accepts both regular tools and context tools.
   */
  tools?: ContextTools<DepsT> | ContextToolkit<DepsT>;
}

/**
 * A streaming response from a context-based LLM call.
 *
 * This class provides context-aware functionality on top of the standard streaming response:
 * - `executeTools()`: Execute all tool calls with context dependency injection
 * - `resume()`: Continue the conversation with additional user content
 *
 * @template DepsT - The type of dependencies in the context.
 * @template F - The type of the formatted output when using structured outputs.
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
export class ContextStreamResponse<
  DepsT = unknown,
  F = unknown,
> extends BaseStreamResponse<F> {
  /**
   * The context toolkit containing tools that can receive context.
   */
  readonly contextToolkit: ContextToolkit<DepsT>;

  constructor(args: ContextStreamResponseInit<DepsT>) {
    // Convert tools to context toolkit (matching Python's pattern)
    const contextToolkit =
      args.tools instanceof ContextToolkit
        ? args.tools
        : new ContextToolkit(args.tools ?? []);

    super({ ...args, toolkit: contextToolkit });

    this.contextToolkit = contextToolkit;
  }

  // ===== Tool Execution =====

  /**
   * Execute all tool calls in this response using the registered context tools.
   *
   * Note: The stream must be consumed before calling executeTools() to ensure
   * all tool calls have been received.
   *
   * @param ctx - The context containing dependencies to pass to tools.
   * @returns An array of ToolOutput objects, one for each tool call.
   *
   * @example
   * ```typescript
   * const response = await myPrompt.stream(model, ctx, [searchTool]);
   *
   * // Consume the stream first
   * for await (const text of response.textStream()) {
   *   process.stdout.write(text);
   * }
   *
   * // Then execute tools
   * if (response.toolCalls.length > 0) {
   *   const outputs = await response.executeTools(ctx);
   *   const followUp = await response.resume(ctx, outputs);
   * }
   * ```
   */
  async executeTools(ctx: Context<DepsT>): Promise<ToolOutput<Jsonable>[]> {
    return this.contextToolkit.executeAll(ctx, this.toolCalls);
  }

  // ===== Resume Methods =====

  /**
   * Generate a new ContextStreamResponse using this response's messages with additional user content.
   *
   * Uses this response's tools and format type. Also uses this response's provider,
   * model, and params.
   *
   * Note: The stream must be consumed before calling resume() to ensure
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
   * const followUp = await response.resume(ctx, 'Tell me more about that');
   * for await (const text of followUp.textStream()) {
   *   process.stdout.write(text);
   * }
   * ```
   */
  async resume(
    ctx: Context<DepsT>,
    content: UserContent,
  ): Promise<ContextStreamResponse<DepsT, F>> {
    const model = await this.model;
    return model.contextResumeStream(ctx, this, content) as Promise<
      ContextStreamResponse<DepsT, F>
    >;
  }
}
