/**
 * E2E tests for WebSearchTool (provider-native web search).
 *
 * Tests verify that WebSearchTool is correctly passed to providers
 * and that the responses are properly handled.
 *
 * Note: OpenAI Responses API is excluded because web search can take
 * a very long time and causes timeout issues.
 */

import { resolve } from "node:path";

import type { ProviderConfig } from "@/tests/e2e/providers";

import { defineCall, WebSearchTool } from "@/llm";
import { createIt, describe, expect, snapshotTest } from "@/tests/e2e/utils";

const it = createIt(resolve(__dirname, "cassettes"), "web-search-tool");

/**
 * Providers for web search tests.
 * Excludes OpenAI Responses API due to timeout issues with web search.
 */
const WEB_SEARCH_PROVIDERS: ProviderConfig[] = [
  { providerId: "anthropic", model: "anthropic/claude-haiku-4-5" },
  { providerId: "google", model: "google/gemini-2.5-flash" },
  { providerId: "openai:completions", model: "openai/gpt-4o-mini:completions" },
];

describe("WebSearchTool", () => {
  it.record.each(WEB_SEARCH_PROVIDERS)(
    "performs web search and returns results",
    async ({ model }) => {
      const cryptoPriceLookup = defineCall({
        model,
        maxTokens: 1000,
        tools: [new WebSearchTool()],
        template: () =>
          "Jan 1, 2026 is a date in the past. Use the web search tool to lookup the price of bitcoin on that date.",
      });

      const snap = await snapshotTest(async (s) => {
        const response = await cryptoPriceLookup();

        // Resume to verify re-encoding works correctly
        const resumed = await response.resume(
          "Please also look up the price of Ethereum on that date",
        );

        s.setResponse(resumed);

        // Response should contain price information
        expect(resumed.text().length).toBeGreaterThan(0);
      });

      expect(snap.toObject()).toMatchSnapshot();
    },
    120000, // Web search can take longer
  );

  it.record.each(WEB_SEARCH_PROVIDERS)(
    "streams with web search tool",
    async ({ model }) => {
      const cryptoPriceLookup = defineCall({
        model,
        maxTokens: 1000,
        tools: [new WebSearchTool()],
        template: () =>
          "Jan 1, 2026 is a date in the past. Use the web search tool to lookup the price of bitcoin on that date.",
      });

      const snap = await snapshotTest(async (s) => {
        const response = await cryptoPriceLookup.stream();
        await response.consume();

        // Resume with streaming to verify re-encoding works correctly
        const resumed = await response.resume(
          "Please also look up the price of Ethereum on that date",
        );
        await resumed.consume();

        s.setResponse(resumed);

        // Response should contain price information
        expect(resumed.text().length).toBeGreaterThan(0);
      });

      expect(snap.toObject()).toMatchSnapshot();
    },
    120000, // Web search can take longer
  );
});
