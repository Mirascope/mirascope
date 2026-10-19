/**
 * E2E tests for AuthenticationError handling.
 *
 * Tests verify that invalid API keys result in AuthenticationError.
 */

import { it as vitestIt, beforeEach, afterEach, vi } from "vitest";

import { defineCall } from "@/llm/calls";
import { AuthenticationError } from "@/llm/exceptions";
import {
  registerProvider,
  resetProviderRegistry,
} from "@/llm/providers/registry";
import { describe, expect } from "@/tests/e2e/utils";

describe("authentication error handling", () => {
  beforeEach(() => {
    resetProviderRegistry();
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL) => {
        const anthropic = String(input).includes("anthropic.com");
        return Promise.resolve(
          new globalThis.Response(
            JSON.stringify(
              anthropic
                ? {
                    type: "error",
                    error: {
                      type: "authentication_error",
                      message: "Invalid API key",
                    },
                  }
                : {
                    error: {
                      message: "Invalid API key",
                      type: "invalid_request_error",
                      code: "invalid_api_key",
                    },
                  },
            ),
            { status: 401, headers: { "content-type": "application/json" } },
          ),
        );
      }),
    );
    // Register providers with invalid API keys
    registerProvider("anthropic", { apiKey: "invalid-key-12345" });
    registerProvider("openai", { apiKey: "invalid-key-12345" });
    registerProvider("google", { apiKey: "invalid-key-12345" });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    resetProviderRegistry();
  });

  vitestIt(
    "throws AuthenticationError for invalid Anthropic API key",
    async () => {
      const call = defineCall({
        model: "anthropic/claude-haiku-4-5",
        maxTokens: 100,
        template: () => "This should fail with AuthenticationError",
      });

      await expect(call()).rejects.toThrow(AuthenticationError);
    },
  );

  vitestIt(
    "throws AuthenticationError for invalid OpenAI API key",
    async () => {
      const call = defineCall({
        model: "openai/gpt-4o-mini:completions",
        maxTokens: 100,
        template: () => "This should fail with AuthenticationError",
      });

      await expect(call()).rejects.toThrow(AuthenticationError);
    },
  );

  // Note: Google returns 400 BadRequestError for invalid API keys instead of 401
  // so we skip this test for Google.
  vitestIt.skip(
    "throws AuthenticationError for invalid Google API key",
    async () => {
      const call = defineCall({
        model: "google/gemini-2.5-flash",
        maxTokens: 100,
        template: () => "This should fail with AuthenticationError",
      });

      await expect(call()).rejects.toThrow(AuthenticationError);
    },
  );

  vitestIt(
    "throws AuthenticationError during streaming for invalid API key",
    async () => {
      const call = defineCall({
        model: "anthropic/claude-haiku-4-5",
        maxTokens: 100,
        template: () => "This should fail with AuthenticationError",
      });

      const response = await call.stream();

      // Consume the stream to trigger the error
      await expect(response.consume()).rejects.toThrow(AuthenticationError);
    },
  );
});
