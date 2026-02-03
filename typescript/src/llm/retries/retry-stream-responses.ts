/**
 * Retry stream response wrappers that add retry capabilities to streaming LLM responses.
 */

import type { AssistantContentChunk } from "@/llm/content";
import type { ToolOutput } from "@/llm/content/tool-output";
import type { Context } from "@/llm/context";
import type { UserContent } from "@/llm/messages";
import type { Model } from "@/llm/models";
import type { Jsonable } from "@/llm/types/jsonable";

import { RetriesExhausted, StreamRestarted } from "@/llm/exceptions";
import { ContextStreamResponse } from "@/llm/responses/context-stream-response";
import { StreamResponse } from "@/llm/responses/stream-response";

import type { RetryConfig } from "./retry-config";
import type { RetryModel } from "./retry-model";

import { getRetryModelFromContext } from "./retry-model";
import { isRetryableError, type RetryFailure } from "./utils";

/**
 * Create a dummy async iterator for initial construction.
 * The actual iteration will be handled by the wrapped stream.
 */
async function* emptyIterator(): AsyncGenerator<never> {
  // Never yields anything - we override chunkStream to use the wrapped stream
}

/**
 * A streaming response wrapper that includes retry capabilities.
 *
 * This class wraps a `StreamResponse` and adds automatic retry behavior when
 * retryable errors occur during iteration. When a retry happens, a
 * `StreamRestarted` exception is raised so the user can handle the restart
 * (e.g., clear terminal output) before re-iterating.
 *
 * @template F - The type of the formatted output when using structured outputs.
 *
 * @example
 * ```typescript
 * const response = await retryModel.stream("Tell me a story");
 *
 * while (true) {
 *   try {
 *     for await (const text of response.textStream()) {
 *       process.stdout.write(text);
 *     }
 *     break; // Success
 *   } catch (e) {
 *     if (e instanceof llm.StreamRestarted) {
 *       console.log(`\nStream restarted: ${e.message}`);
 *     } else {
 *       throw e;
 *     }
 *   }
 * }
 * ```
 */
export class RetryStreamResponse<F = unknown> extends StreamResponse<F> {
  /**
   * The current RetryModel variant being used.
   */
  private _currentVariant: RetryModel;

  /**
   * Async iterator over model variants with backoff delays.
   */
  private _variantsIter: AsyncGenerator<RetryModel>;

  /**
   * Failed attempts before success (empty if first attempt succeeded).
   */
  readonly retryFailures: RetryFailure[] = [];

  /**
   * Function that creates a stream from a Model.
   */
  private readonly _streamFn: (model: Model) => Promise<StreamResponse<F>>;

  /**
   * The current underlying stream response.
   */
  private _currentStream: StreamResponse<F>;

  /**
   * Initialize a RetryStreamResponse.
   *
   * @param streamFn - Async function that creates a stream from a Model.
   * @param initialStream - The pre-awaited initial stream.
   * @param initialVariant - The first variant from the iterator.
   * @param variantsIter - The async iterator for remaining variants.
   */
  constructor(
    streamFn: (model: Model) => Promise<StreamResponse<F>>,
    initialStream: StreamResponse<F>,
    initialVariant: RetryModel,
    variantsIter: AsyncGenerator<RetryModel>,
  ) {
    // Initialize with the initial stream's properties
    super({
      providerId: initialStream.providerId,
      modelId: initialStream.modelId,
      providerModelName: initialStream.providerModelName,
      params: initialStream.params,
      tools: initialStream.toolkit,
      format: initialStream.format,
      inputMessages: initialStream.inputMessages,
      chunkIterator: emptyIterator(),
    });

    this._currentVariant = initialVariant;
    this._variantsIter = variantsIter;
    this._streamFn = streamFn;
    this._currentStream = initialStream;
  }

  /**
   * A RetryModel with parameters matching this response.
   *
   * If a model is set in context (via `withModel()`), that model is used
   * instead, wrapped with this response's retry config.
   */
  override get model(): Promise<RetryModel> {
    return Promise.resolve(getRetryModelFromContext(this._currentVariant));
  }

  /**
   * The retry configuration for this response.
   */
  get retryConfig(): RetryConfig {
    return this._currentVariant.retryConfig;
  }

  /**
   * Reset to a fresh stream for a new retry attempt.
   */
  private async _resetStream(variant: RetryModel): Promise<void> {
    this._currentStream = await this._streamFn(variant.getActiveModel());
  }

  /**
   * Stream content chunks with retry support.
   *
   * If a retryable error occurs during iteration, the stream is reset
   * and a `StreamRestarted` exception is raised. The user should catch
   * this exception and re-iterate to continue from the new attempt.
   *
   * @throws StreamRestarted - When the stream is reset for a retry attempt.
   * @throws RetriesExhausted - If all retry attempts fail.
   */
  override async *chunkStream(): AsyncGenerator<AssistantContentChunk> {
    try {
      for await (const chunk of this._currentStream.chunkStream()) {
        yield chunk;
      }
    } catch (error) {
      /* v8 ignore next 2 -- defensive: errors are always Error instances */
      if (!(error instanceof Error)) throw error;
      if (!isRetryableError(error, this.retryConfig)) throw error;

      const failure: RetryFailure = {
        model: this._currentVariant.getActiveModel(),
        exception: error,
      };
      this.retryFailures.push(failure);

      // Try to get next variant (handles backoff and fallback)
      const next = await this._variantsIter.next();
      if (next.done) {
        throw new RetriesExhausted(this.retryFailures);
      }

      this._currentVariant = next.value;
      await this._resetStream(this._currentVariant);

      throw new StreamRestarted(failure);
    }
  }

