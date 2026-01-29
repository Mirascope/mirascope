/**
 * OpenAI provider implementation with routing between Completions and Responses APIs.
 */

import OpenAI from 'openai';

import type { Context } from '@/llm/context';
import type { Message } from '@/llm/messages';
import type { Params } from '@/llm/models';
import { BaseProvider } from '@/llm/providers/base';
import type { Tools, ContextTools } from '@/llm/tools';
import { OPENAI_ERROR_MAP } from '@/llm/providers/openai/_utils/errors';
import { OpenAICompletionsProvider } from '@/llm/providers/openai/completions/provider';
import { OpenAIResponsesProvider } from '@/llm/providers/openai/responses/provider';
import type { ApiMode, OpenAIModelId } from '@/llm/providers/openai/model-id';
import { OPENAI_KNOWN_MODELS } from '@/llm/providers/openai/model-info';
import { Response } from '@/llm/responses';
import type { ContextResponse } from '@/llm/responses/context-response';
import type { ContextStreamResponse } from '@/llm/responses/context-stream-response';
import { StreamResponse } from '@/llm/responses/stream-response';

/**
 * Check if messages contain any audio content.
 *
 * Audio content requires the Completions API since Responses API doesn't support it yet.
 */
function hasAudioContent(messages: readonly Message[]): boolean {
  for (const message of messages) {
    if (message.role === 'system') {
      continue;
    }
    for (const part of message.content) {
      if (part.type === 'audio') {
        return true;
      }
    }
  }
  return false;
}

/**
 * Choose between 'responses' or 'completions' API based on model ID and messages.
 *
 * If the user manually specified an API mode (by appending it as a suffix to the model
 * ID), then we use it.
 *
 * Otherwise, we prefer the Responses API where supported (because it has better
 * reasoning support and better prompt caching). However we will use the Completions API
 * if the messages contain any audio content, as audio content is not yet supported in
 * the Responses API.
 *
 * @param modelId - The model identifier
 * @param messages - The messages to send to the LLM
 * @returns Either "responses" or "completions" depending on the model and message content
 */
export function chooseApiMode(
  modelId: OpenAIModelId,
  messages: readonly Message[]
): ApiMode {
  // Check explicit suffix
  if (modelId.endsWith(':completions')) {
    return 'completions';
  }
  if (modelId.endsWith(':responses')) {
    return 'responses';
  }

  // Audio content requires completions API
  if (hasAudioContent(messages)) {
    return 'completions';
  }

  // Prefer responses API when we know it is available
  if (OPENAI_KNOWN_MODELS.has(`${modelId}:responses`)) {
    return 'responses';
  }

  // If we know from testing that the completions API is available, and
  // (implied by above) that responses wasn't, then we should use completions
  if (OPENAI_KNOWN_MODELS.has(`${modelId}:completions`)) {
    return 'completions';
  }

  // If we don't have either :responses or :completions in the known models, it's
  // likely that this is a new model we haven't tested. We default to responses API for
  // openai/ models (on the assumption that they are new models and OpenAI prefers
  // the responses API) but completions for other models (on the assumption that they
  // are other models routing through the OpenAI completions API)
  if (modelId.startsWith('openai/')) {
    return 'responses';
  }

  return 'completions';
}

