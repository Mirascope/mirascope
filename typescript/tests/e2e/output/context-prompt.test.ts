/**
 * E2E tests for context prompt output handling.
 *
 * These tests verify we correctly decode API responses when calling context prompts.
 * Tests run against multiple providers via parameterization.
 */

import { resolve } from "node:path";

import { createContext, type Context } from "@/llm/context";
import { definePrompt } from "@/llm/prompts";
import { PROVIDERS } from "@/tests/e2e/providers";
import { createIt, describe, expect, snapshotTest } from "@/tests/e2e/utils";

const it = createIt(resolve(__dirname, "cassettes"), "context-prompt");

interface TestDeps {
  multiplier: number;
}

describe("context prompt output", () => {
  it.record.each(PROVIDERS)("calls model with context", async ({ model }) => {
    const multiply = definePrompt<{ ctx: Context<TestDeps>; value: number }>({
      template: ({ ctx, value }) =>
        `What is ${value} * ${ctx.deps.multiplier}?`,
    });

    const snap = await snapshotTest(async (s) => {
      const ctx = createContext<TestDeps>({ multiplier: 10 });
      const response = await multiply(model, ctx, { value: 42 });
      s.setResponse(response);

      expect(response.text()).toContain("420");
      expect(response.usage).not.toBeNull();
    });

    expect(snap.toObject()).toMatchSnapshot();
  });

  it.record.each(PROVIDERS)("streams model with context", async ({ model }) => {
    const multiply = definePrompt<{ ctx: Context<TestDeps>; value: number }>({
      template: ({ ctx, value }) =>
        `What is ${value} * ${ctx.deps.multiplier}?`,
    });

    const snap = await snapshotTest(async (s) => {
      const ctx = createContext<TestDeps>({ multiplier: 10 });
      const response = await multiply.stream(model, ctx, { value: 42 });

      await response.consume();
      s.setResponse(response);

      expect(response.text()).toContain("420");
      expect(response.usage).not.toBeNull();
    });

    expect(snap.toObject()).toMatchSnapshot();
  });
});
