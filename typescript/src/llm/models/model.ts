/**
 * The Model class - unified interface for LLM calls.
 */

import type { Context } from '@/llm/context';
import type { Message, UserContent } from '@/llm/messages';
import { promoteToMessages } from '@/llm/messages';
import type { RootResponse } from '@/llm/responses/root-response';
import type { Params } from '@/llm/models/params';
import type { BaseProvider } from '@/llm/providers/base';
import type { ModelId } from '@/llm/providers/model-id';
import type { ProviderId } from '@/llm/providers/provider-id';
import { getProviderForModel } from '@/llm/providers/registry';
import type { Response } from '@/llm/responses';
import type { ContextResponse } from '@/llm/responses/context-response';
import type { ContextStreamResponse } from '@/llm/responses/context-stream-response';
import type { StreamResponse } from '@/llm/responses/stream-response';
import type { ToolSchema } from '@/llm/tools';

/**
 * The unified LLM interface that delegates to provider-specific clients.
 *
 * This class provides a consistent interface for interacting with language models
 * from various providers. It handles the common operations like generating responses
 * by delegating to the appropriate provider methods.
 *
 * @example
 * ```typescript
 * import { Model } from 'mirascope/llm';
 *
 * const model = new Model('anthropic/claude-sonnet-4-20250514');
 * const response = await model.call('Hello!');
 * console.log(response.text());
 * ```
 *
 * @example With parameters
 * ```typescript
 * const model = new Model('anthropic/claude-sonnet-4-20250514', {
 *   temperature: 0.7,
 *   maxTokens: 1000,
 * });
 * const response = await model.call('Write a haiku about coding.');
 * ```
 */
export class Model {
  /**
   * The model ID being used (e.g., "anthropic/claude-sonnet-4-20250514").
   */
  readonly modelId: ModelId;

  /**
   * The default parameters for the model (temperature, maxTokens, etc.).
   */
  readonly params: Params;

  /**
   * Initialize the Model with a model ID and optional parameters.
   *
   * @param modelId - The model ID in "provider/model-name" format.
   * @param params - Optional parameters for the model.
   * @throws Error if the model ID format is invalid.
   */
  constructor(modelId: ModelId, params: Params = {}) {
    if (!modelId.includes('/')) {
      throw new Error(
        `Invalid model_id format. Expected format: 'provider/model-name' ` +
          `(e.g., 'anthropic/claude-sonnet-4-20250514'). Got: '${modelId}'`
      );
    }
    this.modelId = modelId;
    this.params = params;
  }

  /**
   * The provider being used (e.g., an AnthropicProvider).
   *
   * This property dynamically looks up the provider from the registry based on
   * the current modelId. This allows provider overrides via registerProvider()
   * to take effect even after the model instance is created.
   *
   * @throws NoRegisteredProviderError if no provider is available for the modelId.
   */
  get provider(): BaseProvider {
    return getProviderForModel(this.modelId);
  }

  /**
   * The string ID of the provider being used (e.g., "anthropic").
   *
   * @throws NoRegisteredProviderError if no provider is available for the modelId.
   */
  get providerId(): ProviderId {
    return this.provider.id;
  }

  /**
   * Generate a Response by calling this model's LLM provider.
   *
   * @param content - Content to send to the LLM. Can be a string (converted to user
   *   message), UserContent, a sequence of UserContent, or a sequence of Messages
   *   for full control.
   * @param tools - Optional tools to make available to the model.
   * @returns A Response object containing the LLM-generated content.
   *
   * @example Simple string input
   * ```typescript
   * const response = await model.call('What is the capital of France?');
   * console.log(response.text());
   * ```
   *
   * @example With message array
   * ```typescript
   * import { system, user } from 'mirascope/llm/messages';
   *
   * const response = await model.call([
   *   system('You are a helpful assistant.'),
   *   user('What is the capital of France?'),
   * ]);
   * ```
   */
  async call(
    content: UserContent | readonly Message[],
    tools?: readonly ToolSchema[]
  ): Promise<Response> {
    const messages = promoteToMessages(content);
    return this.provider.call({
      modelId: this.modelId,
      messages,
      tools,
      params: this.params,
    });
  }