/**
 * Provider for the OpenAI API with intelligent routing between Completions and Responses APIs.
 *
 * This provider automatically selects the appropriate API based on the model ID and messages:
 * - Model IDs ending with `:completions` force the Chat Completions API
 * - Model IDs ending with `:responses` force the Responses API
 * - Messages with audio content use the Completions API (Responses doesn't support audio)
 * - Known models prefer the Responses API when available
 * - Unknown openai/ models default to Responses API
 * - Other unknown models default to Completions API (for OpenAI-compatible providers)
 *
 * @example
 * ```typescript
 * const provider = new OpenAIProvider();
 *
 * // Smart routing: uses Responses API for known models
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
  private readonly responsesProvider: OpenAIResponsesProvider;

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
    this.responsesProvider = new OpenAIResponsesProvider(init);
  }

  /**
   * Execute a call to the OpenAI API, routing to the appropriate API based on model ID.
   *
   * @param args - Call arguments
   * @param args.modelId - The OpenAI model ID to use (optionally with :completions or :responses suffix)
   * @param args.messages - Array of messages to send
   * @param args.tools - Optional tools to make available to the model
   * @param args.params - Optional additional parameters
   * @returns Response object containing the API response
   */
  protected async _call(args: {
    modelId: string;
    messages: readonly Message[];
    tools?: Tools;
    params?: Params;
  }): Promise<Response> {
    const modelId = args.modelId as OpenAIModelId;
    const apiMode = chooseApiMode(modelId, args.messages);

    if (apiMode === 'responses') {
      // Delegate to the responses provider
      return this.responsesProvider.call({
        modelId: args.modelId,
        messages: args.messages,
        tools: args.tools,
        params: args.params,
      });
    }

    // Delegate to the completions provider
    return this.completionsProvider.call({
      modelId: args.modelId,
      messages: args.messages,
      tools: args.tools,
      params: args.params,
    });
  }

  /**
   * Execute a streaming call to the OpenAI API, routing to the appropriate API based on model ID.
   *
   * @param args - Call arguments
   * @param args.modelId - The OpenAI model ID to use (optionally with :completions or :responses suffix)
   * @param args.messages - Array of messages to send
   * @param args.tools - Optional tools to make available to the model
   * @param args.params - Optional additional parameters
   * @returns StreamResponse object for streaming consumption
   */
  protected async _stream(args: {
    modelId: string;
    messages: readonly Message[];
    tools?: Tools;
    params?: Params;
  }): Promise<StreamResponse> {
    const modelId = args.modelId as OpenAIModelId;
    const apiMode = chooseApiMode(modelId, args.messages);

    if (apiMode === 'responses') {
      return this.responsesProvider.stream({
        modelId: args.modelId,
        messages: args.messages,
        tools: args.tools,
        params: args.params,
      });
    }

    return this.completionsProvider.stream({
      modelId: args.modelId,
      messages: args.messages,
      tools: args.tools,
      params: args.params,
    });
  }

  /**
   * Execute a context-aware call to the OpenAI API, routing to the appropriate API.
   *
   * NOTE: This implementation intentionally duplicates _call() routing logic rather
   * than delegating. When context-aware tools are implemented, this method will
   * diverge to handle passing context to tools during execution. We keep them
   * separate now to make that future change clearer.
   *
   * @param args - Call arguments including context and model
   * @param args.modelId - The OpenAI model ID to use (optionally with :completions or :responses suffix)
   * @param args.messages - Array of messages to send
   * @param args.tools - Optional tools to make available to the model
   * @param args.params - Optional additional parameters
   * @returns ContextResponse object containing the API response
   */
  protected async _contextCall<DepsT>(args: {
    ctx: Context<DepsT>;
    modelId: string;
    messages: readonly Message[];
    tools?: ContextTools<DepsT>;
    params?: Params;
  }): Promise<ContextResponse<DepsT>> {
    const modelId = args.modelId as OpenAIModelId;
    const apiMode = chooseApiMode(modelId, args.messages);

    if (apiMode === 'responses') {
      // Delegate to the responses provider's context call
      return this.responsesProvider.contextCall({
        ctx: args.ctx,
        modelId: args.modelId,
        messages: args.messages,
        tools: args.tools,
        params: args.params,
      });
    }

    // Delegate to the completions provider's context call
    return this.completionsProvider.contextCall({
      ctx: args.ctx,
      modelId: args.modelId,
      messages: args.messages,
      tools: args.tools,
      params: args.params,
    });
  }

  /**
   * Execute a context-aware streaming call to the OpenAI API, routing to the appropriate API.
   *
   * NOTE: This implementation intentionally duplicates _stream() routing logic rather
   * than delegating. When context-aware tools are implemented, this method will
   * diverge to handle passing context to tools during execution. We keep them
   * separate now to make that future change clearer.
   *
   * @param args - Call arguments including context and model
   * @param args.modelId - The OpenAI model ID to use (optionally with :completions or :responses suffix)
   * @param args.messages - Array of messages to send
   * @param args.tools - Optional tools to make available to the model
   * @param args.params - Optional additional parameters
   * @returns ContextStreamResponse object for streaming consumption
   */
  protected async _contextStream<DepsT>(args: {
    ctx: Context<DepsT>;
    modelId: string;
    messages: readonly Message[];
    tools?: ContextTools<DepsT>;
    params?: Params;
  }): Promise<ContextStreamResponse<DepsT>> {
    const modelId = args.modelId as OpenAIModelId;
    const apiMode = chooseApiMode(modelId, args.messages);

    if (apiMode === 'responses') {
      return this.responsesProvider.contextStream({
        ctx: args.ctx,
        modelId: args.modelId,
        messages: args.messages,
        tools: args.tools,
        params: args.params,
      });
    }

    return this.completionsProvider.contextStream({
      ctx: args.ctx,
      modelId: args.modelId,
      messages: args.messages,
      tools: args.tools,
      params: args.params,
    });
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
