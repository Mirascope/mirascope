/**
 * Ollama provider implementation.
 *
 * Ollama provides an OpenAI-compatible API for local LLM inference.
 */

import { BaseOpenAICompletionsProvider } from "@/llm/providers/openai/completions/base-provider";

const DEFAULT_BASE_URL = "http://localhost:11434/v1/";
const API_KEY_ENV_VAR = "OLLAMA_API_KEY";

export interface OllamaProviderInit {
  apiKey?: string;
  baseURL?: string;
}

/**
 * Provider for Ollama's OpenAI-compatible API.
 *
 * Inherits from BaseOpenAICompletionsProvider with Ollama-specific configuration:
 * - Uses Ollama's local API endpoint (default: http://localhost:11434/v1/)
 * - API key is not required (Ollama ignores API keys)
 * - Supports OLLAMA_BASE_URL environment variable
 *
 * @example
 * ```typescript
 * const provider = new OllamaProvider();
 * const response = await provider.call({
 *   modelId: 'ollama/llama2',
 *   messages: [user('Hello!')],
 * });
 * console.log(response.text());
 * ```
 */
export class OllamaProvider extends BaseOpenAICompletionsProvider {
  readonly id = "ollama" as const;

  /**
   * Create a new Ollama provider instance.
   *
   * @param init - Configuration options
   * @param init.apiKey - API key (defaults to OLLAMA_API_KEY env var, or 'ollama' if not set)
   * @param init.baseURL - Base URL (defaults to OLLAMA_BASE_URL env var, or 'http://localhost:11434/v1/')
   */
  constructor(init: OllamaProviderInit = {}) {
    const resolvedApiKey =
      init.apiKey ?? process.env[API_KEY_ENV_VAR] ?? "ollama";
    const resolvedBaseUrl =
      init.baseURL ?? process.env.OLLAMA_BASE_URL ?? DEFAULT_BASE_URL;

    super({
      id: "ollama",
      apiKey: resolvedApiKey,
      baseURL: resolvedBaseUrl,
    });
  }

  /**
   * Strip 'ollama/' prefix from model ID for Ollama API.
   */
  protected override modelName(modelId: string): string {
    return modelId.startsWith("ollama/") ? modelId.slice(7) : modelId;
  }
}
