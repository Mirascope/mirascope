/**
 * @fileoverview Google client implementation.
 */

import type { Content, FunctionResponse } from '@google/genai';
import type { Message } from '../messages';
import type { BaseParams } from './base';
import type { Response } from '../responses';
import { BaseClient } from './base';
import type { GOOGLE_REGISTERED_LLMS } from './register';

export type GoogleMessage = Message | Content | FunctionResponse;

export interface GoogleParams extends BaseParams {
  // Add any Google-specific parameters here
}

/**
 * The client for the Google LLM model.
 */
export class GoogleClient extends BaseClient<
  GoogleMessage,
  GoogleParams,
  GOOGLE_REGISTERED_LLMS
> {
  call(args: {
    model: GOOGLE_REGISTERED_LLMS;
    messages: GoogleMessage[];
    params?: GoogleParams | null;
  }): Response {
    throw new Error('Not implemented');
  }

  async callAsync(args: {
    model: GOOGLE_REGISTERED_LLMS;
    messages: GoogleMessage[];
    params?: GoogleParams | null;
  }): Promise<Response> {
    throw new Error('Not implemented');
  }
}
