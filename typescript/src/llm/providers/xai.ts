/** xAI's OpenAI-compatible Responses API. */

import { OpenAIResponsesProvider } from "@/llm/providers/openai/responses/provider";

export class XAIProvider extends OpenAIResponsesProvider {
  override readonly id: string = "xai";

  constructor(init: { apiKey?: string; baseURL?: string } = {}) {
    super({
      apiKey: init.apiKey ?? process.env.XAI_API_KEY,
      baseURL: init.baseURL ?? "https://api.x.ai/v1",
    });
  }

  protected override requestModelId(modelId: string): string {
    return `openai/${modelId.replace(/^xai\//, "")}`;
  }
}
