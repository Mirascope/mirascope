/**
 * E2E input tests for call message and param encoding.
 *
 * These tests make actual API calls to verify inputs are correctly encoded.
 * Tests run against multiple providers via parameterization.
 */

import { resolve } from 'node:path';
import { createIt, describe, expect } from '@/tests/e2e/utils';
import { PROVIDERS } from '@/tests/e2e/providers';
import { defineCall } from '@/llm/calls';
import { assistant, system, user } from '@/llm/messages';

const it = createIt(resolve(__dirname, 'cassettes'), 'call');

describe('call input encoding', () => {
  it.record.each(PROVIDERS)('encodes system message', async ({ model }) => {
    const call = defineCall<{ topic: string }>({
      model,
      maxTokens: 200,
      template: ({ topic }) => [
        system('You are a helpful assistant. Be very concise.'),
        user(`What is ${topic}?`),
      ],
    });

    const response = await call({ topic: 'TypeScript' });

    expect(response.text().length).toBeGreaterThan(0);
    expect(response.usage).not.toBeNull();
  });

  it.record.each(PROVIDERS)('encodes temperature param', async ({ model }) => {
    const call = defineCall({
      model,
      maxTokens: 100,
      temperature: 0.5,
      template: () => 'Say hello in one word.',
    });

    const response = await call();

    expect(response.text().length).toBeGreaterThan(0);
  });

  it.record.each(PROVIDERS)('encodes topP param', async ({ model }) => {
    const call = defineCall({
      model,
      maxTokens: 100,
      topP: 0.9,
      template: () => 'Say hi in one word.',
    });

    const response = await call();

    expect(response.text().length).toBeGreaterThan(0);
  });

  it.record.each(PROVIDERS)('encodes topK param', async ({ model }) => {
    const call = defineCall({
      model,
      maxTokens: 100,
      topK: 40,
      template: () => 'Say hey in one word.',
    });

    const response = await call();

    expect(response.text().length).toBeGreaterThan(0);
  });

  it.record.each(PROVIDERS)(
    'encodes stopSequences param',
    async ({ model }) => {
      const call = defineCall({
        model,
        maxTokens: 100,
        stopSequences: ['STOP'],
        template: () => 'Count from 1 to 5, then write STOP, then continue.',
      });

      const response = await call();

      // Should stop before completing due to stop sequence
      expect(response.text()).not.toContain('STOP');
    }
  );

  it.record.each(PROVIDERS)('encodes assistant message', async ({ model }) => {
    const call = defineCall({
      model,
      maxTokens: 100,
      template: () => [
        user('What is 2+2?'),
        assistant('The answer is', { modelId: null, providerId: null }),
      ],
    });

    const response = await call();

    // Model should continue from the assistant prefix
    expect(response.text()).toContain('4');
  });

  it.record.each(PROVIDERS)(
    'encodes multi-part user content',
    async ({ model }) => {
      const call = defineCall({
        model,
        maxTokens: 100,
        template: () => [
          user([
            { type: 'text', text: 'What is ' },
            { type: 'text', text: '5 + 5?' },
          ]),
        ],
      });

      const response = await call();

      expect(response.text()).toContain('10');
    }
  );
});
