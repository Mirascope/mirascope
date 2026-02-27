/**
 * OpenRouter provider implementation.
 *
 * OpenRouter provides access to multiple LLM providers via a unified OpenAI-compatible API.
 */

import {
  EMPTY_FEATURE_INFO,
  featureInfoForOpenAIModel,
  type CompletionsModelFeatureInfo,
} from "@/llm/providers/openai/completions/_utils/feature-info";
import { BaseOpenAICompletionsProvider } from "@/llm/providers/openai/completions/base-provider";
import { modelName as openaiModelName } from "@/llm/providers/openai/model-id";

const DEFAULT_BASE_URL = "https://openrouter.ai/api/v1";
const API_KEY_ENV_VAR = "OPENROUTER_API_KEY";

export interface OpenRouterProviderInit {
  apiKey?: string;
  baseURL?: string;
}

/**
 * Provider for OpenRouter's OpenAI-compatible API.
 *
 * Inherits from BaseOpenAICompletionsProvider with OpenRouter-specific configuration:
 * - Uses OpenRouter's API endpoint (https://openrouter.ai/api/v1)
 * - Requires OPENROUTER_API_KEY environment variable
 *
 * @example
 * ```typescript
 * import { registerProvider } from 'mirascope/llm';
 *
 * // Option 1: Use "openrouter/" prefix for explicit OpenRouter models
 * registerProvider('openrouter', { scope: 'openrouter/' });
 *
 * const call = defineCall({
 *   model: 'openrouter/openai/gpt-4o',
 *   fn: () => [user('Hello!')],
 * });
 *
 * // Option 2: Route existing model IDs through OpenRouter
 * registerProvider('openrouter', { scope: ['openai/', 'anthropic/'] });
 *
 * // Now openai/ models go through OpenRouter
 * const call = defineCall({
 *   model: 'openai/gpt-4',
 *   fn: () => [user('Hello!')],
 * });
 * ```
 */
export class OpenRouterProvider extends BaseOpenAICompletionsProvider {
  readonly id = "openrouter" as const;

  /**
   * Create a new OpenRouter provider instance.
   *
   * @param init - Configuration options
   * @param init.apiKey - API key (defaults to OPENROUTER_API_KEY env var)
   * @param init.baseURL - Base URL (defaults to 'https://openrouter.ai/api/v1')
   */
  constructor(init: OpenRouterProviderInit = {}) {
    const resolvedApiKey = init.apiKey ?? process.env[API_KEY_ENV_VAR];
    const resolvedBaseUrl = init.baseURL ?? DEFAULT_BASE_URL;

    super({
      id: "openrouter",
      apiKey: resolvedApiKey,
      baseURL: resolvedBaseUrl,
    });
  }

  /**
   * Strip 'openrouter/' prefix from model ID for OpenRouter API.
   *
   * @param modelId - Full model ID (e.g. "openrouter/openai/gpt-4o")
   * @returns Model ID without openrouter prefix (e.g. "openai/gpt-4o")
   */
  protected override modelName(modelId: string): string {
    return modelId.replace(/^openrouter\//, "");
  }

  /**
   * Return OpenAI feature info for openai/* models, empty info otherwise.
   *
   * This allows OpenRouter to properly handle OpenAI models (including reasoning
   * models like o1/o3) while being permissive for other providers.
   *
   * @param modelId - Full model ID (e.g. "openrouter/openai/gpt-4o")
   * @returns Feature info for the model
   */
  protected override modelFeatureInfo(
    modelId: string,
  ): CompletionsModelFeatureInfo {
    const baseModelId = modelId.replace(/^openrouter\//, "");
    if (baseModelId.startsWith("openai/")) {
      const openaiName = openaiModelName(baseModelId, null);
      return featureInfoForOpenAIModel(openaiName);
    }
    return EMPTY_FEATURE_INFO;
  }
}
