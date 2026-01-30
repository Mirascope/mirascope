/**
 * E2E tests for LLM call output handling.
 *
 * These tests verify we correctly decode API responses.
 * Input encoding tests are in e2e/input/.
 * Tests run against multiple providers via parameterization.
 */

import { resolve } from "node:path";

import { defineCall } from "@/llm/calls";
import { FinishReason } from "@/llm/responses/finish-reason";
import { PROVIDERS } from "@/tests/e2e/providers";
import { createIt, describe, expect } from "@/tests/e2e/utils";

const it = createIt(resolve(__dirname, "cassettes"), "call");

describe("call output", () => {
  it.record.each(PROVIDERS)("decodes text response", async ({ model }) => {
    const call = defineCall<{ a: number; b: number }>({
      model,
      maxTokens: 100,
      template: ({ a, b }) => `What is ${a} + ${b}?`,
    });

    const response = await call({ a: 4200, b: 42 });

    expect(response.text()).toContain("4242");
    expect(response.usage).not.toBeNull();
    expect(response.usage?.inputTokens).toBeGreaterThan(0);
    expect(response.usage?.outputTokens).toBeGreaterThan(0);
    expect(response.finishReason).toBeNull(); // Normal completion
  });

  it.record.each(PROVIDERS)(
    "returns max_tokens finish reason",
    async ({ model }) => {
      const call = defineCall({
        model,
        maxTokens: 50, // Low enough to truncate but above Responses API minimum
        template: () => "Write a long story about a dragon.",
      });

      const response = await call();

      expect(response.finishReason).toBe(FinishReason.MAX_TOKENS);
    },
  );
});
