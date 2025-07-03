/**
 * @fileoverview The base model interfaces for LLM models.
 */

import type { BaseClient, BaseParams } from '../clients/base';
import type { Response } from '../responses';

/**
 * The unified LLM interface that delegates to provider-specific clients.
 *
 * This class provides a consistent interface for interacting with language models
 * from various providers. It handles the common operations like generating responses,
 * streaming, and async variants by delegating to the appropriate client methods.
 */
export class LLM<
  MessageT = any,
  ParamsT extends BaseParams = BaseParams,
  ClientT extends BaseClient<MessageT, ParamsT> = BaseClient<MessageT, ParamsT>,
> {
  /**
   * The provider of the model (e.g., 'google', 'openai', 'anthropic', etc.).
   */
  provider: string;

  /**
   * The name of the model (e.g., 'gpt-4', 'claude-3-5-sonnet', 'gemini-2.5-flash').
   */
  name: string;

  /**
   * The default parameters for the model (temperature, max_tokens, etc.).
   */
  params: ParamsT;

  /**
   * The client object used to interact with the model API.
   */
  client: ClientT;

  /**
   * Initializes a `LLM` instance.
   */
  constructor(options: {
    provider: string;
    name: string;
    params?: ParamsT | null;
    client?: ClientT | null;
  }) {
    this.provider = options.provider;
    this.name = options.name;
    this.params = options.params!; // Will need proper initialization logic
    this.client = options.client!; // Will need proper initialization logic
  }

  /**
   * Standard call for generating responses.
   */
  call(args: {
    messages: MessageT[];
    responseFormat?: null;
    params?: ParamsT | null;
  }): Response {
    // Implementation will delegate to this.client.call()
    throw new Error('Not implemented');
  }

  /**
   * Standard async call for generating responses.
   */
  async callAsync(args: {
    messages: MessageT[];
    responseFormat?: null;
    params?: ParamsT | null;
  }): Promise<Response> {
    // Implementation will delegate to this.client.callAsync()
    throw new Error('Not implemented');
  }
}
