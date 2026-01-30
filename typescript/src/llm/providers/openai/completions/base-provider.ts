/**
 * Base class for OpenAI Completions-compatible providers.
 *
 * This base class contains all the logic for calling OpenAI-compatible APIs.
 * Subclasses (OpenAICompletionsProvider, OllamaProvider, etc.) extend this
 * and provide their specific configuration.
 */

import OpenAI from 'openai';

import type { Context } from '@/llm/context';
import type { Format } from '@/llm/formatting';
import type { Message } from '@/llm/messages';
import type { Params } from '@/llm/models';
import { BaseProvider } from '@/llm/providers/base';
import type { Tools, ContextTools } from '@/llm/tools';
import { OPENAI_ERROR_MAP } from '@/llm/providers/openai/_utils/errors';
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
 * Configuration for initializing an OpenAI-compatible provider.
 */
export interface BaseOpenAICompletionsProviderInit {
  apiKey?: string;
  baseURL?: string;
}

/**
 * Internal configuration passed from subclass to base class.
 */
interface BaseOpenAICompletionsProviderConfig {
  /** The provider identifier */
  id: string;
  /** Resolved API key */
  apiKey: string | undefined;
  /** Resolved base URL */
  baseURL: string | undefined;
}

/**
 * Base class for providers that use OpenAI Completions-compatible APIs.
 *
 * Subclasses must:
 * - Set `id` as a readonly property
 * - Override `resolveConfig()` to provide API key and base URL resolution
 * - Optionally override `modelName()` to extract model name from model ID
 * - Optionally override `providerModelName()` for Response tracking
 */
export abstract class BaseOpenAICompletionsProvider extends BaseProvider {
  abstract readonly id: string;
  protected readonly errorMap = OPENAI_ERROR_MAP;
  protected readonly client: OpenAI;

  constructor(config: BaseOpenAICompletionsProviderConfig) {
    super();

    // If base URL is set but no API key, use placeholder
    let effectiveApiKey = config.apiKey;
    /* v8 ignore start - tested via E2E with custom base URLs */
    if (config.baseURL !== undefined && !effectiveApiKey) {
      effectiveApiKey = 'not-needed';
    }
    /* v8 ignore stop */

    this.client = new OpenAI({
      apiKey: effectiveApiKey,
      baseURL: config.baseURL,
    });
  }

  /**
   * Extract the model name to send to the API.
   * Override in subclasses to strip provider-specific prefixes.
   */
  protected modelName(modelId: string): string {
    return modelId;
  }

  /**
   * Get the model name for tracking in Response.
   * Override in subclasses for custom tracking names.
   */
  /* v8 ignore start - default used by subclasses, tested via E2E */
  protected providerModelName(modelId: string): string {
    return this.modelName(modelId);
  }
  /* v8 ignore stop */

  /**
   * Execute a call to the OpenAI-compatible API.
   */
  protected async _call(args: {
    modelId: string;
    messages: readonly Message[];
    tools?: Tools;
    format?: Format | null;
    params?: Params;
  }): Promise<Response> {
    const apiModelName = this.modelName(args.modelId);
    const requestParams = buildRequestParams(
      apiModelName,
      args.messages,
      args.tools,
      args.params
    );

    const openaiResponse =
      await this.client.chat.completions.create(requestParams);

    const { assistantMessage, finishReason, usage } = decodeResponse(
      openaiResponse,
      apiModelName
    );

    return new Response({
      raw: openaiResponse,
      providerId: this.id,
      modelId: args.modelId,
      providerModelName: this.providerModelName(args.modelId),
      params: args.params ?? {},
      tools: args.tools,
      format: args.format,
      inputMessages: args.messages,
      assistantMessage,
      finishReason,
      usage,
    });
  }

  /**
   * Execute a streaming call to the OpenAI-compatible API.
   */
  protected async _stream(args: {
    modelId: string;
    messages: readonly Message[];
    tools?: Tools;
    format?: Format | null;
    params?: Params;
  }): Promise<StreamResponse> {
    const apiModelName = this.modelName(args.modelId);
    const requestParams = buildRequestParams(
      apiModelName,
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
      providerId: this.id,
      modelId: args.modelId,
      providerModelName: this.providerModelName(args.modelId),
      params: args.params ?? /* v8 ignore next */ {},
      tools: args.tools,
      format: args.format,
      inputMessages: args.messages,
      chunkIterator,
    });
  }

  /**
   * Execute a context-aware call to the OpenAI-compatible API.
   */
  protected async _contextCall<DepsT>(args: {
    ctx: Context<DepsT>;
    modelId: string;
    messages: readonly Message[];
    tools?: ContextTools<DepsT>;
    format?: Format | null;
    params?: Params;
  }): Promise<ContextResponse<DepsT>> {
    const apiModelName = this.modelName(args.modelId);
    const requestParams = buildRequestParams(
      apiModelName,
      args.messages,
      args.tools,
      args.params
    );

    const openaiResponse =
      await this.client.chat.completions.create(requestParams);

    const { assistantMessage, finishReason, usage } = decodeResponse(
      openaiResponse,
      apiModelName
    );

    return new ContextResponse({
      raw: openaiResponse,
      providerId: this.id,
      modelId: args.modelId,
      providerModelName: this.providerModelName(args.modelId),
      params: args.params ?? /* v8 ignore next */ {},
      tools: args.tools,
      format: args.format,
      inputMessages: args.messages,
      assistantMessage,
      finishReason,
      usage,
    });
  }

  /**
   * Execute a context-aware streaming call to the OpenAI-compatible API.
   */
  protected async _contextStream<DepsT>(args: {
    ctx: Context<DepsT>;
    modelId: string;
    messages: readonly Message[];
    tools?: ContextTools<DepsT>;
    format?: Format | null;
    params?: Params;
  }): Promise<ContextStreamResponse<DepsT>> {
    const apiModelName = this.modelName(args.modelId);
    const requestParams = buildRequestParams(
      apiModelName,
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
      providerId: this.id,
      modelId: args.modelId,
      providerModelName: this.providerModelName(args.modelId),
      params: args.params ?? /* v8 ignore next */ {},
      tools: args.tools,
      format: args.format,
      inputMessages: args.messages,
      chunkIterator,
    });
  }

  /**
   * Extract the HTTP status code from an OpenAI API error.
   */
  protected getErrorStatus(e: Error): number | undefined {
    return (e as InstanceType<typeof OpenAI.APIError>).status;
  }
}
