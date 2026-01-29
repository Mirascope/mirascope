/**
 * Anthropic provider implementation with routing between standard and beta APIs.
 */

import Anthropic from '@anthropic-ai/sdk';

import type { Context } from '@/llm/context';
import type { Message } from '@/llm/messages';
import type { Params } from '@/llm/models';
import { BaseProvider } from '@/llm/providers/base';
import type { ToolSchema } from '@/llm/tools';
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
  decodeResponse,
} from '@/llm/providers/anthropic/_utils';
import { decodeStream } from '@/llm/providers/anthropic/decode-stream';
import { AnthropicBetaProvider } from '@/llm/providers/anthropic/beta-provider';

/**
 * Determine whether to use the beta API based on format mode or strict tools.
 *
 * Routes to beta when:
 * - Format mode is "strict" (TODO: not yet supported in TypeScript SDK)
 * - Any tools have strict=True (TODO: not yet supported in TypeScript SDK)
 *
 * @param _modelId - The model identifier (unused until strict mode is implemented)
 * @param _params - The request parameters (unused until strict mode is implemented)
 * @returns Whether to use the beta API
 */
function shouldUseBeta(_modelId: AnthropicModelId, _params?: Params): boolean {
  // TODO: Implement when strict mode format and tools are supported
  // Will check:
  // 1. If format resolves to strict mode
  // 2. If any tools have strict=true
  // 3. If model supports strict structured outputs (not in MODELS_WITHOUT_STRICT_STRUCTURED_OUTPUTS)
  return false;
}

/**
 * Provider for the Anthropic API with intelligent routing between standard and beta APIs.
 *
 * This provider automatically selects the appropriate API based on the request:
 * - Standard API (`client.messages.create()`) for regular requests
 * - Beta API (`client.beta.messages.create()`) for requests requiring strict mode
 *
 * Currently, routing always uses the standard API. Beta API routing will be enabled
 * when strict mode format and tools support is added to the TypeScript SDK.
 *
 * @example
 * ```typescript
 * const provider = new AnthropicProvider();
 * const response = await provider.call({
 *   modelId: 'anthropic/claude-sonnet-4-20250514',
 *   messages: [user('Hello!')],
 * });
 * console.log(response.text());
 * ```
 */
export class AnthropicProvider extends BaseProvider {
  readonly id = 'anthropic' as const;
  protected readonly errorMap = ANTHROPIC_ERROR_MAP;

