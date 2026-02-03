/**
 * RetryModel extends Model to add retry logic.
 */

import type { Context } from "@/llm/context";
import type { Format } from "@/llm/formatting";
import type { Message, UserContent } from "@/llm/messages";
import type { Params } from "@/llm/models/params";
import type { ModelId } from "@/llm/providers";
import type { RootResponse } from "@/llm/responses/root-response";
import type { ContextTools, Tools } from "@/llm/tools";

import { RetriesExhausted } from "@/llm/exceptions";
import { Model } from "@/llm/models";
import { modelFromContext } from "@/llm/models/model-context";

import { RetryConfig, type RetryArgs } from "./retry-config";
import { RetryResponse, ContextRetryResponse } from "./retry-responses";
import {
  RetryStreamResponse,
  ContextRetryStreamResponse,
} from "./retry-stream-responses";
import {
  calculateDelay,
  isRetryableError,
  sleep,
  type RetryFailure,
} from "./utils";

/**
 * Keys that belong to RetryArgs (for separating from Params).
 */
const RETRY_ARG_KEYS = new Set<string>([
  "maxRetries",
  "retryOn",
  "initialDelay",
  "maxDelay",
  "backoffMultiplier",
  "jitter",
  "fallbackModels",
]);

/**
 * Combined parameters for RetryModel: model params + retry config.
 */
export type RetryModelParams = Params & RetryArgs;

/**
 * Extends Model with retry logic and optional fallback models.
 *
 * RetryModel "is-a" Model - it has a primary modelId and params determined by
 * the active model. It also supports fallback models that will be tried if the
 * active model exhausts its retries.
 *
 * The `models` array contains all available models (primary + resolved fallbacks).
 * The `activeIndex` indicates which model is currently "primary". When a call
 * succeeds on a fallback model, the returned response's `.model` property will
 * be a new RetryModel with that successful model as the active model.
 *
 * @example
 * ```typescript
 * const model = new RetryModel("openai/gpt-4o", new RetryConfig({
 *   maxRetries: 3,
 *   fallbackModels: ["anthropic/claude-sonnet-4-20250514"],
 * }));
 *
 * const response = await model.call("Hello!");
 * console.log(response.retryFailures); // [] if first attempt succeeded
 * ```
 */
export class RetryModel extends Model {
  /**
   * All available models: primary at index 0, then fallbacks.
   */
  private readonly models: Model[];

  /**
   * Index into models for the currently active model.
   */
  private readonly activeIndex: number;

  /**
   * The RetryConfig specifying retry behavior.
   */
  readonly retryConfig: RetryConfig;

  /**
   * Initialize a RetryModel.
   *
   * @param model - Either a Model instance to wrap, or a ModelId string to create
   *   a new Model from.
   * @param retryConfig - Configuration for retry behavior.
   * @param params - Additional parameters for the model. Only used when `model`
   *   is a ModelId string; ignored when wrapping an existing Model.
   */
  constructor(
    model: Model | ModelId,
    retryConfig: RetryConfig,
    params: Params = {},
  ) {
    // Resolve the primary model (strip to plain Model if needed)
    let primary: Model;
    if (model instanceof Model) {
      primary = RetryModel.stripRetryModel(model);
    } else {
      primary = new Model(model, params);
    }

    // Initialize with primary model's properties
    super(primary.modelId, primary.params);

    // Resolve fallback models
    const resolvedFallbacks: Model[] = [];
    for (const fb of retryConfig.fallbackModels) {
      if (fb instanceof Model) {
        // Strip any RetryModel wrapping, just take modelId and params
        resolvedFallbacks.push(RetryModel.stripRetryModel(fb));
      } else {
        // ModelId string - inherit params from primary
        resolvedFallbacks.push(new Model(fb, primary.params));
      }
    }

    this.models = [primary, ...resolvedFallbacks];
    this.activeIndex = 0;
    this.retryConfig = retryConfig;
  }

