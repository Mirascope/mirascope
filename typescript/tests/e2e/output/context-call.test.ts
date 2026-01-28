/**
 * E2E tests for context-aware LLM calls.
 *
 * These tests verify context calls work correctly across providers.
 * Context calls are functionally equivalent to regular calls until
 * context-aware tools are implemented.
 */

import { resolve } from 'node:path';
import { createIt, describe, expect } from '@/tests/e2e/utils';
import { PROVIDERS } from '@/tests/e2e/providers';
import { defineContextCall } from '@/llm/calls';
import { createContext } from '@/llm/context';

const it = createIt(resolve(__dirname, 'cassettes'), 'context-call');

interface TestDeps {
  multiplier: number;
}

describe('context call output', () => {
  it.record.each(PROVIDERS)(
    'decodes text response with context',
    async ({ model }) => {
      const call = defineContextCall<{ value: number }, TestDeps>({
        model,
        maxTokens: 100,
        template: ({ ctx, value }) =>
          `What is ${value} * ${ctx.deps.multiplier}?`,
      });

      const ctx = createContext<TestDeps>({ multiplier: 10 });
      const response = await call(ctx, { value: 42 });

      expect(response.text()).toContain('420');
      expect(response.usage).not.toBeNull();
      expect(response.usage?.inputTokens).toBeGreaterThan(0);
      expect(response.usage?.outputTokens).toBeGreaterThan(0);
    }
  );

  it.record.each(PROVIDERS)(
    'streams response with context',
    async ({ model }) => {
      const call = defineContextCall<{ value: number }, TestDeps>({
        model,
        maxTokens: 100,
        template: ({ ctx, value }) =>
          `What is ${value} * ${ctx.deps.multiplier}?`,
      });

      const ctx = createContext<TestDeps>({ multiplier: 10 });
      const stream = await call.stream(ctx, { value: 42 });

      const chunks: string[] = [];
      for await (const text of stream.textStream()) {
        chunks.push(text);
      }

      expect(stream.text()).toContain('420');
      expect(chunks.length).toBeGreaterThan(0);
    }
  );
});