  private readonly client: Anthropic;
  private readonly betaProvider: AnthropicBetaProvider;

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
    this.betaProvider = new AnthropicBetaProvider(init);
  }

  /**
   * Execute a call to the Anthropic API, routing to beta API if needed.
   *
   * @param args - Call arguments
   * @param args.modelId - The Anthropic model ID to use
   * @param args.messages - Array of messages to send
   * @param args.tools - Optional tools to make available to the model
   * @param args.params - Optional additional parameters
   * @returns Response object containing the API response
   */
  protected async _call(args: {
    modelId: string;
    messages: readonly Message[];
    tools?: readonly ToolSchema[];
    params?: Params;
  }): Promise<Response> {
    const modelId = args.modelId as AnthropicModelId;

    // Route to beta provider for strict mode
    /* v8 ignore start - beta routing not yet implemented */
    if (shouldUseBeta(modelId, args.params)) {
      return this.betaProvider.call({
        modelId: args.modelId,
        messages: args.messages,
        tools: args.tools,
        params: args.params,
      });
    }
    /* v8 ignore stop */

    const requestParams = buildRequestParams(
      modelId,
      args.messages,
      args.tools,
      args.params
    );

    const anthropicResponse = await this.client.messages.create(requestParams);

    const includeThoughts = getIncludeThoughts(args.params);

    const { assistantMessage, finishReason, usage } = decodeResponse(
      anthropicResponse,
      modelId,
      includeThoughts
    );

    return new Response({
      raw: anthropicResponse,
      providerId: 'anthropic',
      modelId,
      providerModelName: modelName(modelId),
      params: args.params ?? /* v8 ignore next 1 */ {},
      inputMessages: args.messages,
      assistantMessage,
      finishReason,
      usage,
    });
  }

  /**
   * Execute a streaming call to the Anthropic API, routing to beta API if needed.
   *
   * @param args - Call arguments
   * @param args.modelId - The Anthropic model ID to use
   * @param args.messages - Array of messages to send
   * @param args.tools - Optional tools to make available to the model
   * @param args.params - Optional additional parameters
   * @returns StreamResponse object for streaming consumption
   */
  protected async _stream(args: {
    modelId: string;
    messages: readonly Message[];
    tools?: readonly ToolSchema[];
    params?: Params;
  }): Promise<StreamResponse> {
    const modelId = args.modelId as AnthropicModelId;

    // Route to beta provider for strict mode
    /* v8 ignore start - beta routing not yet implemented */
    if (shouldUseBeta(modelId, args.params)) {
      return this.betaProvider.stream({
        modelId: args.modelId,
        messages: args.messages,
        tools: args.tools,
        params: args.params,
      });
    }
    /* v8 ignore stop */

    const requestParams = buildRequestParams(
      modelId,
      args.messages,
      args.tools,
      args.params
    );

    const includeThoughts = getIncludeThoughts(args.params);

    const stream = this.client.messages.stream(requestParams);

    const chunkIterator = decodeStream(stream, includeThoughts);

    return new StreamResponse({
      providerId: 'anthropic',
      modelId,
      providerModelName: modelName(modelId),
      params: args.params ?? /* v8 ignore next 1 */ {},
      inputMessages: args.messages,
      chunkIterator,
    });
  }

  /**
   * Execute a context-aware call to the Anthropic API.
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
   * @param args.params - Optional additional parameters
   * @returns ContextResponse object containing the API response
   */
  protected async _contextCall<DepsT>(args: {
    ctx: Context<DepsT>;
    modelId: string;
    messages: readonly Message[];
    tools?: readonly ToolSchema[];
    params?: Params;
  }): Promise<ContextResponse<DepsT>> {
    const modelId = args.modelId as AnthropicModelId;

    // Route to beta provider for strict mode
    /* v8 ignore start - beta routing not yet implemented */
    if (shouldUseBeta(modelId, args.params)) {
      return this.betaProvider.contextCall({
        ctx: args.ctx,
        modelId: args.modelId,
        messages: args.messages,
        tools: args.tools,
        params: args.params,
      });
    }
    /* v8 ignore stop */

    const requestParams = buildRequestParams(
      modelId,
      args.messages,
      args.tools,
      args.params
    );

    const anthropicResponse = await this.client.messages.create(requestParams);

    const includeThoughts = getIncludeThoughts(args.params);

    const { assistantMessage, finishReason, usage } = decodeResponse(
      anthropicResponse,
      modelId,
      includeThoughts
    );

    return new ContextResponse({
      raw: anthropicResponse,
      providerId: 'anthropic',
      modelId,
      providerModelName: modelName(modelId),
      params: args.params ?? /* v8 ignore next 1 */ {},
      inputMessages: args.messages,
      assistantMessage,
      finishReason,
      usage,
    });
  }

  /**
   * Execute a context-aware streaming call to the Anthropic API.
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
   * @param args.params - Optional additional parameters
   * @returns ContextStreamResponse object for streaming consumption
   */
  protected async _contextStream<DepsT>(args: {
    ctx: Context<DepsT>;
    modelId: string;
    messages: readonly Message[];
    tools?: readonly ToolSchema[];
    params?: Params;
  }): Promise<ContextStreamResponse<DepsT>> {
    const modelId = args.modelId as AnthropicModelId;

    // Route to beta provider for strict mode
    /* v8 ignore start - beta routing not yet implemented */
    if (shouldUseBeta(modelId, args.params)) {
      return this.betaProvider.contextStream({
        ctx: args.ctx,
        modelId: args.modelId,
        messages: args.messages,
        tools: args.tools,
        params: args.params,
      });
    }
    /* v8 ignore stop */

    const requestParams = buildRequestParams(
      modelId,
      args.messages,
      args.tools,
      args.params
    );

    const includeThoughts = getIncludeThoughts(args.params);

    const stream = this.client.messages.stream(requestParams);

    const chunkIterator = decodeStream(stream, includeThoughts);

    return new ContextStreamResponse({
      providerId: 'anthropic',
      modelId,
      providerModelName: modelName(modelId),
      params: args.params ?? /* v8 ignore next 1 */ {},
      inputMessages: args.messages,
      chunkIterator,
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
