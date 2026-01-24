/**
 * Anthropic provider implementation.
 */

import Anthropic from '@anthropic-ai/sdk';

import type { Message } from '@/llm/messages';
import type { Params } from '@/llm/models';
import { BaseProvider } from '@/llm/providers/base';
import type { AnthropicModelId } from '@/llm/providers/anthropic/model-id';
import { modelName } from '@/llm/providers/anthropic/model-id';
import { Response } from '@/llm/responses';
import {
  ANTHROPIC_ERROR_MAP,
  buildRequestParams,
  decodeResponse,
} from '@/llm/providers/anthropic/_utils';

/**
 * Provider for the Anthropic API.
 *
 * @example
 * ```typescript
 * const provider = new AnthropicProvider();
 * const response = await provider.call({
 *   modelId: 'claude-sonnet-4-20250514',
 *   messages: [user('Hello!')],
 * });
 * console.log(response.text());
 * ```
 */
export class AnthropicProvider extends BaseProvider {
  readonly id = 'anthropic' as const;
  protected readonly errorMap = ANTHROPIC_ERROR_MAP;

  private readonly client: Anthropic;

  /**
   * Create a new Anthropic provider instance.
   *
   * @param init - Configuration options
   * @param init.apiKey - Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
   * @param init.baseURL - Optional custom base URL for the API
   */
  constructor(init: { apiKey?: string; baseURL?: string } = {}) {
    super();
    this.client = new Anthropic({
      apiKey: init.apiKey,
      baseURL: init.baseURL,
    });
  }

  /**
   * Execute a call to the Anthropic API.
   *
   * @param args - Call arguments
   * @param args.modelId - The Anthropic model ID to use
   * @param args.messages - Array of messages to send
   * @param args.params - Optional additional parameters
   * @returns Response object containing the API response
   */
  protected async _call(args: {
    modelId: string;
    messages: readonly Message[];
    params?: Params;
  }): Promise<Response> {
    const modelId = args.modelId as AnthropicModelId;
    const requestParams = buildRequestParams(
      modelId,
      args.messages,
      args.params
    );

    const anthropicResponse = await this.client.messages.create(requestParams);

    const { assistantMessage, finishReason, usage } = decodeResponse(
      anthropicResponse,
      modelId
    );

    return new Response({
      raw: anthropicResponse,
      providerId: 'anthropic',
      modelId,
      providerModelName: modelName(modelId),
      params: args.params ?? {},
      inputMessages: args.messages,
      assistantMessage,
      finishReason,
      usage,
    });
  }

  /**
   * Extract the HTTP status code from an Anthropic API error.
   *
   * @param e - The error to extract the status from
   * @returns The HTTP status code or undefined if not available
   */
  protected getErrorStatus(e: Error): number | undefined {
    // Anthropic SDK uses 'status' property
    return (e as InstanceType<typeof Anthropic.APIError>).status;
  }
}
