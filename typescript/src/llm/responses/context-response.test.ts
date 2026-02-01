/**
 * Tests for ContextResponse.
 */

import { describe, it, expect } from 'vitest';
import { user, assistant } from '@/llm/messages';
import { ContextResponse } from '@/llm/responses/context-response';
import { createUsage } from '@/llm/responses/usage';

describe('ContextResponse', () => {
  interface TestDeps {
    userId: string;
  }

  const mockAssistantMessage = assistant([{ type: 'text', text: 'Hello!' }], {
    providerId: 'anthropic',
    modelId: 'anthropic/claude-sonnet-4-20250514',
    providerModelName: 'claude-sonnet-4-20250514',
  });
  const mockUsage = createUsage({
    inputTokens: 10,
    outputTokens: 5,
    cacheReadTokens: 0,
    cacheWriteTokens: 0,
    reasoningTokens: 0,
    raw: null,
  });

  function createTestResponse(): ContextResponse<TestDeps> {
    return new ContextResponse({
      raw: { test: 'raw' },
      providerId: 'anthropic',
      modelId: 'anthropic/claude-sonnet-4-20250514',
      providerModelName: 'claude-sonnet-4-20250514',
      params: { temperature: 0.5 },
      inputMessages: [user('Hi')],
      assistantMessage: mockAssistantMessage,
      finishReason: null,
      usage: mockUsage,
    });
  }

  describe('constructor', () => {
    it('inherits properties from BaseResponse', () => {
      const response = createTestResponse();

      expect(response.providerId).toBe('anthropic');
      expect(response.modelId).toBe('anthropic/claude-sonnet-4-20250514');
      expect(response.text()).toBe('Hello!');
      expect(response.finishReason).toBeNull();
      expect(response.usage).toBe(mockUsage);
    });
  });
});
