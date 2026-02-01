/**
 * E2E tests for Mirascope Router provider.
 */

import { resolve } from "node:path";

import type { ProviderConfig } from "@/tests/e2e/providers";

import { defineCall } from "@/llm/calls";
import { user } from "@/llm/messages";
import { MirascopeProvider } from "@/llm/providers/mirascope";
import { registerProvider } from "@/llm/providers/registry";
import { createIt, describe, expect } from "@/tests/e2e/utils";

const it = createIt(resolve(__dirname, "cassettes"), "mirascope");

const MIRASCOPE_PROVIDERS: ProviderConfig[] = [
  { providerId: "mirascope:openai", model: "openai/gpt-4o-mini" },
  { providerId: "mirascope:anthropic", model: "anthropic/claude-haiku-4-5" },
  { providerId: "mirascope:google", model: "google/gemini-2.0-flash" },
];

function registerMirascopeRouter(): void {
  const provider = new MirascopeProvider({
    baseURL: "http://localhost:3000/router/v2",
  });
  registerProvider(provider, { scope: ["anthropic/", "google/", "openai/"] });
}

describe("mirascope provider", () => {
  it.record.each(MIRASCOPE_PROVIDERS)(
    "routes to underlying provider",
    async ({ model }) => {
      registerMirascopeRouter();

      const call = defineCall({
        model,
        maxTokens: 100,
        template: () => [
          user("What is 4200 + 42? Answer with just the number."),
        ],
      });

      const response = await call();
      expect(response.text()).toContain("4242");
    },
  );

  it.record.each(MIRASCOPE_PROVIDERS)(
    "streams from underlying provider",
    async ({ model }) => {
      registerMirascopeRouter();

      const call = defineCall({
        model,
        maxTokens: 100,
        template: () => [
          user("What is 4200 + 42? Answer with just the number."),
        ],
      });

      const stream = await call.stream();
      const chunks: string[] = [];
      for await (const text of stream.textStream()) {
        chunks.push(text);
      }
      expect(chunks.join("")).toContain("4242");
    },
  );
});
