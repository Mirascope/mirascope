/**
 * @fileoverview OpenAI client implementation.
 */

import type { ChatCompletionMessageParam } from 'openai/resources';
import type { Message } from '../messages';
import type { BaseParams } from './base';
import type { Response } from '../responses';
import { BaseClient } from './base';
import type { OPENAI_REGISTERED_LLMS } from './register';

export type OpenAIMessage = Message | ChatCompletionMessageParam;

export interface OpenAIParams extends BaseParams {
  // Add any OpenAI-specific parameters here
}

/**
 * The client for the OpenAI LLM model.
 */
export class OpenAIClient extends BaseClient<
  OpenAIMessage,
  OpenAIParams,
  OPENAI_REGISTERED_LLMS
> {
  call(options: {
    model: OPENAI_REGISTERED_LLMS;
    messages: OpenAIMessage[];
    params?: OpenAIParams | null;
  }): Response {
    throw new Error('Not implemented');
  }

  async callAsync(options: {
    model: OPENAI_REGISTERED_LLMS;
    messages: OpenAIMessage[];
    params?: OpenAIParams | null;
  }): Promise<Response> {
    throw new Error('Not implemented');
  }
}
