/**
 * Retry response classes that extend base responses with retry metadata.
 */

import type { ToolOutput } from "@/llm/content/tool-output";
import type { Context } from "@/llm/context";
import type { AssistantMessage, UserContent } from "@/llm/messages";
import type { Jsonable } from "@/llm/types/jsonable";

import { ContextResponse } from "@/llm/responses/context-response";
import { Response } from "@/llm/responses/response";

import type { RetryConfig } from "./retry-config";
import type { RetryModel } from "./retry-model";
import type { RetryFailure } from "./utils";

import { getRetryModelFromContext } from "./retry-model";

/**
 * Response that includes retry metadata.
 *
 * Extends `Response` to add retry configuration and failure tracking.
 * The `model` getter returns a `RetryModel` with the successful model
 * as the active model.
 *
 * @template F - The type of the formatted output when using structured outputs.
 */
export class RetryResponse<F = unknown> extends Response<F> {
  /**
   * The RetryModel with the successful model as active.
   */
  private readonly _retryModel: RetryModel;

  /**
   * Failed attempts before the successful one (empty if first attempt succeeded).
   */
  readonly retryFailures: RetryFailure[];

  /**
   * Initialize a RetryResponse.
   *
   * @param response - The successful response from the LLM.
   * @param retryModel - RetryModel with the successful model as active.
   * @param retryFailures - List of failed attempts before success.
   */
  constructor(
    response: Response<F>,
    retryModel: RetryModel,
    retryFailures: RetryFailure[],
  ) {
    // Extract the assistant message from the response
    const lastMessage = response.messages[response.messages.length - 1];
    /* v8 ignore next 3 -- defensive: response always has assistant message */
    if (lastMessage === undefined || lastMessage.role !== "assistant") {
      throw new Error("Expected assistant message in response");
    }
    const assistantMessage = lastMessage as AssistantMessage;

    // Call parent constructor with the response's init data
    super({
      raw: response.raw,
      providerId: response.providerId,
      modelId: response.modelId,
      providerModelName: response.providerModelName,
      params: response.params,
      tools: response.toolkit,
      format: response.format,
      inputMessages: response.messages.slice(0, -1),
      assistantMessage,
      finishReason: response.finishReason,
      usage: response.usage,
    });

    this._retryModel = retryModel;
    this.retryFailures = retryFailures;
  }

  /**
   * A RetryModel with the successful model as active.
   *
   * If a model is set in context (via `withModel()`), that model is used
   * instead, wrapped with this response's retry config.
   *
   * Otherwise, this RetryModel has the same pool of available models, but with
   * the model that succeeded set as the active model. This means:
   * - `response.model.modelId` equals `response.modelId`
   * - `response.resume()` will try the successful model first
   */
  override get model(): Promise<RetryModel> {
    return Promise.resolve(getRetryModelFromContext(this._retryModel));
  }

  /**
   * The retry configuration for this response.
   */
  get retryConfig(): RetryConfig {
    return this._retryModel.retryConfig;
  }

  /**
   * Generate a new RetryResponse using this response's messages with additional user content.
   *
   * @param content - The new user message content to append to the message history.
   * @returns A new RetryResponse instance generated from the extended message history.
   */
  override async resume(content: UserContent): Promise<RetryResponse<F>> {
    const model = await this.model;
    return model.resume(this, content) as Promise<RetryResponse<F>>;
  }

  /**
   * Execute all tool calls in this response using the registered tools.
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
 * Context response that includes retry metadata.
 *
 * Extends `ContextResponse` to add retry configuration and failure tracking.
 * The `model` getter returns a `RetryModel` with the successful model
 * as the active model.
 *
 * @template DepsT - The type of dependencies in the context.
 * @template F - The type of the formatted output when using structured outputs.
 */
export class ContextRetryResponse<
  DepsT = unknown,
  F = unknown,
> extends ContextResponse<DepsT, F> {
  /**
   * The RetryModel with the successful model as active.
   */
  private readonly _retryModel: RetryModel;

  /**
   * Failed attempts before the successful one (empty if first attempt succeeded).
   */
  readonly retryFailures: RetryFailure[];

  /**
   * Initialize a ContextRetryResponse.
   *
   * @param response - The successful context response from the LLM.
   * @param retryModel - RetryModel with the successful model as active.
   * @param retryFailures - List of failed attempts before success.
   */
  constructor(
    response: ContextResponse<DepsT, F>,
    retryModel: RetryModel,
    retryFailures: RetryFailure[],
  ) {
    // Extract the assistant message from the response
    const lastMessage = response.messages[response.messages.length - 1];
    /* v8 ignore next 3 -- defensive: response always has assistant message */
    if (lastMessage === undefined || lastMessage.role !== "assistant") {
      throw new Error("Expected assistant message in response");
    }
    const assistantMessage = lastMessage as AssistantMessage;

    // Call parent constructor with the response's init data
    super({
      raw: response.raw,
      providerId: response.providerId,
      modelId: response.modelId,
      providerModelName: response.providerModelName,
      params: response.params,
      tools: response.contextToolkit,
      format: response.format,
      inputMessages: response.messages.slice(0, -1),
      assistantMessage,
      finishReason: response.finishReason,
      usage: response.usage,
    });

    this._retryModel = retryModel;
    this.retryFailures = retryFailures;
  }

  /**
   * A RetryModel with the successful model as active.
   *
   * If a model is set in context (via `withModel()`), that model is used
   * instead, wrapped with this response's retry config.
   */
  override get model(): Promise<RetryModel> {
    return Promise.resolve(getRetryModelFromContext(this._retryModel));
  }

  /**
   * The retry configuration for this response.
   */
  get retryConfig(): RetryConfig {
    return this._retryModel.retryConfig;
  }

  /**
   * Generate a new ContextRetryResponse using this response's messages with additional user content.
   *
   * @param ctx - A Context with the required deps type.
   * @param content - The new user message content to append to the message history.
   * @returns A new ContextRetryResponse instance generated from the extended message history.
   */
  override async resume(
    ctx: Context<DepsT>,
    content: UserContent,
  ): Promise<ContextRetryResponse<DepsT, F>> {
    const model = await this.model;
    return model.contextResume(ctx, this, content) as Promise<
      ContextRetryResponse<DepsT, F>
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
