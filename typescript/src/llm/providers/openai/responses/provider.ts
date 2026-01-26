/**
 * OpenAI Responses provider implementation.
 */

import OpenAI from 'openai';

import type { Message } from '@/llm/messages';
import type { Params } from '@/llm/models';
import { BaseProvider } from '@/llm/providers/base';
import { getIncludeThoughts } from '@/llm/providers/_utils';
import { OPENAI_ERROR_MAP } from '@/llm/providers/openai/_utils/errors';
import type { OpenAIModelId } from '@/llm/providers/openai/model-id';
import { modelName } from '@/llm/providers/openai/model-id';
import {
  buildRequestParams,
  decodeResponse,
} from '@/llm/providers/openai/responses/_utils';
import { Response } from '@/llm/responses';

/**
 * Provider for the OpenAI Responses API.
 *
 * This provider uses the Responses API (not the Chat Completions API).
 * For the routing provider that selects between APIs, use `OpenAIProvider`.
 *
 * @example
 * ```typescript
 * const provider = new OpenAIResponsesProvider();
 * const response = await provider.call({
 *   modelId: 'openai/gpt-4o:responses',
 *   messages: [user('Hello!')],
 * });
 * console.log(response.text());
 * ```
 */
export class OpenAIResponsesProvider extends BaseProvider {
  readonly id = 'openai' as const;
  protected readonly errorMap = OPENAI_ERROR_MAP;

  private readonly client: OpenAI;

  /**
   * Create a new OpenAI Responses provider instance.
   *
   * @param init - Configuration options
   * @param init.apiKey - OpenAI API key (defaults to OPENAI_API_KEY env var)
   * @param init.baseURL - Optional custom base URL for the API
   */
  constructor(init: { apiKey?: string; baseURL?: string } = {}) {
    super();
    this.client = new OpenAI({
      apiKey: init.apiKey,
      baseURL: init.baseURL,
    });
  }

  /**
   * Execute a call to the OpenAI Responses API.
   *
   * @param args - Call arguments
   * @param args.modelId - The OpenAI model ID to use
   * @param args.messages - Array of messages to send
   * @param args.params - Optional additional parameters
   * @returns Response object containing the API response
   */
  protected async _call(args: {
    modelId: string;
    messages: readonly Message[];
    params?: Params;
  }): Promise<Response> {
    const modelIdTyped = args.modelId as OpenAIModelId;
    const requestParams = buildRequestParams(
      modelIdTyped,
      args.messages,
      args.params
    );

    const openaiResponse = await this.client.responses.create(requestParams);

    const includeThoughts = getIncludeThoughts(args.params);

    const { assistantMessage, finishReason, usage } = decodeResponse(
      openaiResponse,
      modelIdTyped,
      includeThoughts
    );

    return new Response({
      raw: openaiResponse,
      providerId: 'openai',
      modelId: modelIdTyped,
      providerModelName: modelName(modelIdTyped, null),
      params: args.params ?? {},
      inputMessages: args.messages,
      assistantMessage,
      finishReason,
      usage,
    });
  }

  /**
   * Extract the HTTP status code from an OpenAI API error.
   *
   * @param e - The error to extract the status from
   * @returns The HTTP status code or undefined if not available
   */
  protected getErrorStatus(e: Error): number | undefined {
    // OpenAI SDK uses 'status' property
    return (e as InstanceType<typeof OpenAI.APIError>).status;
  }
}
