/**
 * OpenAI provider implementation with routing between Completions and Responses APIs.
 */

import OpenAI from 'openai';

import { FeatureNotSupportedError } from '@/llm/exceptions';
import type { Message } from '@/llm/messages';
import type { Params } from '@/llm/models';
import { BaseProvider } from '@/llm/providers/base';
import { OPENAI_ERROR_MAP } from '@/llm/providers/openai/_utils/errors';
import { OpenAICompletionsProvider } from '@/llm/providers/openai/completions/provider';
import type { ApiMode, OpenAIModelId } from '@/llm/providers/openai/model-id';
import { Response } from '@/llm/responses';

/**
 * Provider for the OpenAI API with intelligent routing between Completions and Responses APIs.
 *
 * This provider automatically selects the appropriate API based on the model ID:
 * - Model IDs ending with `:completions` force the Chat Completions API
 * - Model IDs ending with `:responses` force the Responses API
 * - Otherwise, defaults to the Completions API (Responses API support coming soon)
 *
 * @example
 * ```typescript
 * const provider = new OpenAIProvider();
 *
 * // Uses Completions API (default)
 * const response = await provider.call({
 *   modelId: 'openai/gpt-4o',
 *   messages: [user('Hello!')],
 * });
 *
 * // Explicitly force Completions API
 * const response2 = await provider.call({
 *   modelId: 'openai/gpt-4o:completions',
 *   messages: [user('Hello!')],
 * });
 * ```
 */
export class OpenAIProvider extends BaseProvider {
  readonly id = 'openai' as const;
  protected readonly errorMap = OPENAI_ERROR_MAP;

  private readonly completionsProvider: OpenAICompletionsProvider;

  /**
   * Create a new OpenAI provider instance.
   *
   * @param init - Configuration options
   * @param init.apiKey - OpenAI API key (defaults to OPENAI_API_KEY env var)
   * @param init.baseURL - Optional custom base URL for the API
   */
  constructor(init: { apiKey?: string; baseURL?: string } = {}) {
    super();
    this.completionsProvider = new OpenAICompletionsProvider(init);
  }

  /**
   * Execute a call to the OpenAI API, routing to the appropriate API based on model ID.
   *
   * @param args - Call arguments
   * @param args.modelId - The OpenAI model ID to use (optionally with :completions or :responses suffix)
   * @param args.messages - Array of messages to send
   * @param args.params - Optional additional parameters
   * @returns Response object containing the API response
   */
  protected async _call(args: {
    modelId: string;
    messages: readonly Message[];
    params?: Params;
  }): Promise<Response> {
    const modelId = args.modelId as OpenAIModelId;
    const apiMode = this.chooseApiMode(modelId);

    if (apiMode === 'responses') {
      throw new FeatureNotSupportedError(
        'responses API',
        'openai',
        modelId,
        'The OpenAI Responses API is not yet supported. ' +
          'Use the :completions suffix (e.g., "openai/gpt-4o:completions") ' +
          'or wait for Responses API support to be implemented.'
      );
    }

    // Delegate to the completions provider
    return this.completionsProvider.call({
      modelId: args.modelId,
      messages: args.messages,
      params: args.params,
    });
  }

  /**
   * Determine which API mode to use based on the model ID.
   *
   * @param modelId - The model ID to check
   * @returns The API mode to use ('completions' or 'responses')
   */
  private chooseApiMode(modelId: OpenAIModelId): ApiMode {
    // Check explicit suffix
    if (modelId.endsWith(':completions')) {
      return 'completions';
    }
    if (modelId.endsWith(':responses')) {
      return 'responses';
    }

    // Default to completions for now
    // TODO: Implement smarter routing based on model capabilities
    return 'completions';
  }

  /**
   * Extract the HTTP status code from an OpenAI API error.
   *
   * @param e - The error to extract the status from
   * @returns The HTTP status code or undefined if not available
   */
  /* v8 ignore start - error handling delegated to completions provider */
  protected getErrorStatus(e: Error): number | undefined {
    // OpenAI SDK uses 'status' property
    return (e as InstanceType<typeof OpenAI.APIError>).status;
  }
  /* v8 ignore stop */
}
