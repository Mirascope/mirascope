/**
 * Base abstract interface for provider clients.
 */

import type { Context } from "@/llm/context";
import type { Format } from "@/llm/formatting";
import type { Message, UserContent } from "@/llm/messages";
import type { Params } from "@/llm/models";
import type { ProviderId } from "@/llm/providers/provider-id";
import type { StreamResponseChunk } from "@/llm/responses/chunks";
import type { RootResponse } from "@/llm/responses/root-response";
import type {
  Tools,
  ContextTools,
  BaseTool,
  AnyContextTool,
} from "@/llm/tools";

import {
  APIError,
  ProviderError,
  type APIErrorOptions,
  type ProviderErrorOptions,
} from "@/llm/exceptions";
import { user } from "@/llm/messages";
import { Response } from "@/llm/responses";
import { ContextResponse } from "@/llm/responses/context-response";
import { ContextStreamResponse } from "@/llm/responses/context-stream-response";
import { StreamResponse } from "@/llm/responses/stream-response";

/**
 * A Mirascope error class constructor.
 */
export type MirascopeErrorClass =
  | (new (message: string, options: ProviderErrorOptions) => ProviderError)
  | (new (message: string, options: APIErrorOptions) => APIError);

/**
 * Mapping from provider SDK exception types to Mirascope error classes.
 */
export type ProviderErrorMap = Array<
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  [new (...args: any[]) => Error, MirascopeErrorClass]
>;

/**
 * Base abstract provider for LLM interactions.
 *
 * This class defines the interface for provider implementations.
 * Each provider (Anthropic, OpenAI, etc.) extends this class.
 */
export abstract class BaseProvider {
  /**
   * Provider identifier (e.g., "anthropic", "openai").
   */
  abstract readonly id: ProviderId;

  /**
   * Mapping from provider SDK exceptions to Mirascope error types.
   */
  protected abstract readonly errorMap: ProviderErrorMap;

  /**
   * Generate a Response by calling this provider's LLM.
   *
   * This method wraps the provider-specific implementation with error handling,
   * converting provider SDK exceptions to Mirascope error types.
   */
  async call(args: {
    modelId: string;
    messages: readonly Message[];
    tools?: Tools;
    format?: Format | null;
    params?: Params;
  }): Promise<Response> {
    try {
      return await this._call(args);
    } catch (e) {
      throw this.wrapError(e);
    }
  }

  /**
   * Provider-specific implementation of call().
   *
   * Subclasses implement this method to handle the actual API call.
   */
  protected abstract _call(args: {
    modelId: string;
    messages: readonly Message[];
    tools?: Tools;
    format?: Format | null;
    params?: Params;
  }): Promise<Response>;

  /**
   * Generate a StreamResponse by calling this provider's LLM with streaming.
   *
   * This method wraps the provider-specific implementation with error handling,
   * converting provider SDK exceptions to Mirascope error types. It also wraps
   * the chunk iterator to catch errors during iteration (not just initial call).
   */
  async stream(args: {
    modelId: string;
    messages: readonly Message[];
    tools?: Tools;
    format?: Format | null;
    params?: Params;
  }): Promise<StreamResponse> {
    let response: StreamResponse;
    try {
      response = await this._stream(args);
    } catch (e) {
      throw this.wrapError(e);
    }

    // Wrap the iterator to catch errors during iteration
    response.wrapChunkIterator((iterator) =>
      this._wrapIteratorErrors(iterator),
    );

    return response;
  }

  /**
   * Wrap an async iterator to catch errors during iteration.
   * Converts provider SDK exceptions to Mirascope error types.
   */
  private async *_wrapIteratorErrors(
    iterator: AsyncIterator<StreamResponseChunk>,
  ): AsyncGenerator<StreamResponseChunk> {
    try {
      let result = await iterator.next();
      while (!result.done) {
        yield result.value;
        result = await iterator.next();
      }
    } catch (e) {
      throw this.wrapError(e);
    }
  }

  /**
   * Provider-specific implementation of stream().
   *
   * Subclasses implement this method to handle the actual streaming API call.
   */
  protected abstract _stream(args: {
    modelId: string;
    messages: readonly Message[];
    tools?: Tools;
    format?: Format | null;
    params?: Params;
  }): Promise<StreamResponse>;

