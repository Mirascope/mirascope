/**
 * Anthropic registered LLM models.
 */

import type { AnthropicKnownModels } from '@/llm/providers/anthropic/model-info';

/**
 * The Anthropic model IDs registered with Mirascope.
 */
export type AnthropicModelId = AnthropicKnownModels | (string & {});

/**
 * Extract the Anthropic model name from the ModelId.
 *
 * @param modelId - Full model ID (e.g. "anthropic/claude-sonnet-4-5" or "anthropic-beta/claude-sonnet-4-5")
 * @returns Provider-specific model ID (e.g. "claude-sonnet-4-5")
 */
export function modelName(modelId: AnthropicModelId): string {
  return modelId.replace(/^anthropic-beta\//, '').replace(/^anthropic\//, '');
}
