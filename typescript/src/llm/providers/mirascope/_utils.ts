import type { BaseProvider } from "@/llm/providers/base";
import type { ProviderId } from "@/llm/providers/provider-id";

import { getProviderSingleton } from "@/llm/providers/registry";

const DEFAULT_ROUTER_BASE_URL = "https://mirascope.com/router/v2";

export function getDefaultRouterBaseUrl(): string {
  return process.env.MIRASCOPE_ROUTER_BASE_URL ?? DEFAULT_ROUTER_BASE_URL;
}

export function extractModelScope(modelId: string): string | null {
  if (!modelId.includes("/")) {
    return null;
  }
  return modelId.split("/")[0]!;
}

const SUPPORTED_PROVIDERS: ProviderId[] = ["anthropic", "google", "openai"];

export function createUnderlyingProvider(
  modelScope: string,
  apiKey: string,
  routerBaseUrl: string,
): BaseProvider {
  if (!SUPPORTED_PROVIDERS.includes(modelScope as ProviderId)) {
    throw new Error(
      `Unsupported provider: ${modelScope}. ` +
        `Mirascope Router currently supports: ${SUPPORTED_PROVIDERS.join(", ")}`,
    );
  }

  let baseURL = `${routerBaseUrl}/${modelScope}`;
  if (modelScope === "openai") {
    baseURL = `${baseURL}/v1`;
  }

  // Use the shared provider singleton cache from registry
  // This ensures proper cleanup via resetProviderRegistry()
  return getProviderSingleton(modelScope as ProviderId, { apiKey, baseURL });
}
