/**
 * E2E tests for context prompt output handling.
 *
 * These tests verify we correctly decode API responses when calling context prompts.
 * Tests run against multiple providers via parameterization.
 */

import { resolve } from 'node:path';
import { createIt, describe, expect } from '@/tests/e2e/utils';
import { PROVIDERS } from '@/tests/e2e/providers';
import { definePrompt } from '@/llm/prompts';
import { createContext, type Context } from '@/llm/context';

const it = createIt(resolve(__dirname, 'cassettes'), 'context-prompt');

interface TestDeps {
  multiplier: number;
}

describe('context prompt output', () => {
  it.record.each(PROVIDERS)('calls model with context', async ({ model }) => {
    const multiply = definePrompt<{ ctx: Context<TestDeps>; value: number }>({
      template: ({ ctx, value }) =>
        `What is ${value} * ${ctx.deps.multiplier}?`,
    });

    const ctx = createContext<TestDeps>({ multiplier: 10 });
    const response = await multiply(model, ctx, { value: 42 });

    expect(response.text()).toContain('420');
    expect(response.usage).not.toBeNull();
  });

  it.record.each(PROVIDERS)('streams model with context', async ({ model }) => {
    const multiply = definePrompt<{ ctx: Context<TestDeps>; value: number }>({
      template: ({ ctx, value }) =>
        `What is ${value} * ${ctx.deps.multiplier}?`,
    });

    const ctx = createContext<TestDeps>({ multiplier: 10 });
    const response = await multiply.stream(model, ctx, { value: 42 });

    await response.consume();

    expect(response.text()).toContain('420');
    expect(response.usage).not.toBeNull();
  });
});