  /**
   * Internal constructor for creating a RetryModel with pre-resolved models.
   */
  private static createWithActive(
    models: Model[],
    activeIndex: number,
    retryConfig: RetryConfig,
  ): RetryModel {
    // Create a new RetryModel without going through the normal constructor
    const active = models[activeIndex];
    /* v8 ignore next 3 -- defensive: activeIndex is always valid */
    if (active === undefined) {
      throw new Error(`Invalid activeIndex: ${activeIndex}`);
    }
    const instance = Object.create(RetryModel.prototype) as RetryModel;

    // Set Model base properties
    Object.defineProperty(instance, "modelId", {
      value: active.modelId,
      writable: false,
      enumerable: true,
    });
    Object.defineProperty(instance, "params", {
      value: active.params,
      writable: false,
      enumerable: true,
    });

    // Set RetryModel-specific properties
    Object.defineProperty(instance, "models", {
      value: models,
      writable: false,
      enumerable: false,
    });
    Object.defineProperty(instance, "activeIndex", {
      value: activeIndex,
      writable: false,
      enumerable: false,
    });
    Object.defineProperty(instance, "retryConfig", {
      value: retryConfig,
      writable: false,
      enumerable: true,
    });

    return instance;
  }

  /**
   * Strip a Model of any RetryModel wrapping by creating a plain Model.
   *
   * If the model is a RetryModel (or any subclass), creates a new plain Model
   * with just the modelId and params. This avoids circular dependencies and
   * ensures we always get a plain Model instance.
   */
  private static stripRetryModel(model: Model): Model {
    // Use constructor check to see if it's anything other than a plain Model
    if (model.constructor !== Model) {
      return new Model(model.modelId, model.params);
    }
    return model;
  }

  /**
   * Get the currently active model.
   */
  getActiveModel(): Model {
    const model = this.models[this.activeIndex];
    /* v8 ignore next 3 -- defensive: activeIndex is always valid */
    if (model === undefined) {
      throw new Error(`Invalid activeIndex: ${this.activeIndex}`);
    }
    return model;
  }

  /**
   * Return a new RetryModel with a different active model.
   */
  private withActive(index: number): RetryModel {
    return RetryModel.createWithActive(this.models, index, this.retryConfig);
  }

  /**
   * Yield RetryModels in attempt order: active model first, then others.
   */
  private *attemptVariants(): Generator<RetryModel> {
    yield this;
    for (let i = 0; i < this.models.length; i++) {
      if (i !== this.activeIndex) {
        yield this.withActive(i);
      }
    }
  }

  /**
   * Async generator that yields model variants with backoff delays between retries.
   *
   * Yields the active model variant first. After each yield, if the caller
   * encountered an error and iterates again, this applies the appropriate
   * backoff delay before yielding the next attempt. Each model gets
   * maxRetries additional attempts before moving to the next fallback model.
   */
  async *variantsAsync(): AsyncGenerator<RetryModel> {
    const config = this.retryConfig;
    for (const variant of this.attemptVariants()) {
      for (let attempt = 0; attempt <= config.maxRetries; attempt++) {
        yield variant;
        // If caller iterates again, they hit an error - apply backoff
        if (attempt < config.maxRetries) {
          const delay = calculateDelay(config, attempt + 1);
          await sleep(delay * 1000);
        }
      }
    }
  }

  /**
   * Execute an async function with retry logic across the RetryModel's models.
   *
   * @param fn - Async function that takes a Model and returns a result.
   * @returns A tuple of (result, failures, updatedRetryModel).
   * @throws RetriesExhausted if all models exhaust retries.
   */
  private async withRetry<T>(
    fn: (model: Model) => Promise<T>,
  ): Promise<[T, RetryFailure[], RetryModel]> {
    const failures: RetryFailure[] = [];

    for await (const variant of this.variantsAsync()) {
      const model = variant.getActiveModel();
      try {
        const result = await fn(model);
        return [result, failures, variant];
      } catch (error) {
        /* v8 ignore next -- defensive: errors are always Error instances */
        if (!(error instanceof Error)) throw error;
        if (!isRetryableError(error, variant.retryConfig)) throw error;
        failures.push({ model, exception: error });
      }
    }

    // All models exhausted
    throw new RetriesExhausted(failures);
  }

  // ===== Call Methods =====

  /**
   * Generate a RetryResponse by calling this model's LLM provider.
   *
   * @param content - User content or LLM messages to send to the LLM.
   * @param options - Optional tools and format configuration.
   * @returns A RetryResponse object containing the LLM-generated content and retry metadata.
   * @throws RetriesExhausted if all retry attempts fail.
   */
  override async call(
    content: UserContent | readonly Message[],
    options?: { tools?: Tools; format?: Format | null },
  ): Promise<RetryResponse> {
    const [response, failures, updatedModel] = await this.withRetry((m) =>
      m.call(content, options),
    );
    return new RetryResponse(response, updatedModel, failures);
  }

