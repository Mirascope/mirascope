/**
 * Model feature information for OpenAI completions encoding.
 */

import {
  MODELS_WITHOUT_AUDIO_SUPPORT,
  MODELS_WITHOUT_JSON_OBJECT_SUPPORT,
  MODELS_WITHOUT_JSON_SCHEMA_SUPPORT,
  NON_REASONING_MODELS,
} from "@/llm/providers/openai/model-info";

/**
 * Model feature information for OpenAI completions encoding.
 *
 * This interface encapsulates feature detection for OpenAI-compatible models,
 * allowing providers to pass pre-computed feature information rather than
 * relying on model name matching in buildRequestParams.
 *
 * Undefined/null values mean "unknown":
 * - audioSupport: undefined → allow audio (permissive)
 * - strictSupport: undefined → default to tool mode, but allow explicit strict
 * - jsonObjectSupport: undefined → disable (use prompt instructions instead)
 * - isReasoningModel: undefined → treat as false (allow temperature)
 */
export interface CompletionsModelFeatureInfo {
  /** Whether the model supports audio inputs. undefined means skip check (allow). */
  readonly audioSupport?: boolean;

  /** Whether the model supports strict JSON schema. undefined allows explicit strict. */
  readonly strictSupport?: boolean;

  /** Whether the model supports JSON object response format. undefined disables. */
  readonly jsonObjectSupport?: boolean;

  /** Whether the model is a reasoning model. undefined means false (allow temperature). */
  readonly isReasoningModel?: boolean;
}

/**
 * Empty feature info with all values undefined.
 * Used as the default for unknown models (most permissive).
 */
export const EMPTY_FEATURE_INFO: CompletionsModelFeatureInfo = Object.freeze(
  {},
);

/**
 * Get feature info for a base OpenAI model name.
 *
 * @param modelName - The base model name (e.g., "gpt-4o", not "openai/gpt-4o")
 * @returns Feature info with all fields populated based on known model capabilities
 */
export function featureInfoForOpenAIModel(
  modelName: string,
): CompletionsModelFeatureInfo {
  return {
    audioSupport: !MODELS_WITHOUT_AUDIO_SUPPORT.has(modelName),
    strictSupport: !MODELS_WITHOUT_JSON_SCHEMA_SUPPORT.has(modelName),
    jsonObjectSupport: !MODELS_WITHOUT_JSON_OBJECT_SUPPORT.has(modelName),
    isReasoningModel: !NON_REASONING_MODELS.has(modelName),
  };
}
