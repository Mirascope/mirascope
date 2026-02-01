/**
 * OpenAI model IDs and related utilities.
 */

import type { OpenAIKnownModels } from "@/llm/providers/openai/model-info";

/**
 * The OpenAI model IDs registered with Mirascope.
 */
export type OpenAIModelId = OpenAIKnownModels | (string & {});

/**
 * API mode for OpenAI requests.
 */
export type ApiMode = "responses" | "completions";

/**
 * Extract the OpenAI model name from the ModelId.
 *
 * @param modelId - Full model ID (e.g. "openai/gpt-4o" or "openai/gpt-4o:responses")
 * @param apiMode - API mode to append as suffix ("responses" or "completions").
 *   If null, no suffix will be added (just the base model name).
 * @returns Provider-specific model ID with API suffix (e.g. "gpt-4o:responses")
 */
export function modelName(
  modelId: OpenAIModelId,
  apiMode: ApiMode | null,
): string {
  const modelPart = modelId.replace(/^openai\//, "");
  const baseName = modelPart
    .replace(/:responses$/, "")
    .replace(/:completions$/, "");

  if (apiMode === null) {
    return baseName;
  }
  return `${baseName}:${apiMode}`;
}