  /**
   * Generate a ContextResponse by calling this provider's LLM with context.
   *
   * This method accepts a context for dependency injection, enabling context-aware
   * tools and prompts.
   *
   * @template DepsT - The type of dependencies in the context.
   */
  async contextCall<DepsT>(args: {
    ctx: Context<DepsT>;
    modelId: string;
    messages: readonly Message[];
    tools?: ContextTools<DepsT>;
    format?: Format | null;
    params?: Params;
  }): Promise<ContextResponse<DepsT>> {
    try {
      return await this._contextCall(args);
    } catch (e) {
      throw this.wrapError(e);
    }
  }

  /**
   * Provider-specific implementation of contextCall().
   *
   * Subclasses implement this method to handle the actual API call with context.
   * Currently functionally equivalent to _call() since context-aware tools are
   * not yet implemented. When context-aware tools are added, this method will
   * handle passing context to tools during execution.
   */
  protected abstract _contextCall<DepsT>(args: {
    ctx: Context<DepsT>;
    modelId: string;
    messages: readonly Message[];
    tools?: ContextTools<DepsT>;
    format?: Format | null;
    params?: Params;
  }): Promise<ContextResponse<DepsT>>;

  /**
   * Generate a ContextStreamResponse by calling this provider's LLM with context and streaming.
   *
   * This method accepts a context for dependency injection, enabling context-aware
   * tools and prompts.
   *
   * @template DepsT - The type of dependencies in the context.
   */
  async contextStream<DepsT>(args: {
    ctx: Context<DepsT>;
    modelId: string;
    messages: readonly Message[];
    tools?: ContextTools<DepsT>;
    format?: Format | null;
    params?: Params;
  }): Promise<ContextStreamResponse<DepsT>> {
    let response: ContextStreamResponse<DepsT>;
    try {
      response = await this._contextStream(args);
    } catch (e) {
      throw this.wrapError(e);
    }

    // Wrap the iterator to catch errors during iteration
    response.wrapChunkIterator((iterator) =>
      this._wrapIteratorErrors(iterator),
    );

    return response;
  }

  /**
   * Provider-specific implementation of contextStream().
   *
   * Subclasses implement this method to handle the actual streaming API call with context.
   * Currently functionally equivalent to _stream() since context-aware tools are
   * not yet implemented. When context-aware tools are added, this method will
   * handle passing context to tools during execution.
   */
  protected abstract _contextStream<DepsT>(args: {
    ctx: Context<DepsT>;
    modelId: string;
    messages: readonly Message[];
    tools?: ContextTools<DepsT>;
    format?: Format | null;
    params?: Params;
  }): Promise<ContextStreamResponse<DepsT>>;

  // ===== Resume Methods =====

  /**
   * Generate a new Response by extending a previous response's messages with additional user content.
   *
   * Uses the previous response's tools and output format. The default implementation
   * appends a user message and delegates to call().
   *
   * @param args.modelId - The model ID to use.
   * @param args.response - The previous response to extend.
   * @param args.content - The new user content to append.
   * @param args.params - Optional parameters for the request.
   * @returns A new Response containing the extended conversation.
   */
  async resume(args: {
    modelId: string;
    response: RootResponse;
    content: UserContent;
    params?: Params;
  }): Promise<Response> {
    const messages = [...args.response.messages, user(args.content)];
    const tools = (args.response as { toolkit?: { tools: BaseTool[] } }).toolkit
      ?.tools;
    const format = args.response.format;
    return this.call({
      modelId: args.modelId,
      messages,
      params: args.params,
      tools,
      format,
    });
  }

  /**
   * Generate a new StreamResponse by extending a previous response's messages with additional user content.
   *
   * Uses the previous response's tools and output format. The default implementation
   * appends a user message and delegates to stream().
   *
   * @param args.modelId - The model ID to use.
   * @param args.response - The previous response to extend.
   * @param args.content - The new user content to append.
   * @param args.params - Optional parameters for the request.
   * @returns A new StreamResponse for consuming the extended conversation.
   */
  async resumeStream(args: {
    modelId: string;
    response: RootResponse;
    content: UserContent;
    params?: Params;
  }): Promise<StreamResponse> {
    const messages = [...args.response.messages, user(args.content)];
    const tools = (args.response as { toolkit?: { tools: BaseTool[] } }).toolkit
      ?.tools;
    const format = args.response.format;
    return this.stream({
      modelId: args.modelId,
      messages,
      tools,
      format,
      params: args.params,
    });
  }

