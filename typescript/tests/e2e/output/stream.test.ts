/**
 * E2E tests for LLM streaming output handling.
 *
 * These tests verify we correctly decode streaming API responses.
 * Tests run against multiple providers via parameterization.
 */

import { resolve } from "node:path";

import { defineCall } from "@/llm/calls";
import { NotFoundError, BadRequestError } from "@/llm/exceptions";
import { FinishReason } from "@/llm/responses/finish-reason";
import { PROVIDERS, PROVIDERS_FOR_THINKING_TESTS } from "@/tests/e2e/providers";
import { createIt, describe, expect } from "@/tests/e2e/utils";

const it = createIt(resolve(__dirname, "cassettes"), "stream");

/**
 * Providers that reliably return thought content during streaming.
 * OpenAI Responses API may return empty reasoning summaries, so it's excluded.
 */
const PROVIDERS_FOR_THOUGHT_STREAMING = PROVIDERS_FOR_THINKING_TESTS.filter(
  (p) => !p.providerId.startsWith("openai"),
);

describe("stream output", () => {
  // Note: gpt-5-mini uses reasoning by default, so we need enough tokens for reasoning + output
  it.record.each(PROVIDERS)("streams text response", async ({ model }) => {
    const call = defineCall({
      model,
      maxTokens: 500,
      template: () => 'Say "hello world"',
    });

    const response = await call.stream();

    const chunks: string[] = [];
    for await (const text of response.textStream()) {
      chunks.push(text);
    }

    expect(chunks.length).toBeGreaterThan(0);
    expect(chunks.join("")).toMatch(/hello\s*world/i);
    expect(response.text()).toMatch(/hello\s*world/i);
  });

  it.record.each(PROVIDERS)(
    "provides finish reason after streaming",
    async ({ model }) => {
      const call = defineCall({
        model,
        maxTokens: 500,
        template: () => "Hi",
      });

      const response = await call.stream();

      // Consume the stream
      for await (const _ of response.textStream()) {
        // Just consume
      }

      // Normal completion returns null finish reason
      expect(response.finishReason).toBeNull();
    },
  );

  // Test max_tokens finish reason across all providers.
  // Use a small max_tokens (but above provider minimums) and prompt that generates lots of output.
  it.record.each(PROVIDERS)(
    "returns max_tokens finish reason",
    async ({ model }) => {
      const call = defineCall({
        model,
        maxTokens: 50, // Small enough to hit limit, large enough for all providers
        template: () =>
          "Write a 1000 word essay about the history of dragons in mythology, " +
          "covering their origins in ancient civilizations, their role in medieval " +
          "European folklore, and their depictions in modern fantasy literature.",
      });

      const response = await call.stream();

      // Consume the stream
      for await (const _ of response.textStream()) {
        // Just consume
      }

      expect(response.finishReason).toBe(FinishReason.MAX_TOKENS);
    },
  );

  it.record.each(PROVIDERS)(
    "provides usage after streaming",
    async ({ model }) => {
      const call = defineCall({
        model,
        maxTokens: 500,
        template: () => "Hi",
      });

      const response = await call.stream();

      // Consume the stream
      for await (const _ of response.textStream()) {
        // Just consume
      }

      expect(response.usage).not.toBeNull();
      expect(response.usage?.inputTokens).toBeGreaterThan(0);
      expect(response.usage?.outputTokens).toBeGreaterThan(0);
    },
  );

  it.record.each(PROVIDERS)(
    "accumulates content as stream progresses",
    async ({ model }) => {
      const call = defineCall({
        model,
        maxTokens: 500,
        template: () => 'Say "hello"',
      });

      const response = await call.stream();

      // Content should be empty initially
      expect(response.content.length).toBe(0);

      // Consume the stream
      for await (const _ of response.textStream()) {
        // Just consume
      }

      // After consuming, content should be populated
      expect(response.content.length).toBeGreaterThan(0);
      expect(response.content[0]?.type).toBe("text");
    },
  );

  it.record.each(PROVIDERS)(
    "builds assistant message after streaming",
    async ({ model }) => {
      const call = defineCall({
        model,
        maxTokens: 500,
        template: () => 'Say "hello"',
      });

      const response = await call.stream();

      // Consume the stream
      for await (const _ of response.textStream()) {
        // Just consume
      }

      const msg = response.assistantMessage;
      expect(msg.role).toBe("assistant");
      expect(msg.content.length).toBeGreaterThan(0);
      expect(msg.providerId).toBeDefined();
    },
  );
});

describe("stream thinking", () => {
  // Note: Anthropic requires maxTokens > thinking budget. We use 16000 for safety.
  // Note: OpenAI Responses API may return empty reasoning summaries, so we use
  // PROVIDERS_FOR_THOUGHT_STREAMING which excludes OpenAI.
  it.record.each(PROVIDERS_FOR_THOUGHT_STREAMING)(
    "streams thought content when includeThoughts is true",
    async ({ model }) => {
      const call = defineCall({
        model,
        maxTokens: 16000,
        thinking: { level: "low", includeThoughts: true },
        template: () => "What is 2 + 2? Think step by step.",
      });

      const response = await call.stream();

      const thoughts: string[] = [];
      for await (const thought of response.thoughtStream()) {
        thoughts.push(thought);
      }

      // At least some thought content should be streamed
      expect(thoughts.length).toBeGreaterThan(0);
      expect(response.thought()).toBeTruthy();
    },
  );

  it.record.each(PROVIDERS_FOR_THINKING_TESTS)(
    "completes with text output when thinking is enabled",
    async ({ model }) => {
      const call = defineCall({
        model,
        maxTokens: 16000,
        thinking: { level: "low", includeThoughts: true },
        template: () => "What is 2 + 2?",
      });

      const response = await call.stream();

      // Consume the stream
      const texts: string[] = [];
      for await (const chunk of response.chunkStream()) {
        if (chunk.type === "text_chunk") {
          texts.push(chunk.delta);
        }
      }

      // Should always have text content
      expect(texts.length).toBeGreaterThan(0);
      expect(response.text()).toMatch(/4/);
    },
  );
});

describe("stream error handling", () => {
  it.record.each(PROVIDERS)(
    "wraps API errors on stream call",
    async ({ model }) => {
      // Use an invalid model ID to trigger an API error
      // Extract provider prefix from model (e.g., 'anthropic/claude-haiku-4-5' -> 'anthropic')
      const providerPrefix = model.split("/")[0];
      const invalidModel = `${providerPrefix}/invalid-model-that-does-not-exist-12345`;

      const call = defineCall({
        model: invalidModel,
        maxTokens: 100,
        template: () => "Hi",
      });

      // Should throw a wrapped API error - either on initial call or during iteration
      // Some providers (like Anthropic) throw during iteration, not initial call
      let caughtError: unknown = null;
      try {
        const response = await call.stream();
        // Consume the stream to trigger iteration errors
        for await (const _ of response.textStream()) {
          // Just consume
        }
      } catch (error) {
        caughtError = error;
      }

      // Verify an error was thrown
      expect(caughtError).not.toBeNull();

      // Verify it's a Mirascope error type (NotFoundError or BadRequestError depending on provider)
      expect(
        caughtError instanceof NotFoundError ||
          caughtError instanceof BadRequestError,
      ).toBe(true);
    },
  );
});
