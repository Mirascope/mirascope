/**
 * Beta Anthropic provider implementation.
 *
 * Uses the beta API (client.beta.messages.create()) which supports
 * additional features like extended thinking and structured outputs.
 */

import Anthropic from '@anthropic-ai/sdk';

import type { Context } from '@/llm/context';
import type { Format } from '@/llm/formatting';
import type { Message } from '@/llm/messages';
import type { Params } from '@/llm/models';
import { BaseProvider } from '@/llm/providers/base';
import type { Tools, ContextTools } from '@/llm/tools';
import { getIncludeThoughts } from '@/llm/providers/_utils';
import type { AnthropicModelId } from '@/llm/providers/anthropic/model-id';
import { modelName } from '@/llm/providers/anthropic/model-id';
import { Response } from '@/llm/responses';
import { ContextResponse } from '@/llm/responses/context-response';
import { ContextStreamResponse } from '@/llm/responses/context-stream-response';
import { StreamResponse } from '@/llm/responses/stream-response';
import {
  ANTHROPIC_ERROR_MAP,
  buildRequestParams,
} from '@/llm/providers/anthropic/_utils';
import { betaDecodeResponse } from '@/llm/providers/anthropic/beta-decode';
import { decodeBetaStream } from '@/llm/providers/anthropic/beta-decode-stream';

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
   * @param args.tools - Optional tools to make available to the model
   * @param args.format - Optional format for structured output
   * @param args.params - Optional additional parameters
   * @returns Response object containing the API response
   */
  protected async _call(args: {
    modelId: string;
    messages: readonly Message[];
    tools?: Tools;
    format?: Format | null;
    params?: Params;
  }): Promise<Response> {
    const modelId = args.modelId as AnthropicModelId;
    const requestParams = buildRequestParams(
      modelId,
      args.messages,
      args.tools,
      args.format,
      args.params
    );

    // Use beta API instead of standard
    const betaResponse = await this.client.beta.messages.create(requestParams);

    const includeThoughts = getIncludeThoughts(args.params);

    const { assistantMessage, finishReason, usage } = betaDecodeResponse(
      betaResponse,
      modelId,
      includeThoughts
    );

    return new Response({
      raw: betaResponse,
      // Note: providerId is 'anthropic' (not 'anthropic-beta') to match Python SDK
      providerId: 'anthropic',
      modelId,
      providerModelName: modelName(modelId),
      params: args.params ?? /* v8 ignore next 1 */ {},
      format: args.format ?? null,
      inputMessages: args.messages,
      assistantMessage,
      finishReason,
      usage,
    });
  }

  /**
   * Execute a streaming call to the Anthropic Beta API.
   *
   * @param args - Call arguments
   * @param args.modelId - The Anthropic model ID to use
   * @param args.messages - Array of messages to send
   * @param args.tools - Optional tools to make available to the model
   * @param args.format - Optional format for structured output
   * @param args.params - Optional additional parameters
   * @returns StreamResponse object for streaming consumption
   */
  /* v8 ignore start - beta streaming is feature-gated behind shouldUseBeta() */
  protected _stream(args: {
    modelId: string;
    messages: readonly Message[];
    tools?: Tools;
    format?: Format | null;
    params?: Params;
  }): Promise<StreamResponse> {
    const modelId = args.modelId as AnthropicModelId;
    const requestParams = buildRequestParams(
      modelId,
      args.messages,
      args.tools,
      args.format,
      args.params
    );

    const includeThoughts = getIncludeThoughts(args.params);

    const stream = this.client.beta.messages.stream(requestParams);

    const chunkIterator = decodeBetaStream(stream, includeThoughts);

    return Promise.resolve(
      new StreamResponse({
        // Note: providerId is 'anthropic' (not 'anthropic-beta')
        providerId: 'anthropic',
        modelId,
        providerModelName: modelName(modelId),
        params: args.params ?? /* v8 ignore next 1 */ {},
        tools: args.tools,
        format: args.format ?? null,
        inputMessages: args.messages,
        chunkIterator,
      })
    );
  }
  /* v8 ignore stop */

  /**
   * Execute a context-aware call to the Anthropic Beta API.
   *
   * NOTE: This implementation intentionally duplicates _call() rather than delegating.
   * When context-aware tools are implemented, this method will diverge to handle
   * passing context to tools during execution. We keep them separate now to make
   * that future change clearer.
   *
   * @param args - Call arguments including context and model
   * @param args.modelId - The Anthropic model ID to use
   * @param args.messages - Array of messages to send
   * @param args.tools - Optional tools to make available to the model
   * @param args.format - Optional format for structured output
   * @param args.params - Optional additional parameters
   * @returns ContextResponse object containing the API response
   */
  /* v8 ignore start - beta context call is feature-gated behind shouldUseBeta() */
  protected async _contextCall<DepsT>(args: {
    ctx: Context<DepsT>;
    modelId: string;
    messages: readonly Message[];
    tools?: ContextTools<DepsT>;
    format?: Format | null;
    params?: Params;
  }): Promise<ContextResponse<DepsT>> {
    const modelId = args.modelId as AnthropicModelId;
    const requestParams = buildRequestParams(
      modelId,
      args.messages,
      args.tools,
      args.format,
      args.params
    );

    // Use beta API instead of standard
    const betaResponse = await this.client.beta.messages.create(requestParams);

    const includeThoughts = getIncludeThoughts(args.params);

    const { assistantMessage, finishReason, usage } = betaDecodeResponse(
      betaResponse,
      modelId,
      includeThoughts
    );

    return new ContextResponse({
      raw: betaResponse,
      // Note: providerId is 'anthropic' (not 'anthropic-beta') to match Python SDK
      providerId: 'anthropic',
      modelId,
      providerModelName: modelName(modelId),
      params: args.params ?? /* v8 ignore next 1 */ {},
      format: args.format ?? null,
      inputMessages: args.messages,
      assistantMessage,
      finishReason,
      usage,
    });
  }
  /* v8 ignore stop */

  /**
   * Execute a context-aware streaming call to the Anthropic Beta API.
   *
   * NOTE: This implementation intentionally duplicates _stream() rather than delegating.
   * When context-aware tools are implemented, this method will diverge to handle
   * passing context to tools during execution. We keep them separate now to make
   * that future change clearer.
   *
   * @param args - Call arguments including context and model
   * @param args.modelId - The Anthropic model ID to use
   * @param args.messages - Array of messages to send
   * @param args.tools - Optional tools to make available to the model
   * @param args.format - Optional format for structured output
   * @param args.params - Optional additional parameters
   * @returns ContextStreamResponse object for streaming consumption
   */
  /* v8 ignore start - beta context stream is feature-gated behind shouldUseBeta() */
  protected _contextStream<DepsT>(args: {
    ctx: Context<DepsT>;
    modelId: string;
    messages: readonly Message[];
    tools?: ContextTools<DepsT>;
    format?: Format | null;
    params?: Params;
  }): Promise<ContextStreamResponse<DepsT>> {
    const modelId = args.modelId as AnthropicModelId;
    const requestParams = buildRequestParams(
      modelId,
      args.messages,
      args.tools,
      args.format,
      args.params
    );

    const includeThoughts = getIncludeThoughts(args.params);

    const stream = this.client.beta.messages.stream(requestParams);

    const chunkIterator = decodeBetaStream(stream, includeThoughts);

    return Promise.resolve(
      new ContextStreamResponse({
        // Note: providerId is 'anthropic' (not 'anthropic-beta')
        providerId: 'anthropic',
        modelId,
        providerModelName: modelName(modelId),
        params: args.params ?? /* v8 ignore next 1 */ {},
        tools: args.tools,
        format: args.format ?? null,
        inputMessages: args.messages,
        chunkIterator,
      })
    );
  }
  /* v8 ignore stop */

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
