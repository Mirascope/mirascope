/**
 * E2E tests for LLM call output handling.
 *
 * These tests verify we correctly decode API responses.
 * Input encoding tests are in e2e/input/.
 */

import { resolve } from 'node:path';
import { createIt, describe, expect } from '@/tests/e2e/utils';
import { defineCall } from '@/llm/calls';
import { FinishReason } from '@/llm/responses/finish-reason';

const it = createIt(resolve(__dirname, 'cassettes'), 'call');

describe('call output', () => {
  it.record('decodes text response', async () => {
    const call = defineCall<{ a: number; b: number }>({
      model: 'anthropic/claude-haiku-4-5',
      maxTokens: 100,
      template: ({ a, b }) => `What is ${a} + ${b}?`,
    });

    const response = await call({ a: 4200, b: 42 });

    expect(response.text()).toContain('4242');
    expect(response.usage).not.toBeNull();
    expect(response.usage?.inputTokens).toBeGreaterThan(0);
    expect(response.usage?.outputTokens).toBeGreaterThan(0);
    expect(response.finishReason).toBeNull(); // Normal completion
  });

  it.record('returns max_tokens finish reason', async () => {
    const call = defineCall({
      model: 'anthropic/claude-haiku-4-5',
      maxTokens: 5, // Very low to force truncation
      template: () => 'Write a long story about a dragon.',
    });

    const response = await call();

    expect(response.finishReason).toBe(FinishReason.MAX_TOKENS);
  });
});
