/**
 * E2E tests for thinking/reasoning output handling.
 *
 * These tests verify we correctly decode thinking blocks from API responses
 * when thinking is enabled with includeThoughts: true.
 */

import { resolve } from "node:path";

import { defineCall } from "@/llm/calls";
import { PROVIDERS_FOR_THINKING_TESTS } from "@/tests/e2e/providers";
import { createIt, describe, expect } from "@/tests/e2e/utils";

const it = createIt(resolve(__dirname, "cassettes"), "thinking");

describe("thinking output", () => {
  // Use maxTokens > thinking budget. For Anthropic, level 'low' = 0.2 multiplier
  // with minimum 1024 tokens, so we need maxTokens > 1024.
  // Using 8192 gives a budget of 1638 tokens (0.2 * 8192).
  const maxTokens = 8192;

  it.record.each(PROVIDERS_FOR_THINKING_TESTS)(
    "includes thoughts when includeThoughts is true",
    async ({ model }) => {
      const call = defineCall({
        model,
        maxTokens,
        thinking: { level: "low", includeThoughts: true },
        template: () => "What is 2 + 2? Think step by step.",
      });

      const response = await call();

      // Should have at least one thought block
      expect(response.thoughts.length).toBeGreaterThan(0);

      // Thought content should be non-empty
      const firstThought = response.thoughts[0];
      expect(firstThought?.thought.length).toBeGreaterThan(0);

      // Should also have text content with the answer
      expect(response.text()).toBeTruthy();
    },
  );

  it.record.each(PROVIDERS_FOR_THINKING_TESTS)(
    "excludes thoughts when includeThoughts is false",
    async ({ model }) => {
      const call = defineCall({
        model,
        maxTokens,
        thinking: { level: "low", includeThoughts: false },
        template: () => "What is 2 + 2? Think step by step.",
      });

      const response = await call();

      // Should have no thought blocks
      expect(response.thoughts.length).toBe(0);

      // Should still have text content
      expect(response.text()).toBeTruthy();
    },
  );

  // Google and OpenAI Responses report separate reasoning tokens.
  // Anthropic includes thinking tokens in the regular output_tokens.
  // Testing with Google as the canonical example.
  it.record("reports reasoning tokens in usage", async () => {
    const call = defineCall({
      model: "google/gemini-2.5-flash",
      maxTokens,
      thinking: { level: "low", includeThoughts: true },
      template: () => "What is 2 + 2?",
    });

    const response = await call();

    // Usage should include reasoning tokens
    expect(response.usage).not.toBeNull();
    expect(response.usage?.reasoningTokens).toBeGreaterThan(0);
  });
});
