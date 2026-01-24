/**
 * E2E input tests for call message and param encoding.
 *
 * These tests make actual API calls to verify inputs are correctly encoded.
 */

import { resolve } from 'node:path';
import { createIt, describe, expect } from '@/tests/e2e/utils';
import { defineCall } from '@/llm/calls';
import { assistant, system, user } from '@/llm/messages';

const it = createIt(resolve(__dirname, 'cassettes'), 'call');

describe('call input encoding', () => {
  it.record('encodes system message', async () => {
    const call = defineCall<{ topic: string }>({
      model: 'anthropic/claude-haiku-4-5',
      maxTokens: 50,
      template: ({ topic }) => [
        system('You are a helpful assistant. Be very concise.'),
        user(`What is ${topic}?`),
      ],
    });

    const response = await call({ topic: 'TypeScript' });

    expect(response.text().length).toBeGreaterThan(0);
    expect(response.usage).not.toBeNull();
  });

  it.record('encodes temperature param', async () => {
    const call = defineCall({
      model: 'anthropic/claude-haiku-4-5',
      maxTokens: 20,
      temperature: 0.5,
      template: () => 'Say hello in one word.',
    });

    const response = await call();

    expect(response.text().length).toBeGreaterThan(0);
  });

  it.record('encodes topP param', async () => {
    const call = defineCall({
      model: 'anthropic/claude-haiku-4-5',
      maxTokens: 20,
      topP: 0.9,
      template: () => 'Say hi in one word.',
    });

    const response = await call();

    expect(response.text().length).toBeGreaterThan(0);
  });

  it.record('encodes topK param', async () => {
    const call = defineCall({
      model: 'anthropic/claude-haiku-4-5',
      maxTokens: 20,
      topK: 40,
      template: () => 'Say hey in one word.',
    });

    const response = await call();

    expect(response.text().length).toBeGreaterThan(0);
  });

  it.record('encodes stopSequences param', async () => {
    const call = defineCall({
      model: 'anthropic/claude-haiku-4-5',
      maxTokens: 100,
      stopSequences: ['STOP'],
      template: () => 'Count from 1 to 5, then write STOP, then continue.',
    });

    const response = await call();

    // Should stop before completing due to stop sequence
    expect(response.text()).not.toContain('STOP');
  });

  it.record('encodes assistant message', async () => {
    const call = defineCall({
      model: 'anthropic/claude-haiku-4-5',
      maxTokens: 20,
      template: () => [
        user('What is 2+2?'),
        assistant('The answer is', { modelId: null, providerId: null }),
      ],
    });

    const response = await call();

    // Model should continue from the assistant prefix
    expect(response.text()).toContain('4');
  });

  it.record('encodes multi-part user content', async () => {
    const call = defineCall({
      model: 'anthropic/claude-haiku-4-5',
      maxTokens: 20,
      template: () => [
        user([
          { type: 'text', text: 'What is ' },
          { type: 'text', text: '5 + 5?' },
        ]),
      ],
    });

    const response = await call();

    expect(response.text()).toContain('10');
  });
});
