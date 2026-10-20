/** API Route provider using its OpenAI-compatible Chat Completions API. */

import {
  EMPTY_FEATURE_INFO,
  featureInfoForOpenAIModel,
  type CompletionsModelFeatureInfo,
} from "@/llm/providers/openai/completions/_utils/feature-info";
import { BaseOpenAICompletionsProvider } from "@/llm/providers/openai/completions/base-provider";

const DEFAULT_BASE_URL = "https://global.api-route.com/v1";
const API_KEY_ENV_VAR = "API_ROUTE_API_KEY";
const OPENAI_MODEL_PREFIXES = ["gpt-", "o1", "o3", "o4"];

export interface APIRouteProviderInit {
  apiKey?: string;
  baseURL?: string;
}

/**
 * Route `api-route/` model IDs to API Route. Only this routing prefix is
 * removed, so upstream vendor prefixes remain part of the API model ID.
 */
export class APIRouteProvider extends BaseOpenAICompletionsProvider {
  readonly id = "api-route" as const;

  constructor(init: APIRouteProviderInit = {}) {
    super({
      id: "api-route",
      apiKey: init.apiKey ?? process.env[API_KEY_ENV_VAR],
      baseURL: init.baseURL ?? DEFAULT_BASE_URL,
    });
  }

  protected override modelName(modelId: string): string {
    return modelId.replace(/^api-route\//, "");
  }

  protected override modelFeatureInfo(
    modelId: string,
  ): CompletionsModelFeatureInfo {
    const name = this.modelName(modelId);
    return OPENAI_MODEL_PREFIXES.some((prefix) => name.startsWith(prefix))
      ? featureInfoForOpenAIModel(name)
      : EMPTY_FEATURE_INFO;
  }
}
