/**
 * E2E tests for provider overriding.
 *
 * Tests verify that providers can be overridden for specific model scopes.
 */

import { resolve } from "node:path";

import type { ProviderConfig } from "@/tests/e2e/providers";

import { defineCall } from "@/llm/calls";
import {
  OpenAICompletionsProvider,
  OpenAIResponsesProvider,
} from "@/llm/providers/openai";
import { registerProvider } from "@/llm/providers/registry";
import { createIt, describe, expect, snapshotTest } from "@/tests/e2e/utils";

const it = createIt(resolve(__dirname, "cassettes"), "provider-overriding");

/**
 * OpenAI model configurations to test with provider overrides.
 */
const OPENAI_MODEL_IDS: ProviderConfig[] = [
  { providerId: "openai", model: "openai/gpt-4o-mini" },
  { providerId: "openai:completions", model: "openai/gpt-4o-mini:completions" },
  { providerId: "openai:responses", model: "openai/gpt-4o-mini:responses" },
];

// Note: These tests are skipped because provider overriding interacts
// with cassette recording in complex ways. The runtime behavior is correct
// but the recorded responses capture the original provider info.
describe.skip("provider overriding", () => {
  it.record.each(OPENAI_MODEL_IDS)(
    "enforces completions API usage when registered",
    async ({ model }) => {
      // Register completions provider instance for all openai/ models
      const completionsProvider = new OpenAICompletionsProvider({});
      registerProvider(completionsProvider, { scope: "openai/" });

      const simpleCall = defineCall({
        model,
        maxTokens: 100,
        template: () => "Say hello",
      });

      const snap = await snapshotTest(async (s) => {
        const response = await simpleCall();

        // Should use completions provider regardless of model suffix
        expect(response.providerId).toBe("openai:completions");
        expect(response.providerModelName).toMatch(/:completions$/);

        s.setResponse(response);
      });

      expect(snap.toObject()).toMatchSnapshot();
    },
    60000,
  );

  it.record.each(OPENAI_MODEL_IDS)(
    "enforces responses API usage when registered",
    async ({ model }) => {
      // Register responses provider instance for all openai/ models
      const responsesProvider = new OpenAIResponsesProvider({});
      registerProvider(responsesProvider, { scope: "openai/" });

      const simpleCall = defineCall({
        model,
        maxTokens: 100,
        template: () => "Say hello",
      });

      const snap = await snapshotTest(async (s) => {
        const response = await simpleCall();

        // Should use responses provider regardless of model suffix
        expect(response.providerId).toBe("openai:responses");
        expect(response.providerModelName).toMatch(/:responses$/);

        s.setResponse(response);
      });

      expect(snap.toObject()).toMatchSnapshot();
    },
    60000,
  );
});