  /**
   * Generate a RetryStreamResponse by streaming from this model's LLM provider.
   *
   * The returned response supports automatic retry on failure. If a retryable
   * error occurs during iteration, a `StreamRestarted` exception is raised
   * and the user can re-iterate to continue from the new attempt.
   *
   * @param content - User content or LLM messages to send to the LLM.
   * @param options - Optional tools and format configuration.
   * @returns A RetryStreamResponse for iterating over the LLM-generated content.
   */
  override async stream(
    content: UserContent | readonly Message[],
    options?: { tools?: Tools; format?: Format | null },
  ): Promise<RetryStreamResponse> {
    const streamFn = (m: Model) => m.stream(content, options);
    const variantsIter = this.variantsAsync();
    const initialVariant = (await variantsIter.next()).value as RetryModel;
    const initialStream = await streamFn(initialVariant.getActiveModel());
    return new RetryStreamResponse(
      streamFn,
      initialStream,
      initialVariant,
      variantsIter,
    );
  }

  // ===== Context Call Methods =====

  /**
   * Generate a ContextRetryResponse by calling this model's LLM provider with context.
   *
   * @param ctx - A Context with the required deps type.
   * @param content - User content or LLM messages to send to the LLM.
   * @param options - Optional context-aware tools and format configuration.
   * @returns A ContextRetryResponse object containing the LLM-generated content and retry metadata.
   * @throws RetriesExhausted if all retry attempts fail.
   */
  override async contextCall<DepsT>(
    ctx: Context<DepsT>,
    content: UserContent | readonly Message[],
    options?: { tools?: ContextTools<DepsT>; format?: Format | null },
  ): Promise<ContextRetryResponse<DepsT>> {
    const [response, failures, updatedModel] = await this.withRetry((m) =>
      m.contextCall(ctx, content, options),
    );
    return new ContextRetryResponse(response, updatedModel, failures);
  }

  /**
   * Generate a ContextRetryStreamResponse by streaming from this model's LLM provider with context.
   *
   * @param ctx - A Context with the required deps type.
   * @param content - User content or LLM messages to send to the LLM.
   * @param options - Optional context-aware tools and format configuration.
   * @returns A ContextRetryStreamResponse for iterating over the LLM-generated content.
   */
  override async contextStream<DepsT>(
    ctx: Context<DepsT>,
    content: UserContent | readonly Message[],
    options?: { tools?: ContextTools<DepsT>; format?: Format | null },
  ): Promise<ContextRetryStreamResponse<DepsT>> {
    const streamFn = (m: Model) => m.contextStream(ctx, content, options);
    const variantsIter = this.variantsAsync();
    const initialVariant = (await variantsIter.next()).value as RetryModel;
    const initialStream = await streamFn(initialVariant.getActiveModel());
    return new ContextRetryStreamResponse(
      streamFn,
      initialStream,
      initialVariant,
      variantsIter,
    );
  }

  // ===== Resume Methods =====

  /**
   * Generate a new RetryResponse by extending another response's messages.
   *
   * @param response - Previous response to extend.
   * @param content - Additional user content to append.
   * @returns A new RetryResponse containing the extended conversation.
   * @throws RetriesExhausted if all retry attempts fail.
   */
  override async resume(
    response: RootResponse,
    content: UserContent,
  ): Promise<RetryResponse> {
    const [newResponse, failures, updatedModel] = await this.withRetry((m) =>
      m.resume(response, content),
    );
    return new RetryResponse(newResponse, updatedModel, failures);
  }

  /**
   * Generate a new RetryStreamResponse by extending another response's messages.
   *
   * @param response - Previous stream response to extend.
   * @param content - Additional user content to append.
   * @returns A new RetryStreamResponse for streaming the extended conversation.
   */
  override async resumeStream(
    response: RootResponse,
    content: UserContent,
  ): Promise<RetryStreamResponse> {
    const streamFn = (m: Model) => m.resumeStream(response, content);
    const variantsIter = this.variantsAsync();
    const initialVariant = (await variantsIter.next()).value as RetryModel;
    const initialStream = await streamFn(initialVariant.getActiveModel());
    return new RetryStreamResponse(
      streamFn,
      initialStream,
      initialVariant,
      variantsIter,
    );
  }

  // ===== Context Resume Methods =====

