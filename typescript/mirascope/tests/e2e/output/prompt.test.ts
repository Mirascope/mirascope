/**
 * E2E tests for prompt output handling.
 *
 * These tests verify we correctly decode API responses when calling prompts directly.
 */

import { resolve } from 'node:path';
import { createIt, describe, expect } from '@/tests/e2e/utils';
import { definePrompt } from '@/llm/prompts';

const it = createIt(resolve(__dirname, 'cassettes'), 'prompt');

describe('prompt output', () => {
  it.record('calls model with string model id', async () => {
    const addNumbers = definePrompt<{ a: number; b: number }>({
      template: ({ a, b }) => `What is ${a} + ${b}?`,
    });

    // Call prompt directly with string model ID (not a Model instance)
    const response = await addNumbers('anthropic/claude-haiku-4-5', {
      a: 4200,
      b: 42,
    });

    expect(response.text()).toContain('4242');
    expect(response.usage).not.toBeNull();
  });
});