  /**
   * Generate a streaming Response by calling this model's LLM provider.
   *
   * @param content - Content to send to the LLM. Can be a string (converted to user
   *   message), UserContent, a sequence of UserContent, or a sequence of Messages
   *   for full control.
   * @param tools - Optional tools to make available to the model.
   * @returns A StreamResponse object for consuming the streamed content.
   *
   * @example Simple string input
   * ```typescript
   * const response = await model.stream('What is the capital of France?');
   * for await (const text of response.textStream()) {
   *   process.stdout.write(text);
   * }
   * ```
   *
   * @example With message array
   * ```typescript
   * import { system, user } from 'mirascope/llm/messages';
   *
   * const response = await model.stream([
   *   system('You are a helpful assistant.'),
   *   user('What is the capital of France?'),
   * ]);
   *
   * for await (const text of response.textStream()) {
   *   process.stdout.write(text);
   * }
   *
   * // After consuming the stream, get the full text
   * console.log(response.text());
   * ```
   */
  async stream(
    content: UserContent | readonly Message[],
    tools?: readonly ToolSchema[]
  ): Promise<StreamResponse> {
    const messages = promoteToMessages(content);
    return this.provider.stream({
      modelId: this.modelId,
      messages,
      tools,
      params: this.params,
    });
  }

  /**
   * Generate a ContextResponse by calling this model's LLM provider with context.
   *
   * This method accepts a context for dependency injection, enabling context-aware
   * tools and prompts.
   *
   * @template DepsT - The type of dependencies in the context.
   * @param ctx - The context containing dependencies for tools.
   * @param content - Content to send to the LLM.
   * @param tools - Optional tools to make available to the model.
   * @returns A ContextResponse object containing the LLM-generated content.
   *
   * @example
   * ```typescript
   * interface MyDeps { userId: string; }
   *
   * const ctx = createContext<MyDeps>({ userId: '123' });
   * const response = await model.contextCall(ctx, 'Hello!');
   * console.log(response.text());
   * ```
   */
  async contextCall<DepsT>(
    ctx: Context<DepsT>,
    content: UserContent | readonly Message[],
    tools?: readonly ToolSchema[]
  ): Promise<ContextResponse<DepsT>> {
    const messages = promoteToMessages(content);
    return this.provider.contextCall({
      ctx,
      modelId: this.modelId,
      messages,
      tools,
      params: this.params,
    });
  }

  /**
   * Generate a streaming ContextStreamResponse by calling this model's LLM provider with context.
   *
   * This method accepts a context for dependency injection, enabling context-aware
   * tools and prompts.
   *
   * @template DepsT - The type of dependencies in the context.
   * @param ctx - The context containing dependencies for tools.
   * @param content - Content to send to the LLM.
   * @param tools - Optional tools to make available to the model.
   * @returns A ContextStreamResponse object for consuming the streamed content.
   *
   * @example
   * ```typescript
   * interface MyDeps { userId: string; }
   *
   * const ctx = createContext<MyDeps>({ userId: '123' });
   * const response = await model.contextStream(ctx, 'Hello!');
   * for await (const text of response.textStream()) {
   *   process.stdout.write(text);
   * }
   * ```
   */
  async contextStream<DepsT>(
    ctx: Context<DepsT>,
    content: UserContent | readonly Message[],
    tools?: readonly ToolSchema[]
  ): Promise<ContextStreamResponse<DepsT>> {
    const messages = promoteToMessages(content);
    return this.provider.contextStream({
      ctx,
      modelId: this.modelId,
      messages,
      tools,
      params: this.params,
    });
  }

  // ===== Resume Methods =====

