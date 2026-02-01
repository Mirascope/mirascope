/**
 * E2E tests for prompt output handling.
 *
 * These tests verify we correctly decode API responses when calling prompts directly.
 * Tests run against multiple providers via parameterization.
 */

import { resolve } from 'node:path';
import { createIt, describe, expect } from '@/tests/e2e/utils';
import { PROVIDERS } from '@/tests/e2e/providers';
import { definePrompt } from '@/llm/prompts';

const it = createIt(resolve(__dirname, 'cassettes'), 'prompt');

describe('prompt output', () => {
  it.record.each(PROVIDERS)(
    'calls model with string model id',
    async ({ model }) => {
      const addNumbers = definePrompt<{ a: number; b: number }>({
        template: ({ a, b }) => `What is ${a} + ${b}?`,
      });

      // Call prompt directly with string model ID (not a Model instance)
      const response = await addNumbers(model, {
        a: 4200,
        b: 42,
      });

      expect(response.text()).toContain('4242');
      expect(response.usage).not.toBeNull();
    }
  );

  it.record.each(PROVIDERS)(
    'streams model with string model id',
    async ({ model }) => {
      const addNumbers = definePrompt<{ a: number; b: number }>({
        template: ({ a, b }) => `What is ${a} + ${b}?`,
      });

      // Call prompt directly with string model ID (not a Model instance)
      const response = await addNumbers.stream(model, {
        a: 4200,
        b: 42,
      });

      await response.consume();

      expect(response.text()).toContain('4242');
      expect(response.usage).not.toBeNull();
    }
  );
});
