/**
 * Unit tests for OpenAI Completions provider utilities.
 *
 * Note: Most encoding tests are covered by e2e tests in tests/e2e/input/.
 * These tests focus on error cases that can't be tested via successful API calls.
 */

import { describe, it, expect } from 'vitest';
import type { ChatCompletion } from 'openai/resources/chat/completions';
import { assistant, system, user } from '@/llm/messages';
import { FeatureNotSupportedError } from '@/llm/exceptions';
import { encodeMessages, buildRequestParams, decodeResponse } from './_utils';

describe('encodeMessages', () => {
  it('encodes a simple system message', () => {
    const messages = [system('You are a helpful assistant.')];
    const encoded = encodeMessages(messages);

    expect(encoded).toEqual([
      { role: 'system', content: 'You are a helpful assistant.' },
    ]);
  });

  it('encodes a simple user message', () => {
    const messages = [user('Hello!')];
    const encoded = encodeMessages(messages);

    expect(encoded).toEqual([{ role: 'user', content: 'Hello!' }]);
  });

  it('encodes user message with name', () => {
    const messages = [user('Hello!', { name: 'Alice' })];
    const encoded = encodeMessages(messages);

    expect(encoded).toEqual([
      { role: 'user', content: 'Hello!', name: 'Alice' },
    ]);
  });

  it('encodes a simple assistant message', () => {
    const messages = [
      assistant('Hello back!', {
        providerId: 'openai',
        modelId: 'openai/gpt-4o',
      }),
    ];
    const encoded = encodeMessages(messages);

    expect(encoded).toEqual([{ role: 'assistant', content: 'Hello back!' }]);
  });

  it('encodes assistant message with name', () => {
    const messages = [
      assistant('Hello back!', {
        providerId: 'openai',
        modelId: 'openai/gpt-4o',
        name: 'Bot',
      }),
    ];
    const encoded = encodeMessages(messages);

    expect(encoded).toEqual([
      { role: 'assistant', content: 'Hello back!', name: 'Bot' },
    ]);
  });

  it('encodes full conversation with multiple message types', () => {
    const messages = [
      system('You are a helpful assistant.'),
      user('Hello!'),
      assistant('Hi there!', {
        providerId: 'openai',
        modelId: 'openai/gpt-4o',
      }),
      user('How are you?'),
    ];
    const encoded = encodeMessages(messages);

    expect(encoded).toHaveLength(4);
    expect(encoded[0]).toEqual({
      role: 'system',
      content: 'You are a helpful assistant.',
    });
    expect(encoded[1]).toEqual({ role: 'user', content: 'Hello!' });
    expect(encoded[2]).toEqual({ role: 'assistant', content: 'Hi there!' });
    expect(encoded[3]).toEqual({ role: 'user', content: 'How are you?' });
  });

  it('handles user message with multiple text parts', () => {
    const messages = [
      user([
        { type: 'text' as const, text: 'First part.' },
        { type: 'text' as const, text: 'Second part.' },
      ]),
    ];
    const encoded = encodeMessages(messages);

    expect(encoded).toEqual([
      {
        role: 'user',
        content: [
          { type: 'text', text: 'First part.' },
          { type: 'text', text: 'Second part.' },
        ],
      },
    ]);
  });

  it('handles assistant message with empty content', () => {
    const messages = [
      assistant([], { providerId: 'openai', modelId: 'openai/gpt-4o' }),
    ];
    const encoded = encodeMessages(messages);

    expect(encoded).toEqual([{ role: 'assistant', content: null }]);
  });

  it('handles assistant message with multiple text parts', () => {
    const messages = [
      assistant(
        [
          { type: 'text' as const, text: 'First part.' },
          { type: 'text' as const, text: 'Second part.' },
        ],
        { providerId: 'openai', modelId: 'openai/gpt-4o' }
      ),
    ];
    const encoded = encodeMessages(messages);

    expect(encoded).toEqual([
      {
        role: 'assistant',
        content: [
          { type: 'text', text: 'First part.' },
          { type: 'text', text: 'Second part.' },
        ],
      },
    ]);
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

    expect(params.max_tokens).toBe(100);
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

  it('throws FeatureNotSupportedError for topK param', () => {
    const messages = [user('Hello')];

    expect(() =>
      buildRequestParams('openai/gpt-4o', messages, {
        topK: 10,
      })
    ).toThrow(FeatureNotSupportedError);
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

  it('decodes basic text response', () => {
    const response = createMockResponse();
    const decoded = decodeResponse(response, 'openai/gpt-4o');

    expect(decoded.assistantMessage.role).toBe('assistant');
    expect(decoded.assistantMessage.content).toEqual([
      { type: 'text', text: 'Hello!' },
    ]);
    expect(decoded.assistantMessage.providerId).toBe('openai');
    expect(decoded.assistantMessage.modelId).toBe('openai/gpt-4o');
    expect(decoded.assistantMessage.providerModelName).toBe('gpt-4o');
  });

  it('decodes response with refusal', () => {
    const response = createMockResponse({
      choices: [
        {
          index: 0,
          message: {
            role: 'assistant',
            content: null,
            refusal: "I can't help with that.",
          },
          finish_reason: 'stop',
          logprobs: null,
        },
      ],
    });

    const decoded = decodeResponse(response, 'openai/gpt-4o');

    expect(decoded.assistantMessage.content).toEqual([
      { type: 'text', text: "I can't help with that." },
    ]);
  });

  it('maps length finish_reason to max_tokens', () => {
    const response = createMockResponse({
      choices: [
        {
          index: 0,
          message: {
            role: 'assistant',
            content: 'Hello!',
            refusal: null,
          },
          finish_reason: 'length',
          logprobs: null,
        },
      ],
    });

    const decoded = decodeResponse(response, 'openai/gpt-4o');
    expect(decoded.finishReason).toBe('max_tokens');
  });

  it('maps content_filter finish_reason to refusal', () => {
    const response = createMockResponse({
      choices: [
        {
          index: 0,
          message: {
            role: 'assistant',
            content: 'Hello!',
            refusal: null,
          },
          finish_reason: 'content_filter',
          logprobs: null,
        },
      ],
    });

    const decoded = decodeResponse(response, 'openai/gpt-4o');
    expect(decoded.finishReason).toBe('refusal');
  });

  it('decodes usage tokens', () => {
    const response = createMockResponse({
      usage: {
        prompt_tokens: 10,
        completion_tokens: 20,
        total_tokens: 30,
        prompt_tokens_details: {
          cached_tokens: 5,
        },
        completion_tokens_details: {
          reasoning_tokens: 3,
        },
      },
    });

    const decoded = decodeResponse(response, 'openai/gpt-4o');

    expect(decoded.usage).not.toBeNull();
    expect(decoded.usage?.inputTokens).toBe(10);
    expect(decoded.usage?.outputTokens).toBe(20);
    expect(decoded.usage?.cacheReadTokens).toBe(5);
    expect(decoded.usage?.reasoningTokens).toBe(3);
  });

  it('handles response without usage', () => {
    const response = createMockResponse();
    delete response.usage;

    const decoded = decodeResponse(response, 'openai/gpt-4o');
    expect(decoded.usage).toBeNull();
  });

  it('sets provider metadata on assistant message', () => {
    const response = createMockResponse();
    const decoded = decodeResponse(response, 'openai/gpt-4o');

    expect(decoded.assistantMessage.providerId).toBe('openai');
    expect(decoded.assistantMessage.modelId).toBe('openai/gpt-4o');
    expect(decoded.assistantMessage.providerModelName).toBe('gpt-4o');
  });
});