  /**
   * Generate a new ContextRetryResponse by extending another response's messages.
   *
   * @param ctx - A Context with the required deps type.
   * @param response - Previous context response to extend.
   * @param content - Additional user content to append.
   * @returns A new ContextRetryResponse containing the extended conversation.
   * @throws RetriesExhausted if all retry attempts fail.
   */
  override async contextResume<DepsT>(
    ctx: Context<DepsT>,
    response: RootResponse,
    content: UserContent,
  ): Promise<ContextRetryResponse<DepsT>> {
    const [newResponse, failures, updatedModel] = await this.withRetry((m) =>
      m.contextResume(ctx, response, content),
    );
    return new ContextRetryResponse(newResponse, updatedModel, failures);
  }

  /**
   * Generate a new ContextRetryStreamResponse by extending another response's messages.
   *
   * @param ctx - A Context with the required deps type.
   * @param response - Previous context stream response to extend.
   * @param content - Additional user content to append.
   * @returns A new ContextRetryStreamResponse for streaming the extended conversation.
   */
  override async contextResumeStream<DepsT>(
    ctx: Context<DepsT>,
    response: RootResponse,
    content: UserContent,
  ): Promise<ContextRetryStreamResponse<DepsT>> {
    const streamFn = (m: Model) =>
      m.contextResumeStream(ctx, response, content);
    const variantsIter = this.variantsAsync();
    const initialVariant = (await variantsIter.next()).value as RetryModel;
    const initialStream = await streamFn(initialVariant.getActiveModel());
    return new ContextRetryStreamResponse(
      streamFn,
      initialStream,
      initialVariant,
      variantsIter,
    );
  }
}

/**
 * Get the RetryModel to use, checking context for overrides.
 *
 * If a model is set in context (via `withModel()`), that model is used instead,
 * wrapped with this response's retry config.
 *
 * @param storedRetryModel - The RetryModel stored on the response.
 * @returns Either the context model (wrapped in RetryModel if needed) or the stored model.
 */
export function getRetryModelFromContext(
  storedRetryModel: RetryModel,
): RetryModel {
  const contextModel = modelFromContext();
  if (contextModel !== undefined) {
    if (contextModel instanceof RetryModel) {
      return contextModel;
    }
    return new RetryModel(contextModel, storedRetryModel.retryConfig);
  }
  return storedRetryModel;
}

/**
 * Helper for creating a `RetryModel` instance with retry logic.
 *
 * This function creates a RetryModel that wraps the specified model with automatic
 * retry functionality. It accepts both model parameters (temperature, maxTokens, etc.)
 * and retry configuration (maxRetries, initialDelay, etc.) in a single call.
 *
 * @param modelId - A model ID string (e.g., "openai/gpt-4o").
 * @param args - Combined model parameters and retry configuration.
 * @returns A RetryModel instance configured with the specified model and retry settings.
 *
 * @example Basic usage with retry defaults
 * ```typescript
 * import * as llm from "mirascope/llm";
 *
 * const model = llm.retryModel("openai/gpt-4o");
 * const response = await model.call("Hello!");
 * ```
 *
 * @example With model parameters and retry configuration
 * ```typescript
 * const model = llm.retryModel("openai/gpt-4o", {
 *   temperature: 0.7,
 *   maxTokens: 1000,
 *   maxRetries: 5,
 *   initialDelay: 1.0,
 *   backoffMultiplier: 2.0,
 * });
 * const response = await model.call("Write a story.");
 * ```
 *
 * @example With fallback models
 * ```typescript
 * const model = llm.retryModel("openai/gpt-4o", {
 *   maxRetries: 3,
 *   fallbackModels: ["anthropic/claude-sonnet-4-20250514", "google/gemini-2.0-flash"],
 * });
 * const response = await model.call("Complex task...");
 * ```
 */
export function retryModel(
  modelId: ModelId,
  args: RetryModelParams = {},
): RetryModel {
  // Separate retry args from model params
  const retryArgs: RetryArgs = {};
  const modelParams: Params = {};

  for (const [key, value] of Object.entries(args)) {
    if (RETRY_ARG_KEYS.has(key)) {
      (retryArgs as Record<string, unknown>)[key] = value;
    } else {
      (modelParams as Record<string, unknown>)[key] = value;
    }
  }

  const retryConfig = RetryConfig.fromArgs(retryArgs);
  return new RetryModel(modelId, retryConfig, modelParams);
}
