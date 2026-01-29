/**
 * OpenAI Completions provider implementation.
 */

import OpenAI from 'openai';

import type { Context } from '@/llm/context';
import type { Message } from '@/llm/messages';
import type { Params } from '@/llm/models';
import { BaseProvider } from '@/llm/providers/base';
import type { ToolSchema } from '@/llm/tools';
import { OPENAI_ERROR_MAP } from '@/llm/providers/openai/_utils/errors';
import type { OpenAIModelId } from '@/llm/providers/openai/model-id';
import { modelName } from '@/llm/providers/openai/model-id';
import {
  buildRequestParams,
  decodeResponse,
} from '@/llm/providers/openai/completions/_utils';
import { decodeStream } from '@/llm/providers/openai/completions/decode-stream';
import { Response } from '@/llm/responses';
import { ContextResponse } from '@/llm/responses/context-response';
import { ContextStreamResponse } from '@/llm/responses/context-stream-response';
import { StreamResponse } from '@/llm/responses/stream-response';

/**
 * Provider for the OpenAI Chat Completions API.
 *
 * This provider uses the Chat Completions API (not the Responses API).
 * For the routing provider that selects between APIs, use `OpenAIProvider`.
 *
 * @example
 * ```typescript
 * const provider = new OpenAICompletionsProvider();
 * const response = await provider.call({
 *   modelId: 'openai/gpt-4o',
 *   messages: [user('Hello!')],
 * });
 * console.log(response.text());
 * ```
 */
export class OpenAICompletionsProvider extends BaseProvider {
  readonly id = 'openai' as const;
  protected readonly errorMap = OPENAI_ERROR_MAP;

  private readonly client: OpenAI;

  /**
   * Create a new OpenAI Completions provider instance.
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
   * Execute a call to the OpenAI Chat Completions API.
   *
   * @param args - Call arguments
   * @param args.modelId - The OpenAI model ID to use
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
    const modelIdTyped = args.modelId as OpenAIModelId;
    const requestParams = buildRequestParams(
      modelIdTyped,
      args.messages,
      args.tools,
      args.params
    );

    const openaiResponse =
      await this.client.chat.completions.create(requestParams);

    const { assistantMessage, finishReason, usage } = decodeResponse(
      openaiResponse,
      modelIdTyped
    );

    return new Response({
      raw: openaiResponse,
      providerId: 'openai',
      modelId: modelIdTyped,
      providerModelName: modelName(modelIdTyped, 'completions'),
      params: args.params ?? /* v8 ignore next 1 */ {},
      inputMessages: args.messages,
      assistantMessage,
      finishReason,
      usage,
    });
  }

  /**
   * Execute a streaming call to the OpenAI Chat Completions API.
   *
   * @param args - Call arguments
   * @param args.modelId - The OpenAI model ID to use
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
    const modelIdTyped = args.modelId as OpenAIModelId;
    const requestParams = buildRequestParams(
      modelIdTyped,
      args.messages,
      args.tools,
      args.params
    );

    const stream = await this.client.chat.completions.create({
      ...requestParams,
      stream: true,
      stream_options: { include_usage: true },
    });

    const chunkIterator = decodeStream(stream);

    return new StreamResponse({
      providerId: 'openai',
      modelId: modelIdTyped,
      providerModelName: modelName(modelIdTyped, 'completions'),
      params: args.params ?? /* v8 ignore next 1 */ {},
      inputMessages: args.messages,
      chunkIterator,
    });
  }

  /**
   * Execute a context-aware call to the OpenAI Chat Completions API.
   *
   * NOTE: This implementation intentionally duplicates _call() rather than delegating.
   * When context-aware tools are implemented, this method will diverge to handle
   * passing context to tools during execution. We keep them separate now to make
   * that future change clearer.
   *
   * @param args - Call arguments including context and model
   * @param args.modelId - The OpenAI model ID to use
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
    const modelIdTyped = args.modelId as OpenAIModelId;
    const requestParams = buildRequestParams(
      modelIdTyped,
      args.messages,
      args.tools,
      args.params
    );

    const openaiResponse =
      await this.client.chat.completions.create(requestParams);

    const { assistantMessage, finishReason, usage } = decodeResponse(
      openaiResponse,
      modelIdTyped
    );

    return new ContextResponse({
      raw: openaiResponse,
      providerId: 'openai',
      modelId: modelIdTyped,
      providerModelName: modelName(modelIdTyped, 'completions'),
      params: args.params ?? /* v8 ignore next 1 */ {},
      inputMessages: args.messages,
      assistantMessage,
      finishReason,
      usage,
    });
  }

  /**
   * Execute a context-aware streaming call to the OpenAI Chat Completions API.
   *
   * NOTE: This implementation intentionally duplicates _stream() rather than delegating.
   * When context-aware tools are implemented, this method will diverge to handle
   * passing context to tools during execution. We keep them separate now to make
   * that future change clearer.
   *
   * @param args - Call arguments including context and model
   * @param args.modelId - The OpenAI model ID to use
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
    const modelIdTyped = args.modelId as OpenAIModelId;
    const requestParams = buildRequestParams(
      modelIdTyped,
      args.messages,
      args.tools,
      args.params
    );

    const stream = await this.client.chat.completions.create({
      ...requestParams,
      stream: true,
      stream_options: { include_usage: true },
    });

    const chunkIterator = decodeStream(stream);

    return new ContextStreamResponse({
      providerId: 'openai',
      modelId: modelIdTyped,
      providerModelName: modelName(modelIdTyped, 'completions'),
      params: args.params ?? /* v8 ignore next 1 */ {},
      inputMessages: args.messages,
      chunkIterator,
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
