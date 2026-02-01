/**
 * OpenAI Completions provider implementation.
 */

import {
  BaseOpenAICompletionsProvider,
  type BaseOpenAICompletionsProviderInit,
} from "@/llm/providers/openai/completions/base-provider";
import { modelName } from "@/llm/providers/openai/model-id";

const API_KEY_ENV_VAR = "OPENAI_API_KEY";

/**
 * Provider for the OpenAI Chat Completions API.
 *
 * This provider uses the Chat Completions API (not the Responses API).
 * For the routing provider that selects between APIs, use `OpenAIProvider`.
 *
 * @example
 * ```typescript
 * const provider = new OpenAICompletionsProvider();
 * const response = await provider.call({
 *   modelId: 'openai/gpt-4o',
 *   messages: [user('Hello!')],
 * });
 * console.log(response.text());
 * ```
 */
export class OpenAICompletionsProvider extends BaseOpenAICompletionsProvider {
  readonly id = "openai" as const;

  constructor(init: BaseOpenAICompletionsProviderInit = {}) {
    const resolvedApiKey = init.apiKey ?? process.env[API_KEY_ENV_VAR];
    super({
      id: "openai",
      apiKey: resolvedApiKey,
      baseURL: init.baseURL,
    });
  }

  /**
   * Get the model name for tracking in Response.
   *
   * Returns the model name with :completions suffix for tracking which API was used.
   */
  protected override providerModelName(modelId: string): string {
    return modelName(modelId, "completions");
  }
}
