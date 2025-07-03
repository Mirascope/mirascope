/**
 * @fileoverview Anthropic client implementation.
 */

import type { MessageParam } from '@anthropic-ai/sdk/resources';
import type { Message } from '../messages';
import type { BaseParams } from './base';
import type { Response } from '../responses';
import { BaseClient } from './base';
import type { ANTHROPIC_REGISTERED_LLMS } from './register';

export type AnthropicMessage = Message | MessageParam;

export interface AnthropicParams extends BaseParams {
  // Add any Anthropic-specific parameters here
}

/**
 * The client for the Anthropic LLM model.
 */
export class AnthropicClient extends BaseClient<
  AnthropicMessage,
  AnthropicParams,
  ANTHROPIC_REGISTERED_LLMS
> {
  call(args: {
    model: ANTHROPIC_REGISTERED_LLMS;
    messages: AnthropicMessage[];
    params?: AnthropicParams | null;
  }): Response {
    throw new Error('Not implemented');
  }

  async callAsync(args: {
    model: ANTHROPIC_REGISTERED_LLMS;
    messages: AnthropicMessage[];
    params?: AnthropicParams | null;
  }): Promise<Response> {
    throw new Error('Not implemented');
  }
}
