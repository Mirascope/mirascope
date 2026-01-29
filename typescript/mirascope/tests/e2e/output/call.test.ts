/**
 * E2E tests for LLM calls without tools or structured outputs.
 */

import { resolve } from 'node:path';
import { createIt, describe, expect } from '@/tests/e2e/utils';
import { defineCall } from '@/llm/calls';

const it = createIt(resolve(__dirname, 'cassettes'), 'call');

describe('call', () => {
  it.record('makes a simple call', async () => {
    const addNumbers = defineCall<{ a: number; b: number }>({
      model: 'anthropic/claude-sonnet-4-20250514',
      maxTokens: 100,
      template: ({ a, b }) => `What is ${a} + ${b}?`,
    });

    const response = await addNumbers({ a: 4200, b: 42 });

    expect(response.text()).toMatchInlineSnapshot(`"4200 + 42 = 4242"`);
    expect(response.text()).toContain('4242');
  });
});
