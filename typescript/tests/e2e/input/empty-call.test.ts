/**
 * E2E tests for LLM calls with empty content.
 *
 * Tests verify correct handling of edge cases like empty strings and arrays.
 * Different providers handle empty content differently:
 * - Anthropic: Rejects empty messages with 400 error
 * - OpenAI: May return empty responses
 * - Google: Handles gracefully
 */

import { resolve } from "node:path";

import { defineCall } from "@/llm/calls";
import { user } from "@/llm/messages";
import { PROVIDERS } from "@/tests/e2e/providers";
import { createIt, describe, expect, snapshotTest } from "@/tests/e2e/utils";

const it = createIt(resolve(__dirname, "cassettes"), "empty-call");

describe("empty call handling", () => {
  it.record.each(PROVIDERS)(
    "handles empty string content",
    async ({ model }) => {
      const call = defineCall({
        model,
        maxTokens: 100,
        template: () => "",
      });

      // Use snapshotTest to capture both success and error cases
      const snap = await snapshotTest(
        async (s) => {
          const response = await call();
          s.setResponse(response);
          // Some providers return empty responses for empty input
          s.set("hasText", response.text().length > 0);
        },
        { extraExceptions: [Error] },
      );

      expect(snap.toObject()).toMatchSnapshot();
    },
  );

  it.record.each(PROVIDERS)("handles user message", async ({ model }) => {
    const call = defineCall({
      model,
      maxTokens: 100,
      template: () => [user("Say hello")],
    });

    const snap = await snapshotTest(async (s) => {
      const response = await call();
      s.setResponse(response);
      expect(response.text().length).toBeGreaterThan(0);
    });

    expect(snap.toObject()).toMatchSnapshot();
  });
});
