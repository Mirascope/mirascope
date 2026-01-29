/**
 * Google registered LLM models.
 */

import type { GoogleKnownModels } from '@/llm/providers/google/model-info';

/**
 * The Google model IDs registered with Mirascope.
 */
export type GoogleModelId = GoogleKnownModels | (string & {});

/**
 * Extract the Google model name from the ModelId.
 *
 * @param modelId - Full model ID (e.g. "google/gemini-2.5-flash")
 * @returns Provider-specific model ID (e.g. "gemini-2.5-flash")
 */
export function modelName(modelId: GoogleModelId): string {
  return modelId.replace(/^google\//, '');
}
