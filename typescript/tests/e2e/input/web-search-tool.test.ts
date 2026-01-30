/**
 * E2E tests for provider web search tool.
 *
 * These tests verify we correctly encode and handle provider-native web search tools.
 * Tests run against providers that support web search: Anthropic, Google, and OpenAI Responses.
 */

import { resolve } from "node:path";

import { defineCall, WebSearchTool } from "@/llm";
import { PROVIDERS_FOR_WEB_SEARCH_TESTS } from "@/tests/e2e/providers";
import { createIt, describe, expect } from "@/tests/e2e/utils";

const it = createIt(resolve(__dirname, "cassettes"), "web-search-tool");

describe("web search tool", () => {
  it.record.each(PROVIDERS_FOR_WEB_SEARCH_TESTS)(
    "handles provider web search tool",
    async ({ model }) => {
      const cryptoPriceLookup = defineCall({
        model,
        maxTokens: 1000,
        tools: [new WebSearchTool()],
        template: () =>
          "Jan 1, 2026 is a date in the past. Use the web search tool to lookup the price of bitcoin on that date.",
      });

      let response = await cryptoPriceLookup();

      // Resume to make sure we handle re-encoding correctly
      response = await response.resume(
        "Please also look up the price of Ethereum on that date",
      );

      // Verify we got a response with some text
      expect(response.text().length).toBeGreaterThan(0);
    },
  );
});

describe("web search tool with streaming", () => {
  it.record.each(PROVIDERS_FOR_WEB_SEARCH_TESTS)(
    "streams with provider web search tool",
    async ({ model }) => {
      const cryptoPriceLookup = defineCall({
        model,
        maxTokens: 1000,
        tools: [new WebSearchTool()],
        template: () =>
          "Jan 1, 2026 is a date in the past. Use the web search tool to lookup the price of bitcoin on that date.",
      });

      let response = await cryptoPriceLookup.stream();

      // Consume the stream
      await response.consume();

      // Resume to make sure we handle re-encoding correctly
      response = await response.resume(
        "Please also look up the price of Ethereum on that date",
      );

      // Consume the resumed stream
      await response.consume();

      // Verify we got a response with some text
      expect(response.text().length).toBeGreaterThan(0);
    },
  );
});
