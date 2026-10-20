import { afterEach, describe, expect, it, vi } from "vitest";

import { MissingAPIKeyError } from "@/llm/exceptions";
import { user } from "@/llm/messages";
import { APIRouteProvider } from "@/llm/providers/api-route";
import {
  EMPTY_FEATURE_INFO,
  featureInfoForOpenAIModel,
} from "@/llm/providers/openai/completions/_utils/feature-info";
import {
  getProviderForModel,
  registerProvider,
  resetProviderRegistry,
} from "@/llm/providers/registry";

class InspectableAPIRouteProvider extends APIRouteProvider {
  modelNameForTest(modelId: string): string {
    return this.modelName(modelId);
  }

  featureInfoForTest(modelId: string) {
    return this.modelFeatureInfo(modelId);
  }
}

function stubCompletion(model: string) {
  const fetchMock = vi.fn().mockResolvedValue(
    new globalThis.Response(
      JSON.stringify({
        id: "chatcmpl-test",
        object: "chat.completion",
        created: 1,
        model,
        choices: [
          {
            index: 0,
            message: { role: "assistant", content: "hello" },
            finish_reason: "stop",
          },
        ],
        usage: { prompt_tokens: 1, completion_tokens: 1, total_tokens: 2 },
      }),
      { headers: { "content-type": "application/json" } },
    ),
  );
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
  resetProviderRegistry();
});

describe("APIRouteProvider", () => {
  it("auto-registers only its explicit scope and preserves upstream model IDs", async () => {
    vi.stubEnv("API_ROUTE_API_KEY", "test-key");
    const fetchMock = stubCompletion("anthropic/claude-sonnet-4-6");

    const provider = getProviderForModel(
      "api-route/anthropic/claude-sonnet-4-6",
    );
    const response = await provider.call({
      modelId: "api-route/anthropic/claude-sonnet-4-6",
      messages: [user("hello")],
    });

    expect(provider).toBeInstanceOf(APIRouteProvider);
    expect(response.providerId).toBe("api-route");
    const [url, init] = fetchMock.mock.calls[0] as [URL, RequestInit];
    expect(String(url)).toBe(
      "https://global.api-route.com/v1/chat/completions",
    );
    expect(JSON.parse(String(init.body)).model).toBe(
      "anthropic/claude-sonnet-4-6",
    );
    expect(new Headers(init.headers).get("authorization")).toBe(
      "Bearer test-key",
    );
  });

  it("uses explicit key, endpoint, and scope overrides", async () => {
    const fetchMock = stubCompletion("anthropic/claude-sonnet-4-6");
    const provider = registerProvider("api-route", {
      apiKey: "override-key",
      baseURL: "https://custom.example/v1",
      scope: "anthropic/",
    });
    expect(provider).toBeInstanceOf(APIRouteProvider);
    expect(getProviderForModel("anthropic/claude-sonnet-4-6")).toBe(provider);
    await provider.call({
      modelId: "anthropic/claude-sonnet-4-6",
      messages: [user("hello")],
    });
    const [url, init] = fetchMock.mock.calls[0] as [URL, RequestInit];
    expect(String(url)).toBe("https://custom.example/v1/chat/completions");
    expect(JSON.parse(String(init.body)).model).toBe(
      "anthropic/claude-sonnet-4-6",
    );
    expect(new Headers(init.headers).get("authorization")).toBe(
      "Bearer override-key",
    );
  });

  it("requires its own key without falling back to another provider", () => {
    vi.stubEnv("API_ROUTE_API_KEY", undefined);
    vi.stubEnv("MIRASCOPE_API_KEY", "router-key");
    expect(() => getProviderForModel("api-route/model")).toThrow(
      MissingAPIKeyError,
    );
  });

  it("strips only the routing prefix and applies OpenAI feature information", () => {
    const provider = new InspectableAPIRouteProvider({ apiKey: "test-key" });
    expect(provider.modelNameForTest("api-route/gpt-4o")).toBe("gpt-4o");
    expect(provider.modelNameForTest("anthropic/claude-sonnet-4-6")).toBe(
      "anthropic/claude-sonnet-4-6",
    );
    expect(provider.featureInfoForTest("api-route/gpt-4o")).toEqual(
      featureInfoForOpenAIModel("gpt-4o"),
    );
    expect(provider.featureInfoForTest("api-route/claude-sonnet-4-6")).toEqual(
      EMPTY_FEATURE_INFO,
    );
  });
});
