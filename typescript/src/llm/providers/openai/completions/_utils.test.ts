/**
 * Unit tests for OpenAI Completions provider utilities.
 *
 * Note: Most encoding tests are covered by e2e tests in tests/e2e/.
 * These tests focus on edge cases that can't be triggered via e2e.
 */

import { describe, it, expect } from 'vitest';
import type { ChatCompletion } from 'openai/resources/chat/completions';
import { assistant, user } from '@/llm/messages';
import type { Thought } from '@/llm/content';
import { FinishReason } from '@/llm/responses/finish-reason';
import {
  encodeMessages,
  decodeResponse,
  buildRequestParams,
} from '@/llm/providers/openai/completions/_utils';

describe('encodeMessages edge cases', () => {
  it('encodes user message with name', () => {
    const messages = [user('Hello!', { name: 'Alice' })];
    const encoded = encodeMessages(messages);

    expect(encoded).toEqual([
      { role: 'user', content: 'Hello!', name: 'Alice' },
    ]);
  });

  it('encodes assistant message with empty content', () => {
    const messages = [
      assistant([], { providerId: 'openai', modelId: 'openai/gpt-4o' }),
    ];
    const encoded = encodeMessages(messages);

    expect(encoded).toEqual([{ role: 'assistant', content: null }]);
  });

  it('encodes assistant message with name', () => {
    const messages = [
      assistant('Hi!', {
        providerId: 'openai',
        modelId: 'openai/gpt-4o',
        name: 'Bot',
      }),
    ];
    const encoded = encodeMessages(messages);

    expect(encoded).toEqual([
      { role: 'assistant', content: 'Hi!', name: 'Bot' },
    ]);
  });
});

describe('buildRequestParams thinking config', () => {
  it('encodes thoughts as text when encodeThoughtsAsText is true', () => {
    const thought: Thought = { type: 'thought', thought: 'Reasoning...' };
    const messages = [
      assistant([thought, { type: 'text', text: 'Result' }], {
        providerId: 'openai',
        modelId: 'openai/gpt-4o',
      }),
    ];

    const params = buildRequestParams('openai/gpt-4o:completions', messages, {
      thinking: { level: 'medium', encodeThoughtsAsText: true },
    });

    expect(params.messages).toEqual([
      { role: 'assistant', content: '**Thinking:** Reasoning...Result' },
    ]);
  });

  it('drops thoughts when encodeThoughtsAsText is not set', () => {
    const thought: Thought = { type: 'thought', thought: 'Reasoning...' };
    const messages = [
      assistant([thought, { type: 'text', text: 'Result' }], {
        providerId: 'openai',
        modelId: 'openai/gpt-4o',
      }),
    ];

    const params = buildRequestParams('openai/gpt-4o:completions', messages, {
      thinking: { level: 'medium' },
    });

    expect(params.messages).toEqual([{ role: 'assistant', content: 'Result' }]);
  });
});

describe('buildRequestParams', () => {
  it('builds basic request with messages', () => {
    const messages = [user('Hello')];
    const params = buildRequestParams('openai/gpt-4o', messages);

    expect(params).toEqual({
      model: 'gpt-4o',
      messages: [{ role: 'user', content: 'Hello' }],
    });
  });

  it('includes maxTokens when provided', () => {
    const messages = [user('Hello')];
    const params = buildRequestParams('openai/gpt-4o', messages, {
      maxTokens: 100,
    });

    expect(params.max_completion_tokens).toBe(100);
  });

  it('includes temperature when provided', () => {
    const messages = [user('Hello')];
    const params = buildRequestParams('openai/gpt-4o', messages, {
      temperature: 0.7,
    });

    expect(params.temperature).toBe(0.7);
  });

  it('includes topP when provided', () => {
    const messages = [user('Hello')];
    const params = buildRequestParams('openai/gpt-4o', messages, {
      topP: 0.9,
    });

    expect(params.top_p).toBe(0.9);
  });

  it('includes seed when provided', () => {
    const messages = [user('Hello')];
    const params = buildRequestParams('openai/gpt-4o', messages, {
      seed: 42,
    });

    expect(params.seed).toBe(42);
  });

  it('includes stopSequences when provided', () => {
    const messages = [user('Hello')];
    const params = buildRequestParams('openai/gpt-4o', messages, {
      stopSequences: ['END', 'STOP'],
    });

    expect(params.stop).toEqual(['END', 'STOP']);
  });
});

describe('decodeResponse', () => {
  const createMockResponse = (
    overrides: Partial<ChatCompletion> = {}
  ): ChatCompletion => ({
    id: 'chatcmpl-123',
    object: 'chat.completion',
    created: 1677652288,
    model: 'gpt-4o',
    choices: [
      {
        index: 0,
        message: {
          role: 'assistant',
          content: 'Hello!',
          refusal: null,
        },
        finish_reason: 'stop',
        logprobs: null,
      },
    ],
    usage: {
      prompt_tokens: 5,
      completion_tokens: 2,
      total_tokens: 7,
    },
    ...overrides,
  });

  it('decodes refusal message as text content', () => {
    const response = createMockResponse({
      choices: [
        {
          index: 0,
          message: {
            role: 'assistant',
            content: null,
            refusal: "I can't help with that request.",
          },
          finish_reason: 'stop',
          logprobs: null,
        },
      ],
    });

    const decoded = decodeResponse(response, 'openai/gpt-4o');

    expect(decoded.assistantMessage.content).toEqual([
      { type: 'text', text: "I can't help with that request." },
    ]);
  });

  it('maps content_filter finish reason to REFUSAL', () => {
    const response = createMockResponse({
      choices: [
        {
          index: 0,
          message: {
            role: 'assistant',
            content: '',
            refusal: null,
          },
          finish_reason: 'content_filter',
          logprobs: null,
        },
      ],
    });

    const decoded = decodeResponse(response, 'openai/gpt-4o');

    expect(decoded.finishReason).toBe(FinishReason.REFUSAL);
  });

  it('handles response without usage', () => {
    const response = createMockResponse();
    delete response.usage;

    const decoded = decodeResponse(response, 'openai/gpt-4o');

    expect(decoded.usage).toBeNull();
  });
});