  /**
   * Generate a new ContextResponse by extending a previous response's messages with additional user content.
   *
   * Uses the previous response's tools and output format. The default implementation
   * appends a user message and delegates to contextCall().
   *
   * @template DepsT - The type of dependencies in the context.
   * @param args.ctx - The context containing dependencies for tools.
   * @param args.modelId - The model ID to use.
   * @param args.response - The previous response to extend.
   * @param args.content - The new user content to append.
   * @param args.params - Optional parameters for the request.
   * @returns A new ContextResponse containing the extended conversation.
   */
  async contextResume<DepsT>(args: {
    ctx: Context<DepsT>;
    modelId: string;
    response: RootResponse;
    content: UserContent;
    params?: Params;
  }): Promise<ContextResponse<DepsT>> {
    const messages = [...args.response.messages, user(args.content)];
    const tools = (
      args.response as { toolkit?: { tools: AnyContextTool<DepsT>[] } }
    ).toolkit?.tools;
    const format = args.response.format;
    return this.contextCall({
      ctx: args.ctx,
      modelId: args.modelId,
      messages,
      tools,
      format,
      params: args.params,
    });
  }

  /**
   * Generate a new ContextStreamResponse by extending a previous response's messages with additional user content.
   *
   * Uses the previous response's tools and output format. The default implementation
   * appends a user message and delegates to contextStream().
   *
   * @template DepsT - The type of dependencies in the context.
   * @param args.ctx - The context containing dependencies for tools.
   * @param args.modelId - The model ID to use.
   * @param args.response - The previous response to extend.
   * @param args.content - The new user content to append.
   * @param args.params - Optional parameters for the request.
   * @returns A new ContextStreamResponse for consuming the extended conversation.
   */
  async contextResumeStream<DepsT>(args: {
    ctx: Context<DepsT>;
    modelId: string;
    response: RootResponse;
    content: UserContent;
    params?: Params;
  }): Promise<ContextStreamResponse<DepsT>> {
    const messages = [...args.response.messages, user(args.content)];
    const tools = (
      args.response as { toolkit?: { tools: AnyContextTool<DepsT>[] } }
    ).toolkit?.tools;
    const format = args.response.format;
    return this.contextStream({
      ctx: args.ctx,
      modelId: args.modelId,
      messages,
      tools,
      format,
      params: args.params,
    });
  }

  /**
   * Wrap a provider SDK exception in the appropriate Mirascope error type.
   */
  protected wrapError(e: unknown): Error {
    if (!(e instanceof Error)) {
      return new Error(String(e));
    }

    // Walk through error map to find matching error type
    for (const [ErrorClass, MirascopeErrorClass] of this.errorMap) {
      if (e instanceof ErrorClass) {
        const statusCode = this.getErrorStatus(e);

        // Check if this is an APIError subclass (has statusCode)
        if (MirascopeErrorClass.prototype instanceof APIError) {
          return new (MirascopeErrorClass as new (
            message: string,
            options: APIErrorOptions,
          ) => APIError)(e.message, {
            provider: this.id,
            statusCode,
            originalException: e,
          });
        }

        return new MirascopeErrorClass(e.message, {
          provider: this.id,
          originalException: e,
        });
      }
    }

    // Not in error map - return as-is
    return e;
  }

  /**
   * Extract HTTP status code from provider-specific exception.
   *
   * Different SDKs store status codes differently (e.g., .status_code vs .code).
   * Each provider implements this to handle their SDK's convention.
   *
   * @param e - The exception to extract status code from.
   * @returns The HTTP status code if available, undefined otherwise.
   */
  protected abstract getErrorStatus(e: Error): number | undefined;
}

/**
 * Type alias for any provider instance.
 * Equivalent to Python's `Provider = BaseProvider[Any]`.
 */
export type Provider = BaseProvider;
