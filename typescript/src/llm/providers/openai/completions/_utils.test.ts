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
import { Audio } from '@/llm/content';
import { FeatureNotSupportedError } from '@/llm/exceptions';
import { FinishReason } from '@/llm/responses/finish-reason';
import {
  encodeMessages,
  decodeResponse,
  buildRequestParams,
} from '@/llm/providers/openai/completions/_utils';
import type { AudioMimeType } from '@/llm/content';

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

    const params = buildRequestParams(
      'openai/gpt-4o:completions',
      messages,
      undefined,
      {
        thinking: { level: 'medium', encodeThoughtsAsText: true },
      }
    );

    // Multiple text parts are kept as a list (thought encoded as text + result)
    expect(params.messages).toEqual([
      {
        role: 'assistant',
        content: [
          { type: 'text', text: '**Thinking:** Reasoning...' },
          { type: 'text', text: 'Result' },
        ],
      },
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

    const params = buildRequestParams(
      'openai/gpt-4o:completions',
      messages,
      undefined,
      {
        thinking: { level: 'medium' },
      }
    );

    // Single text part is simplified to string
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
    const params = buildRequestParams('openai/gpt-4o', messages, undefined, {
      maxTokens: 100,
    });

    expect(params.max_completion_tokens).toBe(100);
  });

  it('includes temperature when provided', () => {
    const messages = [user('Hello')];
    const params = buildRequestParams('openai/gpt-4o', messages, undefined, {
      temperature: 0.7,
    });

    expect(params.temperature).toBe(0.7);
  });

  it('includes topP when provided', () => {
    const messages = [user('Hello')];
    const params = buildRequestParams('openai/gpt-4o', messages, undefined, {
      topP: 0.9,
    });

    expect(params.top_p).toBe(0.9);
  });

  it('includes seed when provided', () => {
    const messages = [user('Hello')];
    const params = buildRequestParams('openai/gpt-4o', messages, undefined, {
      seed: 42,
    });

    expect(params.seed).toBe(42);
  });

  it('includes stopSequences when provided', () => {
    const messages = [user('Hello')];
    const params = buildRequestParams('openai/gpt-4o', messages, undefined, {
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

describe('audio encoding', () => {
  it('throws FeatureNotSupportedError for unsupported audio format', () => {
    // Create audio with unsupported format (ogg)
    const oggAudio = {
      type: 'audio' as const,
      source: {
        type: 'base64_audio_source' as const,
        data: 'dGVzdA==', // base64 for 'test'
        mimeType: 'audio/ogg' as AudioMimeType,
      },
    };
    const messages = [user(['Listen to this', oggAudio])];

    expect(() =>
      buildRequestParams('openai/gpt-4o-audio-preview:completions', messages)
    ).toThrow(FeatureNotSupportedError);
  });

  it('throws FeatureNotSupportedError for models without audio support', () => {
    // Create valid WAV audio with proper magic bytes (RIFF....WAVE)
    const wavAudio = Audio.fromBytes(
      new Uint8Array([
        0x52,
        0x49,
        0x46,
        0x46, // 'RIFF'
        0x00,
        0x00,
        0x00,
        0x00, // file size (placeholder)
        0x57,
        0x41,
        0x56,
        0x45, // 'WAVE'
      ])
    );
    const messages = [user(['Listen to this', wavAudio])];

    // gpt-4o-mini doesn't support audio
    expect(() =>
      buildRequestParams('openai/gpt-4o-mini:completions', messages)
    ).toThrow(FeatureNotSupportedError);
  });
});
