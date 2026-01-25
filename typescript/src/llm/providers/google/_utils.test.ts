/**
 * Unit tests for Google provider utilities.
 *
 * Note: Most encoding tests are covered by e2e tests in tests/e2e/input/.
 * These tests focus on error cases that can't be tested via successful API calls.
 */

import { describe, it, expect } from 'vitest';
import type { GenerateContentResponse, Part } from '@google/genai';
import { assistant, system, user } from '@/llm/messages';
import {
  AuthenticationError,
  PermissionError,
  NotFoundError,
  RateLimitError,
  BadRequestError,
  ServerError,
  APIError,
} from '@/llm/exceptions';
import {
  buildRequestParams,
  decodeResponse,
  encodeMessages,
  mapGoogleErrorByStatus,
} from './_utils';

describe('encodeMessages', () => {
  it('encodes system message as systemInstruction', () => {
    const messages = [system('You are helpful'), user('Hello')];

    const result = encodeMessages(messages);

    expect(result.systemInstruction).toBe('You are helpful');
    expect(result.contents).toHaveLength(1);
    expect(result.contents[0]?.role).toBe('user');
  });

  it('maps assistant role to model', () => {
    const messages = [
      user('Hello'),
      assistant('Hi there!', { modelId: null, providerId: null }),
    ];

    const result = encodeMessages(messages);

    expect(result.contents).toHaveLength(2);
    expect(result.contents[0]?.role).toBe('user');
    expect(result.contents[1]?.role).toBe('model');
  });

  it('handles multiple text parts in user content', () => {
    const messages = [
      user([
        { type: 'text', text: 'Part 1' },
        { type: 'text', text: 'Part 2' },
      ]),
    ];

    const result = encodeMessages(messages);

    expect(result.contents[0]?.parts).toHaveLength(2);
    expect(result.contents[0]?.parts?.[0]).toEqual({ text: 'Part 1' });
    expect(result.contents[0]?.parts?.[1]).toEqual({ text: 'Part 2' });
  });
});

describe('buildRequestParams', () => {
  it('sets default maxOutputTokens', () => {
    const messages = [user('Hello')];

    const result = buildRequestParams('google/gemini-2.0-flash', messages);

    expect(result.config?.maxOutputTokens).toBe(8192);
  });

  it('maps maxTokens to maxOutputTokens', () => {
    const messages = [user('Hello')];

    const result = buildRequestParams('google/gemini-2.0-flash', messages, {
      maxTokens: 100,
    });

    expect(result.config?.maxOutputTokens).toBe(100);
  });

  it('supports seed parameter', () => {
    const messages = [user('Hello')];

    const result = buildRequestParams('google/gemini-2.0-flash', messages, {
      seed: 42,
    });

    expect(result.config?.seed).toBe(42);
  });

  it('supports temperature parameter', () => {
    const messages = [user('Hello')];

    const result = buildRequestParams('google/gemini-2.0-flash', messages, {
      temperature: 0.7,
    });

    expect(result.config?.temperature).toBe(0.7);
  });

  it('supports topP parameter', () => {
    const messages = [user('Hello')];

    const result = buildRequestParams('google/gemini-2.0-flash', messages, {
      topP: 0.9,
    });

    expect(result.config?.topP).toBe(0.9);
  });

  it('supports topK parameter', () => {
    const messages = [user('Hello')];

    const result = buildRequestParams('google/gemini-2.0-flash', messages, {
      topK: 40,
    });

    expect(result.config?.topK).toBe(40);
  });

  it('includes systemInstruction when system message present', () => {
    const messages = [system('You are helpful'), user('Hello')];

    const result = buildRequestParams('google/gemini-2.0-flash', messages);

    expect(result.config?.systemInstruction).toBe('You are helpful');
  });

  it('strips google/ prefix from model name', () => {
    const messages = [user('Hello')];

    const result = buildRequestParams('google/gemini-2.0-flash', messages);

    expect(result.model).toBe('gemini-2.0-flash');
  });

  it('supports stopSequences parameter', () => {
    const messages = [user('Hello')];

    const result = buildRequestParams('google/gemini-2.0-flash', messages, {
      stopSequences: ['STOP', 'END'],
    });

    expect(result.config?.stopSequences).toEqual(['STOP', 'END']);
  });
});

