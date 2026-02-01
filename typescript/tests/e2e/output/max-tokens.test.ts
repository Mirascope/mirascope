/**
 * E2E tests for behavior when reaching max_tokens limits.
 *
 * Tests verify that finish_reason is correctly set to MAX_TOKENS
 * when the response is truncated due to token limits.
 */

import { resolve } from "node:path";

import { defineCall } from "@/llm/calls";
import { FinishReason } from "@/llm/responses/finish-reason";
import { PROVIDERS } from "@/tests/e2e/providers";
import { createIt, describe, expect, snapshotTest } from "@/tests/e2e/utils";

const it = createIt(resolve(__dirname, "cassettes"), "max-tokens");

describe("max tokens", () => {
  it.record.each(PROVIDERS)(
    "returns MAX_TOKENS finish reason for call",
    async ({ model }) => {
      const listStates = defineCall({
        model,
        maxTokens: 50,
        template: () => "List all U.S. states.",
      });

      const snap = await snapshotTest(async (s) => {
        const response = await listStates();
        s.setResponse(response);

        expect(response.finishReason).toBe(FinishReason.MAX_TOKENS);
      });

      expect(snap.toObject()).toMatchSnapshot();
    },
  );

  it.record.each(PROVIDERS)(
    "returns MAX_TOKENS finish reason for stream",
    async ({ model }) => {
      const listStates = defineCall({
        model,
        maxTokens: 50,
        template: () => "List all U.S. states.",
      });

      const snap = await snapshotTest(async (s) => {
        const response = await listStates.stream();
        await response.consume();
        s.setResponse(response);

        expect(response.finishReason).toBe(FinishReason.MAX_TOKENS);
      });

      expect(snap.toObject()).toMatchSnapshot();
    },
  );
});