  /**
   * Generate a new Response by extending a previous response's messages with additional user content.
   *
   * Uses the previous response's tools and output format, and this model's params.
   *
   * @param response - Previous response to extend.
   * @param content - Additional user content to append.
   * @returns A new Response object containing the extended conversation.
   *
   * @example
   * ```typescript
   * const response = await model.call('Hello!');
   * const followUp = await model.resume(response, 'Tell me more');
   * console.log(followUp.text());
   * ```
   */
  async resume(
    response: RootResponse,
    content: UserContent
  ): Promise<Response> {
    return this.provider.resume({
      modelId: this.modelId,
      response,
      content,
      params: this.params,
    });
  }

  /**
   * Generate a new StreamResponse by extending a previous response's messages with additional user content.
   *
   * Uses the previous response's tools and output format, and this model's params.
   *
   * @param response - Previous response to extend.
   * @param content - Additional user content to append.
   * @returns A new StreamResponse object for consuming the streamed content.
   *
   * @example
   * ```typescript
   * const response = await model.call('Hello!');
   * const followUp = await model.resumeStream(response, 'Tell me more');
   * for await (const text of followUp.textStream()) {
   *   process.stdout.write(text);
   * }
   * ```
   */
  async resumeStream(
    response: RootResponse,
    content: UserContent
  ): Promise<StreamResponse> {
    return this.provider.resumeStream({
      modelId: this.modelId,
      response,
      content,
      params: this.params,
    });
  }

  /**
   * Generate a new ContextResponse by extending a previous response's messages with additional user content.
   *
   * Uses the previous response's tools and output format, and this model's params.
   *
   * @template DepsT - The type of dependencies in the context.
   * @param ctx - The context containing dependencies for tools.
   * @param response - Previous response to extend.
   * @param content - Additional user content to append.
   * @returns A new ContextResponse object containing the extended conversation.
   *
   * @example
   * ```typescript
   * const response = await model.contextCall(ctx, 'Hello!');
   * const followUp = await model.contextResume(ctx, response, 'Tell me more');
   * console.log(followUp.text());
   * ```
   */
  async contextResume<DepsT>(
    ctx: Context<DepsT>,
    response: RootResponse,
    content: UserContent
  ): Promise<ContextResponse<DepsT>> {
    return this.provider.contextResume({
      ctx,
      modelId: this.modelId,
      response,
      content,
      params: this.params,
    });
  }

  /**
   * Generate a new ContextStreamResponse by extending a previous response's messages with additional user content.
   *
   * Uses the previous response's tools and output format, and this model's params.
   *
   * @template DepsT - The type of dependencies in the context.
   * @param ctx - The context containing dependencies for tools.
   * @param response - Previous response to extend.
   * @param content - Additional user content to append.
   * @returns A new ContextStreamResponse object for consuming the streamed content.
   *
   * @example
   * ```typescript
   * const response = await model.contextStream(ctx, 'Hello!');
   * await response.consume();
   * const followUp = await model.contextResumeStream(ctx, response, 'Tell me more');
   * for await (const text of followUp.textStream()) {
   *   process.stdout.write(text);
   * }
   * ```
   */
  async contextResumeStream<DepsT>(
    ctx: Context<DepsT>,
    response: RootResponse,
    content: UserContent
  ): Promise<ContextStreamResponse<DepsT>> {
    return this.provider.contextResumeStream({
      ctx,
      modelId: this.modelId,
      response,
      content,
      params: this.params,
    });
  }
}

/**
 * Helper for creating a Model instance.
 *
 * This is just an alias for the Model constructor, added for convenience.
 *
 * @param modelId - A model ID string (e.g., "anthropic/claude-sonnet-4-20250514").
 * @param params - Optional parameters to configure the model.
 * @returns A Model instance.
 *
 * @example
 * ```typescript
 * import { model } from 'mirascope/llm';
 *
 * const m = model('anthropic/claude-sonnet-4-20250514');
 * const response = await m.call('Hello!');
 * ```
 */
export function model(modelId: ModelId, params: Params = {}): Model {
  return new Model(modelId, params);
}
