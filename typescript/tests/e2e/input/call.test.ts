/**
 * E2E input tests for call message and param encoding.
 *
 * These tests make actual API calls to verify inputs are correctly encoded.
 * Tests run against multiple providers via parameterization.
 *
 * Unsupported params (e.g., topK for OpenAI, seed for Anthropic) log warnings
 * and are ignored, allowing a single test to run across all providers.
 */

import { resolve } from "node:path";

import { defineCall } from "@/llm/calls";
import { assistant, system, user } from "@/llm/messages";
import { PROVIDERS, PROVIDERS_FOR_PARAM_TESTS } from "@/tests/e2e/providers";
import { createIt, describe, expect } from "@/tests/e2e/utils";

const it = createIt(resolve(__dirname, "cassettes"), "call");

describe("call input encoding", () => {
  it.record.each(PROVIDERS_FOR_PARAM_TESTS)(
    "encodes messages and all params",
    async ({ model }) => {
      // Note: Using topP instead of temperature because Anthropic doesn't allow both together
      const call = defineCall<{ topic: string }>({
        model,
        maxTokens: 100,
        topP: 0.9,
        topK: 40, // Unsupported by OpenAI (warns)
        seed: 42, // Unsupported by Anthropic (warns)
        stopSequences: ["STOP"],
        template: ({ topic }) => [
          system("You are a helpful assistant. Be very concise."),
          user(`What is ${topic}? Answer in one sentence.`),
        ],
      });

      const response = await call({ topic: "TypeScript" });

      expect(response.text().length).toBeGreaterThan(0);
      expect(response.usage).not.toBeNull();
    },
  );

  it.record.each(PROVIDERS)("encodes assistant message", async ({ model }) => {
    const call = defineCall({
      model,
      maxTokens: 100,
      template: () => [
        user("What is 2+2?"),
        assistant("The answer is", { modelId: null, providerId: null }),
      ],
    });

    const response = await call();

    // Model should continue from the assistant prefix
    expect(response.text()).toContain("4");
  });

  it.record.each(PROVIDERS)(
    "encodes multi-part user content",
    async ({ model }) => {
      const call = defineCall({
        model,
        maxTokens: 100,
        template: () => [
          user([
            { type: "text", text: "What is " },
            { type: "text", text: "5 + 5?" },
          ]),
        ],
      });

      const response = await call();

      expect(response.text()).toContain("10");
    },
  );
});
