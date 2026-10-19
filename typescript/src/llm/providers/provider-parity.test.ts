import { afterEach, describe, expect, it, vi } from "vitest";

import { user } from "@/llm/messages";
import {
  getProviderForModel,
  registerProvider,
  resetProviderRegistry,
} from "@/llm/providers/registry";

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
  resetProviderRegistry();
});

describe("Python-compatible HTTP providers", () => {
  const cases = [
    [
      "atlascloud",
      "ATLASCLOUD_API_KEY",
      "https://api.atlascloud.ai/v1",
      "deepseek-ai/test",
    ],
    [
      "cheaperinference",
      "CHEAPER_INFERENCE_API_KEY",
      "https://api.cheaperinference.com/v1",
      "gpt-5.4-mini",
    ],
    [
      "cheaperinference",
      "CHEAPER_INFERENCE_API_KEY",
      "https://api.cheaperinference.com/v1",
      "deepseek-v4",
    ],
    ["minimax", "MINIMAX_API_KEY", "https://api.minimax.io/v1", "MiniMax-M3"],
    [
      "requesty",
      "REQUESTY_API_KEY",
      "https://router.requesty.ai/v1",
      "openai/gpt-4o",
    ],
  ] as const;

  it("allows Requesty to route an existing OpenAI model scope", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new globalThis.Response(
        JSON.stringify({
          id: "chatcmpl-test",
          object: "chat.completion",
          created: 1,
          model: "openai/gpt-4o",
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
    const provider = registerProvider("requesty", {
      apiKey: "test-key",
      scope: "openai/",
    });
    expect(getProviderForModel("openai/gpt-4o")).toBe(provider);
    await provider.call({
      modelId: "openai/gpt-4o",
      messages: [user("hello")],
    });
    const [, init] = fetchMock.mock.calls[0] as [URL, RequestInit];
    expect(JSON.parse(String(init.body)).model).toBe("openai/gpt-4o");
  });

  it.each(cases)(
    "routes %s to its API with the provider prefix removed",
    async (id, envVar, baseURL, model) => {
      vi.stubEnv(envVar, "test-key");
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

      const provider = getProviderForModel(`${id}/${model}`);
      const response = await provider.call({
        modelId: `${id}/${model}`,
        messages: [user("hello")],
      });

      expect(provider.id).toBe(id);
      expect(response.providerId).toBe(id);
      const [url, init] = fetchMock.mock.calls[0] as [URL, RequestInit];
      expect(String(url)).toBe(`${baseURL}/chat/completions`);
      expect(JSON.parse(String(init.body)).model).toBe(model);
    },
  );

  it("routes xAI through its Responses API", async () => {
    vi.stubEnv("XAI_API_KEY", "test-key");
    const fetchMock = vi.fn().mockResolvedValue(
      new globalThis.Response(
        JSON.stringify({
          id: "resp_test",
          object: "response",
          created_at: 1,
          model: "grok-4",
          output: [
            {
              type: "message",
              id: "msg_test",
              status: "completed",
              role: "assistant",
              content: [
                { type: "output_text", text: "hello", annotations: [] },
              ],
            },
          ],
          status: "completed",
          usage: { input_tokens: 1, output_tokens: 1, total_tokens: 2 },
        }),
        { headers: { "content-type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    const provider = getProviderForModel("xai/grok-4");
    const response = await provider.call({
      modelId: "xai/grok-4",
      messages: [user("hello")],
    });

    expect(response.providerId).toBe("xai");
    expect(response.modelId).toBe("xai/grok-4");
    const [url, init] = fetchMock.mock.calls[0] as [URL, RequestInit];
    expect(String(url)).toBe("https://api.x.ai/v1/responses");
    expect(JSON.parse(String(init.body)).model).toBe("grok-4");
  });
});
