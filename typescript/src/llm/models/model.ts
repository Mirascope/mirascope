/**
 * The Model class - unified interface for LLM calls.
 */

import type { Message, UserContent } from '@/llm/messages';
import { promoteToMessages } from '@/llm/messages';
import type { Params } from '@/llm/models/params';
import type { BaseProvider } from '@/llm/providers/base';
import type { ModelId } from '@/llm/providers/model-id';
import type { ProviderId } from '@/llm/providers/provider-id';
import { getProviderForModel } from '@/llm/providers/registry';
import type { Response } from '@/llm/responses';
import type { StreamResponse } from '@/llm/responses/stream-response';

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
  async call(content: UserContent | readonly Message[]): Promise<Response> {
    const messages = promoteToMessages(content);
    return this.provider.call({
      modelId: this.modelId,
      messages,
      params: this.params,
    });
  }

  /**
   * Generate a streaming Response by calling this model's LLM provider.
   *
   * @param content - Content to send to the LLM. Can be a string (converted to user
   *   message), UserContent, a sequence of UserContent, or a sequence of Messages
   *   for full control.
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
    content: UserContent | readonly Message[]
  ): Promise<StreamResponse> {
    const messages = promoteToMessages(content);
    return this.provider.stream({
      modelId: this.modelId,
      messages,
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
