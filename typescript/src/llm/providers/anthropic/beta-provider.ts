/**
 * Beta Anthropic provider implementation.
 *
 * Uses the beta API (client.beta.messages.create()) which supports
 * additional features like extended thinking and structured outputs.
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
} from '@/llm/providers/anthropic/_utils';
import { betaDecodeResponse } from '@/llm/providers/anthropic/beta-decode';

/**
 * Provider for the Anthropic Beta API.
 *
 * This provider uses the beta messages API which supports additional features
 * like extended thinking and structured outputs. Users opt-in by using the
 * `anthropic-beta/` prefix in their model ID.
 *
 * @example
 * ```typescript
 * const provider = new AnthropicBetaProvider();
 * const response = await provider.call({
 *   modelId: 'claude-sonnet-4-20250514',
 *   messages: [user('Hello!')],
 * });
 * console.log(response.text());
 * ```
 */
export class AnthropicBetaProvider extends BaseProvider {
  readonly id = 'anthropic-beta' as const;
  protected readonly errorMap = ANTHROPIC_ERROR_MAP;

  private readonly client: Anthropic;

  /**
   * Create a new Anthropic Beta provider instance.
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
   * Execute a call to the Anthropic Beta API.
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

    // Use beta API instead of standard
    const betaResponse = await this.client.beta.messages.create(requestParams);

    const { assistantMessage, finishReason, usage } = betaDecodeResponse(
      betaResponse,
      modelId
    );

    return new Response({
      raw: betaResponse,
      // Note: providerId is 'anthropic' (not 'anthropic-beta') to match Python SDK
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
