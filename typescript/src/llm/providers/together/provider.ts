/**
 * Together AI provider implementation.
 *
 * Together AI provides an OpenAI-compatible API for hosted LLM inference.
 */

import { BaseOpenAICompletionsProvider } from '@/llm/providers/openai/completions/base-provider';

const DEFAULT_BASE_URL = 'https://api.together.xyz/v1';
const API_KEY_ENV_VAR = 'TOGETHER_API_KEY';

export interface TogetherProviderInit {
  apiKey?: string;
  baseURL?: string;
}

/**
 * Provider for Together AI's OpenAI-compatible API.
 *
 * Inherits from BaseOpenAICompletionsProvider with Together-specific configuration:
 * - Uses Together AI's API endpoint (https://api.together.xyz/v1)
 * - Requires TOGETHER_API_KEY environment variable
 *
 * @example
 * ```typescript
 * import { registerProvider } from '@mirascope/core/llm';
 *
 * // Register for meta-llama models
 * registerProvider('together', 'meta-llama/');
 *
 * // Now you can use meta-llama models directly
 * const call = defineCall({
 *   model: 'meta-llama/Llama-3.3-70B-Instruct-Turbo',
 *   fn: () => [user('Hello!')],
 * });
 * ```
 */
export class TogetherProvider extends BaseOpenAICompletionsProvider {
  readonly id = 'together' as const;

  /**
   * Create a new Together AI provider instance.
   *
   * @param init - Configuration options
   * @param init.apiKey - API key (defaults to TOGETHER_API_KEY env var)
   * @param init.baseURL - Base URL (defaults to 'https://api.together.xyz/v1')
   */
  constructor(init: TogetherProviderInit = {}) {
    const resolvedApiKey = init.apiKey ?? process.env[API_KEY_ENV_VAR];
    const resolvedBaseUrl = init.baseURL ?? DEFAULT_BASE_URL;

    super({
      id: 'together',
      apiKey: resolvedApiKey,
      baseURL: resolvedBaseUrl,
    });
  }
}
