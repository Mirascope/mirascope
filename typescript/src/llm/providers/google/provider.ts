/**
 * Google provider implementation.
 */

import { GoogleGenAI, ApiError } from "@google/genai";

import type { Context } from "@/llm/context";
import type { Format } from "@/llm/formatting";
import type { Message } from "@/llm/messages";
import type { Params } from "@/llm/models";
import type { GoogleModelId } from "@/llm/providers/google/model-id";
import type { Tools, ContextTools } from "@/llm/tools";

import { getIncludeThoughts } from "@/llm/providers/_utils";
import { BaseProvider } from "@/llm/providers/base";
import {
  GOOGLE_ERROR_MAP,
  buildRequestParams,
  decodeResponse,
  mapGoogleErrorByStatus,
} from "@/llm/providers/google/_utils";
import { decodeStream } from "@/llm/providers/google/decode-stream";
import { modelName } from "@/llm/providers/google/model-id";
import { Response } from "@/llm/responses";
import { ContextResponse } from "@/llm/responses/context-response";
import { ContextStreamResponse } from "@/llm/responses/context-stream-response";
import { StreamResponse } from "@/llm/responses/stream-response";

/**
 * Provider for the Google Gemini API.
 *
 * @example
 * ```typescript
 * const provider = new GoogleProvider();
 * const response = await provider.call({
 *   modelId: 'gemini-2.0-flash',
 *   messages: [user('Hello!')],
 * });
 * console.log(response.text());
 * ```
 */
export class GoogleProvider extends BaseProvider {
  readonly id = "google" as const;
  protected readonly errorMap = GOOGLE_ERROR_MAP;

  private readonly client: GoogleGenAI;

  /**
   * Create a new Google provider instance.
   *
   * @param init - Configuration options
   * @param init.apiKey - Google API key (defaults to GOOGLE_API_KEY env var)
   * @param init.baseURL - Optional custom base URL for the API
   */
  constructor(init: { apiKey?: string; baseURL?: string } = {}) {
    super();
    this.client = new GoogleGenAI({
      apiKey: init.apiKey,
      httpOptions: init.baseURL
        ? {
            baseUrl: init.baseURL,
            headers: { Authorization: `Bearer ${init.apiKey}` },
          }
        : undefined,
    });
  }

  /**
   * Execute a call to the Google Gemini API.
   *
   * @param args - Call arguments
   * @param args.modelId - The Google model ID to use
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
    const modelId = args.modelId as GoogleModelId;
    const requestParams = buildRequestParams(
      modelId,
      args.messages,
      args.tools,
      args.format,
      args.params,
    );

    const googleResponse =
      await this.client.models.generateContent(requestParams);

    const includeThoughts = getIncludeThoughts(args.params);

    const { assistantMessage, finishReason, usage } = decodeResponse(
      googleResponse,
      modelId,
      includeThoughts,
    );

    return new Response({
      raw: googleResponse,
      providerId: "google",
      modelId,
      providerModelName: modelName(modelId),
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
   * Execute a streaming call to the Google Gemini API.
   *
   * @param args - Call arguments
   * @param args.modelId - The Google model ID to use
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
    const modelId = args.modelId as GoogleModelId;
    const requestParams = buildRequestParams(
      modelId,
      args.messages,
      args.tools,
      args.format,
      args.params,
    );

    const includeThoughts = getIncludeThoughts(args.params);

    const stream =
      await this.client.models.generateContentStream(requestParams);

    const chunkIterator = decodeStream(stream, includeThoughts);

    return new StreamResponse({
      providerId: "google",
      modelId,
      providerModelName: modelName(modelId),
      params: args.params ?? /* v8 ignore next 1 */ {},
      tools: args.tools,
      format: args.format,
      inputMessages: args.messages,
      chunkIterator,
    });
  }

  /**
   * Execute a context-aware call to the Google Gemini API.
   *
   * NOTE: This implementation intentionally duplicates _call() rather than delegating.
   * When context-aware tools are implemented, this method will diverge to handle
   * passing context to tools during execution. We keep them separate now to make
   * that future change clearer.
   *
   * @param args - Call arguments including context and model
   * @param args.modelId - The Google model ID to use
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
    const modelId = args.modelId as GoogleModelId;
    const requestParams = buildRequestParams(
      modelId,
      args.messages,
      args.tools,
      args.format,
      args.params,
    );

    const googleResponse =
      await this.client.models.generateContent(requestParams);

    const includeThoughts = getIncludeThoughts(args.params);

    const { assistantMessage, finishReason, usage } = decodeResponse(
      googleResponse,
      modelId,
      includeThoughts,
    );

    return new ContextResponse({
      raw: googleResponse,
      providerId: "google",
      modelId,
      providerModelName: modelName(modelId),
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
   * Execute a context-aware streaming call to the Google Gemini API.
   *
   * NOTE: This implementation intentionally duplicates _stream() rather than delegating.
   * When context-aware tools are implemented, this method will diverge to handle
   * passing context to tools during execution. We keep them separate now to make
   * that future change clearer.
   *
   * @param args - Call arguments including context and model
   * @param args.modelId - The Google model ID to use
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
    const modelId = args.modelId as GoogleModelId;
    const requestParams = buildRequestParams(
      modelId,
      args.messages,
      args.tools,
      args.format,
      args.params,
    );

    const includeThoughts = getIncludeThoughts(args.params);

    const stream =
      await this.client.models.generateContentStream(requestParams);

    const chunkIterator = decodeStream(stream, includeThoughts);

    return new ContextStreamResponse({
      providerId: "google",
      modelId,
      providerModelName: modelName(modelId),
      params: args.params ?? /* v8 ignore next 1 */ {},
      tools: args.tools,
      format: args.format,
      inputMessages: args.messages,
      chunkIterator,
    });
  }

  /**
   * Extract the HTTP status code from a Google API error.
   *
   * @param e - The error to extract the status from
   * @returns The HTTP status code or undefined if not available
   */
  /* v8 ignore next 4 - only used by base class wrapError which we override */
  protected getErrorStatus(e: Error): number | undefined {
    // Google SDK uses 'status' property
    return (e as InstanceType<typeof ApiError>).status;
  }

  /**
   * Wrap an error with provider-specific error handling.
   *
   * Maps Google ApiError instances to specific Mirascope error types
   * based on the HTTP status code.
   *
   * @param e - The error to wrap
   * @returns A Mirascope error instance
   */
  protected override wrapError(e: unknown): Error {
    if (e instanceof ApiError) {
      const ErrorClass = mapGoogleErrorByStatus(e.status);
      return new ErrorClass(e.message, {
        provider: this.id,
        statusCode: e.status,
        originalException: e,
      });
    }
    return super.wrapError(e);
  }
}
