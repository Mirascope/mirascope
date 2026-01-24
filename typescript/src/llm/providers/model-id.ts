/**
 * Union of all provider model IDs.
 */

import type { AnthropicModelId } from '@/llm/providers/anthropic';
import type { GoogleModelId } from '@/llm/providers/google';
import type { OpenAIModelId } from '@/llm/providers/openai';

/**
 * Model identifier for any supported provider.
 *
 * This is a union of all provider-specific model IDs.
 */
export type ModelId =
  | AnthropicModelId
  | GoogleModelId
  | OpenAIModelId
  | (string & {});