  /**
   * Generate a new RetryStreamResponse using this response's messages with additional user content.
   *
   * @param content - The new user message content to append to the message history.
   * @returns A new RetryStreamResponse for streaming the extended conversation.
   */
  override async resume(content: UserContent): Promise<RetryStreamResponse<F>> {
    const model = await this.model;
    return model.resumeStream(this, content) as Promise<RetryStreamResponse<F>>;
  }

  /**
   * Execute all tool calls in this response using the registered tools.
   *
   * Note: The stream must be consumed before calling executeTools() to ensure
   * all tool calls have been received.
   *
   * @returns An array of ToolOutput objects, one for each tool call.
   */
  override async executeTools(): Promise<ToolOutput<Jsonable>[]> {
    return Promise.all(
      this.toolCalls.map((call) => this.toolkit.execute(call)),
    );
  }
}

/**
 * A context-aware streaming response wrapper that includes retry capabilities.
 *
 * This class wraps a `ContextStreamResponse` and adds automatic retry behavior when
 * retryable errors occur during iteration.
 *
 * @template DepsT - The type of dependencies in the context.
 * @template F - The type of the formatted output when using structured outputs.
 */
export class ContextRetryStreamResponse<
  DepsT = unknown,
  F = unknown,
> extends ContextStreamResponse<DepsT, F> {
  /**
   * The current RetryModel variant being used.
   */
  private _currentVariant: RetryModel;

  /**
   * Async iterator over model variants with backoff delays.
   */
  private _variantsIter: AsyncGenerator<RetryModel>;

  /**
   * Failed attempts before success (empty if first attempt succeeded).
   */
  readonly retryFailures: RetryFailure[] = [];

  /**
   * Function that creates a stream from a Model.
   */
  private readonly _streamFn: (
    model: Model,
  ) => Promise<ContextStreamResponse<DepsT, F>>;

  /**
   * The current underlying stream response.
   */
  private _currentStream: ContextStreamResponse<DepsT, F>;

  /**
   * Initialize a ContextRetryStreamResponse.
   *
   * @param streamFn - Async function that creates a stream from a Model.
   * @param initialStream - The pre-awaited initial stream.
   * @param initialVariant - The first variant from the iterator.
   * @param variantsIter - The async iterator for remaining variants.
   */
  constructor(
    streamFn: (model: Model) => Promise<ContextStreamResponse<DepsT, F>>,
    initialStream: ContextStreamResponse<DepsT, F>,
    initialVariant: RetryModel,
    variantsIter: AsyncGenerator<RetryModel>,
  ) {
    // Initialize with the initial stream's properties
    super({
      providerId: initialStream.providerId,
      modelId: initialStream.modelId,
      providerModelName: initialStream.providerModelName,
      params: initialStream.params,
      tools: initialStream.contextToolkit,
      format: initialStream.format,
      inputMessages: initialStream.inputMessages,
      chunkIterator: emptyIterator(),
    });

    this._currentVariant = initialVariant;
    this._variantsIter = variantsIter;
    this._streamFn = streamFn;
    this._currentStream = initialStream;
  }

  /**
   * A RetryModel with parameters matching this response.
   */
  override get model(): Promise<RetryModel> {
    return Promise.resolve(getRetryModelFromContext(this._currentVariant));
  }

  /**
   * The retry configuration for this response.
   */
  get retryConfig(): RetryConfig {
    return this._currentVariant.retryConfig;
  }

  /**
   * Reset to a fresh stream for a new retry attempt.
   */
  private async _resetStream(variant: RetryModel): Promise<void> {
    this._currentStream = await this._streamFn(variant.getActiveModel());
  }

  /**
   * Stream content chunks with retry support.
   */
  override async *chunkStream(): AsyncGenerator<AssistantContentChunk> {
    try {
      for await (const chunk of this._currentStream.chunkStream()) {
        yield chunk;
      }
    } catch (error) {
      /* v8 ignore next 2 -- defensive: errors are always Error instances */
      if (!(error instanceof Error)) throw error;
      if (!isRetryableError(error, this.retryConfig)) throw error;

      const failure: RetryFailure = {
        model: this._currentVariant.getActiveModel(),
        exception: error,
      };
      this.retryFailures.push(failure);

      // Try to get next variant (handles backoff and fallback)
      const next = await this._variantsIter.next();
      if (next.done) {
        throw new RetriesExhausted(this.retryFailures);
      }

      this._currentVariant = next.value;
      await this._resetStream(this._currentVariant);

      throw new StreamRestarted(failure);
    }
  }

  /**
   * Generate a new ContextRetryStreamResponse using this response's messages with additional user content.
   *
   * @param ctx - A Context with the required deps type.
   * @param content - The new user message content to append to the message history.
   * @returns A new ContextRetryStreamResponse for streaming the extended conversation.
   */
  override async resume(
    ctx: Context<DepsT>,
    content: UserContent,
  ): Promise<ContextRetryStreamResponse<DepsT, F>> {
    const model = await this.model;
    return model.contextResumeStream(ctx, this, content) as Promise<
      ContextRetryStreamResponse<DepsT, F>
    >;
  }

  /**
   * Execute all tool calls in this response using the registered context tools.
   *
   * @param ctx - The context containing dependencies to pass to tools.
   * @returns An array of ToolOutput objects, one for each tool call.
   */
  override async executeTools(
    ctx: Context<DepsT>,
  ): Promise<ToolOutput<Jsonable>[]> {
    return this.contextToolkit.executeAll(ctx, this.toolCalls);
  }
}
