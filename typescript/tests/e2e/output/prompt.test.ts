/**
 * E2E tests for prompt output handling.
 *
 * These tests verify we correctly decode API responses when calling prompts directly.
 * Tests run against multiple providers via parameterization.
 */

import { resolve } from "node:path";

import { definePrompt } from "@/llm/prompts";
import { PROVIDERS } from "@/tests/e2e/providers";
import { createIt, describe, expect, snapshotTest } from "@/tests/e2e/utils";

const it = createIt(resolve(__dirname, "cassettes"), "prompt");

describe("prompt output", () => {
  it.record.each(PROVIDERS)(
    "calls model with string model id",
    async ({ model }) => {
      const addNumbers = definePrompt<{ a: number; b: number }>({
        template: ({ a, b }) => `What is ${a} + ${b}?`,
      });

      const snap = await snapshotTest(async (s) => {
        // Call prompt directly with string model ID (not a Model instance)
        const response = await addNumbers(model, {
          a: 4200,
          b: 42,
        });
        s.setResponse(response);

        expect(response.text()).toContain("4242");
        expect(response.usage).not.toBeNull();
      });

      expect(snap.toObject()).toMatchSnapshot();
    },
  );

  it.record.each(PROVIDERS)(
    "streams model with string model id",
    async ({ model }) => {
      const addNumbers = definePrompt<{ a: number; b: number }>({
        template: ({ a, b }) => `What is ${a} + ${b}?`,
      });

      const snap = await snapshotTest(async (s) => {
        // Call prompt directly with string model ID (not a Model instance)
        const response = await addNumbers.stream(model, {
          a: 4200,
          b: 42,
        });

        await response.consume();
        s.setResponse(response);

        expect(response.text()).toContain("4242");
        expect(response.usage).not.toBeNull();
      });

      expect(snap.toObject()).toMatchSnapshot();
    },
  );
});