describe('decodeResponse', () => {
  it('decodes text response', () => {
    const response = {
      candidates: [
        {
          content: {
            parts: [{ text: 'Hello world!' }],
            role: 'model',
          },
          finishReason: 'STOP',
        },
      ],
      usageMetadata: {
        promptTokenCount: 10,
        candidatesTokenCount: 5,
      },
    } as unknown as GenerateContentResponse;

    const result = decodeResponse(response, 'google/gemini-2.0-flash');

    expect(result.assistantMessage.content).toHaveLength(1);
    expect(result.assistantMessage.content[0]).toEqual({
      type: 'text',
      text: 'Hello world!',
    });
    expect(result.finishReason).toBeNull(); // STOP is normal completion
  });

  it('decodes MAX_TOKENS finish reason', () => {
    const response = {
      candidates: [
        {
          content: {
            parts: [{ text: 'Truncated...' }],
            role: 'model',
          },
          finishReason: 'MAX_TOKENS',
        },
      ],
      usageMetadata: {
        promptTokenCount: 10,
        candidatesTokenCount: 5,
      },
    } as unknown as GenerateContentResponse;

    const result = decodeResponse(response, 'google/gemini-2.0-flash');

    expect(result.finishReason).toBe('max_tokens');
  });

  it('decodes safety refusals', () => {
    const safetyReasons = [
      'SAFETY',
      'RECITATION',
      'BLOCKLIST',
      'PROHIBITED_CONTENT',
      'SPII',
    ];

    for (const reason of safetyReasons) {
      const response = {
        candidates: [
          {
            content: { parts: [] as Part[], role: 'model' },
            finishReason: reason,
          },
        ],
        usageMetadata: {},
      } as unknown as GenerateContentResponse;

      const result = decodeResponse(response, 'google/gemini-2.0-flash');
      expect(result.finishReason).toBe('refusal');
    }
  });

  it('extracts usage metadata', () => {
    const response = {
      candidates: [
        {
          content: { parts: [{ text: 'Hi' }], role: 'model' },
          finishReason: 'STOP',
        },
      ],
      usageMetadata: {
        promptTokenCount: 100,
        candidatesTokenCount: 50,
        cachedContentTokenCount: 10,
        thoughtsTokenCount: 5,
      },
    } as unknown as GenerateContentResponse;

    const result = decodeResponse(response, 'google/gemini-2.0-flash');

    expect(result.usage).not.toBeNull();
    expect(result.usage?.inputTokens).toBe(100);
    expect(result.usage?.outputTokens).toBe(55); // 50 + 5 thoughts
    expect(result.usage?.cacheReadTokens).toBe(10);
    expect(result.usage?.reasoningTokens).toBe(5);
  });

  it('handles empty candidates', () => {
    const response = {
      candidates: [],
      usageMetadata: {
        promptTokenCount: 10,
        candidatesTokenCount: 0,
      },
    } as unknown as GenerateContentResponse;

    const result = decodeResponse(response, 'google/gemini-2.0-flash');

    expect(result.assistantMessage.content).toHaveLength(0);
  });

  it('sets provider metadata on assistant message', () => {
    const response = {
      candidates: [
        {
          content: { parts: [{ text: 'Hello' }], role: 'model' },
          finishReason: 'STOP',
        },
      ],
      modelVersion: 'gemini-2.0-flash-exp',
      usageMetadata: {},
    } as unknown as GenerateContentResponse;

    const result = decodeResponse(response, 'google/gemini-2.0-flash');

    expect(result.assistantMessage.providerId).toBe('google');
    expect(result.assistantMessage.modelId).toBe('google/gemini-2.0-flash');
    expect(result.assistantMessage.providerModelName).toBe(
      'gemini-2.0-flash-exp'
    );
  });
});

describe('mapGoogleErrorByStatus', () => {
  it('maps 401 to AuthenticationError', () => {
    expect(mapGoogleErrorByStatus(401)).toBe(AuthenticationError);
  });

  it('maps 403 to PermissionError', () => {
    expect(mapGoogleErrorByStatus(403)).toBe(PermissionError);
  });

  it('maps 404 to NotFoundError', () => {
    expect(mapGoogleErrorByStatus(404)).toBe(NotFoundError);
  });

  it('maps 429 to RateLimitError', () => {
    expect(mapGoogleErrorByStatus(429)).toBe(RateLimitError);
  });

  it('maps 400 to BadRequestError', () => {
    expect(mapGoogleErrorByStatus(400)).toBe(BadRequestError);
  });

  it('maps 422 to BadRequestError', () => {
    expect(mapGoogleErrorByStatus(422)).toBe(BadRequestError);
  });

  it('maps 5xx to ServerError', () => {
    expect(mapGoogleErrorByStatus(500)).toBe(ServerError);
    expect(mapGoogleErrorByStatus(502)).toBe(ServerError);
    expect(mapGoogleErrorByStatus(503)).toBe(ServerError);
  });

  it('maps unknown status codes to APIError', () => {
    expect(mapGoogleErrorByStatus(418)).toBe(APIError);
    expect(mapGoogleErrorByStatus(499)).toBe(APIError);
  });
});
