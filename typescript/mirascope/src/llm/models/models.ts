/**
 * @fileoverview Provider-specific model implementations.
 */

import {
  AnthropicClient,
  type AnthropicMessage,
  type AnthropicParams,
  GoogleClient,
  type GoogleMessage,
  type GoogleParams,
  OpenAIClient,
  type OpenAIMessage,
  type OpenAIParams,
} from '../clients';
import { LLM } from './base';

/**
 * The OpenAI-specific implementation of the `LLM` interface.
 */
export class OpenAI extends LLM<OpenAIMessage, OpenAIParams, OpenAIClient> {
  // All functionality inherited from LLM base class
}

/**
 * The Anthropic-specific implementation of the `LLM` interface.
 */
export class Anthropic extends LLM<
  AnthropicMessage,
  AnthropicParams,
  AnthropicClient
> {
  // All functionality inherited from LLM base class
}

/**
 * The Google-specific implementation of the `LLM` interface.
 */
export class Google extends LLM<GoogleMessage, GoogleParams, GoogleClient> {
  // All functionality inherited from LLM base class
}
