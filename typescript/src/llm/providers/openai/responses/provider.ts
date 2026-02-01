/**
 * OpenAI Responses provider implementation.
 */

import OpenAI from "openai";

import type { Context } from "@/llm/context";
import type { Format } from "@/llm/formatting";
import type { Message } from "@/llm/messages";
import type { Params } from "@/llm/models";
import type { OpenAIModelId } from "@/llm/providers/openai/model-id";
import type { Tools, ContextTools } from "@/llm/tools";

import { getIncludeThoughts } from "@/llm/providers/_utils";
import { BaseProvider } from "@/llm/providers/base";
import { OPENAI_ERROR_MAP } from "@/llm/providers/openai/_utils/errors";
import { modelName } from "@/llm/providers/openai/model-id";
import {
  buildRequestParams,
  decodeResponse,
} from "@/llm/providers/openai/responses/_utils";
import { decodeStream } from "@/llm/providers/openai/responses/decode-stream";
import { Response } from "@/llm/responses";
import { ContextResponse } from "@/llm/responses/context-response";
import { ContextStreamResponse } from "@/llm/responses/context-stream-response";
import { StreamResponse } from "@/llm/responses/stream-response";

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
  readonly id = "openai" as const;
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
    const modelIdTyped = args.modelId as OpenAIModelId;
    const requestParams = buildRequestParams(
      modelIdTyped,
      args.messages,
      args.tools,
      args.params,
    );

    const openaiResponse = await this.client.responses.create(requestParams);

    const includeThoughts = getIncludeThoughts(args.params);

    const { assistantMessage, finishReason, usage } = decodeResponse(
      openaiResponse,
      modelIdTyped,
      includeThoughts,
    );

    return new Response({
      raw: openaiResponse,
      providerId: "openai",
      modelId: modelIdTyped,
      providerModelName: modelName(modelIdTyped, "responses"),
      params: args.params ?? /* v8 ignore next 1 */ {},
      tools: args.tools,
      format: args.format,
      inputMessages: args.messages,
      assistantMessage,
      finishReason,
      usage,
    });
  }

  /**
   * Execute a streaming call to the OpenAI Responses API.
   *
   * @param args - Call arguments
   * @param args.modelId - The OpenAI model ID to use
   * @param args.messages - Array of messages to send
   * @param args.tools - Optional tools to make available to the model
   * @param args.format - Optional format for structured output
   * @param args.params - Optional additional parameters
   * @returns StreamResponse object for streaming consumption
   */
  protected async _stream(args: {
    modelId: string;
    messages: readonly Message[];
    tools?: Tools;
    format?: Format | null;
    params?: Params;
  }): Promise<StreamResponse> {
    const modelIdTyped = args.modelId as OpenAIModelId;
    const requestParams = buildRequestParams(
      modelIdTyped,
      args.messages,
      args.tools,
      args.params,
    );

    const includeThoughts = getIncludeThoughts(args.params);

    const stream = await this.client.responses.create({
      ...requestParams,
      stream: true,
    });

    const chunkIterator = decodeStream(stream, includeThoughts);

    return new StreamResponse({
      providerId: "openai",
      modelId: modelIdTyped,
      providerModelName: modelName(modelIdTyped, "responses"),
      params: args.params ?? /* v8 ignore next 1 */ {},
      tools: args.tools,
      format: args.format,
      inputMessages: args.messages,
      chunkIterator,
    });
  }

  /**
   * Execute a context-aware call to the OpenAI Responses API.
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
   * @param args.format - Optional format for structured output
   * @param args.params - Optional additional parameters
   * @returns ContextResponse object containing the API response
   */
  protected async _contextCall<DepsT>(args: {
    ctx: Context<DepsT>;
    modelId: string;
    messages: readonly Message[];
    tools?: ContextTools<DepsT>;
    format?: Format | null;
    params?: Params;
  }): Promise<ContextResponse<DepsT>> {
    const modelIdTyped = args.modelId as OpenAIModelId;
    const requestParams = buildRequestParams(
      modelIdTyped,
      args.messages,
      args.tools,
      args.params,
    );

    const openaiResponse = await this.client.responses.create(requestParams);

    const includeThoughts = getIncludeThoughts(args.params);

    const { assistantMessage, finishReason, usage } = decodeResponse(
      openaiResponse,
      modelIdTyped,
      includeThoughts,
    );

    return new ContextResponse({
      raw: openaiResponse,
      providerId: "openai",
      modelId: modelIdTyped,
      providerModelName: modelName(modelIdTyped, "responses"),
      params: args.params ?? /* v8 ignore next 1 */ {},
      tools: args.tools,
      format: args.format,
      inputMessages: args.messages,
      assistantMessage,
      finishReason,
      usage,
    });
  }

  /**
   * Execute a context-aware streaming call to the OpenAI Responses API.
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
   * @param args.format - Optional format for structured output
   * @param args.params - Optional additional parameters
   * @returns ContextStreamResponse object for streaming consumption
   */
  protected async _contextStream<DepsT>(args: {
    ctx: Context<DepsT>;
    modelId: string;
    messages: readonly Message[];
    tools?: ContextTools<DepsT>;
    format?: Format | null;
    params?: Params;
  }): Promise<ContextStreamResponse<DepsT>> {
    const modelIdTyped = args.modelId as OpenAIModelId;
    const requestParams = buildRequestParams(
      modelIdTyped,
      args.messages,
      args.tools,
      args.params,
    );

    const includeThoughts = getIncludeThoughts(args.params);

    const stream = await this.client.responses.create({
      ...requestParams,
      stream: true,
    });

    const chunkIterator = decodeStream(stream, includeThoughts);

    return new ContextStreamResponse({
      providerId: "openai",
      modelId: modelIdTyped,
      providerModelName: modelName(modelIdTyped, "responses"),
      params: args.params ?? /* v8 ignore next 1 */ {},
      tools: args.tools,
      format: args.format,
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
