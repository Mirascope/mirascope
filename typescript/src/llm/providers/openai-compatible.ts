/** OpenAI-compatible providers supported by the Python SDK. */

import {
  EMPTY_FEATURE_INFO,
  featureInfoForOpenAIModel,
  type CompletionsModelFeatureInfo,
} from "@/llm/providers/openai/completions/_utils/feature-info";
import { BaseOpenAICompletionsProvider } from "@/llm/providers/openai/completions/base-provider";
import { modelName as openaiModelName } from "@/llm/providers/openai/model-id";

interface ProviderInit {
  apiKey?: string;
  baseURL?: string;
}

abstract class CompatibleProvider extends BaseOpenAICompletionsProvider {
  abstract readonly id: string;

  protected constructor(
    id: string,
    envVar: string,
    baseURL: string,
    init: ProviderInit,
  ) {
    super({
      id,
      apiKey: init.apiKey ?? process.env[envVar],
      baseURL: init.baseURL ?? baseURL,
    });
  }

  protected override modelName(modelId: string): string {
    return modelId.startsWith(`${this.id}/`)
      ? modelId.slice(this.id.length + 1)
      : modelId;
  }

  protected override modelFeatureInfo(
    modelId: string,
  ): CompletionsModelFeatureInfo {
    const name = this.modelName(modelId);
    if (name.startsWith("openai/")) {
      return featureInfoForOpenAIModel(openaiModelName(name, null));
    }
    return EMPTY_FEATURE_INFO;
  }
}

/** Atlas Cloud's OpenAI-compatible API. */
export class AtlasCloudProvider extends CompatibleProvider {
  readonly id = "atlascloud" as const;

  constructor(init: ProviderInit = {}) {
    super(
      "atlascloud",
      "ATLASCLOUD_API_KEY",
      "https://api.atlascloud.ai/v1",
      init,
    );
  }
}

/** Cheaper Inference's OpenAI-compatible API. */
export class CheaperInferenceProvider extends CompatibleProvider {
  readonly id = "cheaperinference" as const;

  constructor(init: ProviderInit = {}) {
    super(
      "cheaperinference",
      "CHEAPER_INFERENCE_API_KEY",
      "https://api.cheaperinference.com/v1",
      init,
    );
  }

  protected override modelFeatureInfo(
    modelId: string,
  ): CompletionsModelFeatureInfo {
    const name = this.modelName(modelId);
    return /^(gpt-|o1|o3|o4)/.test(name)
      ? featureInfoForOpenAIModel(name)
      : EMPTY_FEATURE_INFO;
  }
}

/** MiniMax's OpenAI-compatible API. */
export class MiniMaxProvider extends CompatibleProvider {
  readonly id = "minimax" as const;

  constructor(init: ProviderInit = {}) {
    super("minimax", "MINIMAX_API_KEY", "https://api.minimax.io/v1", init);
  }
}

/** Opper's OpenAI-compatible gateway. */
export class OpperProvider extends CompatibleProvider {
  readonly id = "opper" as const;

  constructor(init: ProviderInit = {}) {
    super("opper", "OPPER_API_KEY", "https://api.opper.ai/v3/compat", init);
  }

  protected override modelFeatureInfo(
    modelId: string,
  ): CompletionsModelFeatureInfo {
    const name = this.modelName(modelId);
    return /^(gpt-|o1|o3|o4)/.test(name)
      ? featureInfoForOpenAIModel(name)
      : super.modelFeatureInfo(modelId);
  }
}

/** Requesty's OpenAI-compatible router. */
export class RequestyProvider extends CompatibleProvider {
  readonly id = "requesty" as const;

  constructor(init: ProviderInit = {}) {
    super(
      "requesty",
      "REQUESTY_API_KEY",
      "https://router.requesty.ai/v1",
      init,
    );
  }
}
