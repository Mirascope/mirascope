/**
 * Unit tests for OpenAI Responses provider utilities.
 *
 * Note: Most encoding tests are covered by e2e tests in tests/e2e/.
 * These tests focus on edge cases that can't be triggered via e2e.
 */

import { describe, it, expect } from 'vitest';
import type { Response as OpenAIResponse } from 'openai/resources/responses/responses';
import { assistant } from '@/llm/messages';
import { FinishReason } from '@/llm/responses/finish-reason';
import { encodeMessages, decodeResponse } from './_utils';

describe('encodeMessages edge cases', () => {
  it('encodes assistant message with empty content', () => {
    const messages = [
      assistant([], { providerId: 'openai', modelId: 'openai/gpt-4o' }),
    ];
    const encoded = encodeMessages(messages);

    expect(encoded).toEqual([{ role: 'assistant', content: '' }]);
  });
});

describe('decodeResponse', () => {
  const createMockResponse = (
    overrides: Partial<OpenAIResponse> = {}
  ): OpenAIResponse =>
    ({
      id: 'resp_123',
      object: 'response',
      created_at: 1677652288,
      model: 'gpt-4o',
      output: [
        {
          type: 'message',
          id: 'msg_123',
          status: 'completed',
          role: 'assistant',
          content: [{ type: 'output_text', text: 'Hello!', annotations: [] }],
        },
      ],
      status: 'completed',
      usage: {
        input_tokens: 5,
        output_tokens: 2,
        total_tokens: 7,
      },
      ...overrides,
    }) as OpenAIResponse;

  it('decodes refusal message as text content', () => {
    const response = createMockResponse({
      output: [
        {
          type: 'message',
          id: 'msg_123',
          status: 'completed',
          role: 'assistant',
          content: [
            {
              type: 'refusal',
              refusal: "I can't help with that request.",
            },
          ],
        },
      ],
    });

    const decoded = decodeResponse(response, 'openai/gpt-4o');

    expect(decoded.assistantMessage.content).toEqual([
      { type: 'text', text: "I can't help with that request." },
    ]);
    expect(decoded.finishReason).toBe(FinishReason.REFUSAL);
  });

  it('maps max_output_tokens incomplete reason to MAX_TOKENS', () => {
    const response = createMockResponse({
      output: [
        {
          type: 'message',
          id: 'msg_123',
          status: 'incomplete',
          role: 'assistant',
          content: [
            { type: 'output_text', text: 'Partial...', annotations: [] },
          ],
        },
      ],
      status: 'incomplete',
      incomplete_details: {
        reason: 'max_output_tokens',
      },
    });

    const decoded = decodeResponse(response, 'openai/gpt-4o');

    expect(decoded.finishReason).toBe(FinishReason.MAX_TOKENS);
  });

  it('maps content_filter incomplete reason to REFUSAL', () => {
    const response = createMockResponse({
      output: [
        {
          type: 'message',
          id: 'msg_123',
          status: 'incomplete',
          role: 'assistant',
          content: [{ type: 'output_text', text: '', annotations: [] }],
        },
      ],
      status: 'incomplete',
      incomplete_details: {
        reason: 'content_filter',
      },
    });

    const decoded = decodeResponse(response, 'openai/gpt-4o');

    expect(decoded.finishReason).toBe(FinishReason.REFUSAL);
  });

  it('handles response without usage', () => {
    const response = createMockResponse();
    delete (response as { usage?: unknown }).usage;

    const decoded = decodeResponse(response, 'openai/gpt-4o');

    expect(decoded.usage).toBeNull();
  });
});
