/**
 * Tests for ContextResponse.
 */

import { describe, it, expect, vi } from 'vitest';
import { createContext } from '@/llm/context';
import { user, assistant } from '@/llm/messages';
import { ContextResponse } from '@/llm/responses/context-response';
import { createUsage } from '@/llm/responses/usage';

// Mock the provider registry to return our mock provider
vi.mock('@/llm/providers/registry', () => ({
  getProviderForModel: vi.fn(),
}));

import { getProviderForModel } from '@/llm/providers/registry';

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
      const mockProvider = {
        contextCall: vi.fn(),
      };
      vi.mocked(getProviderForModel).mockReturnValue(mockProvider as never);

      const response = createTestResponse();

      expect(response.providerId).toBe('anthropic');
      expect(response.modelId).toBe('anthropic/claude-sonnet-4-20250514');
      expect(response.text()).toBe('Hello!');
      expect(response.finishReason).toBeNull();
      expect(response.usage).toBe(mockUsage);
    });
  });

  describe('executeTools()', () => {
    it('returns empty array (tools not yet implemented)', () => {
      const mockProvider = {
        contextCall: vi.fn(),
      };
      vi.mocked(getProviderForModel).mockReturnValue(mockProvider as never);

      const response = createTestResponse();
      const ctx = createContext<TestDeps>({ userId: '123' });

      const outputs = response.executeTools(ctx);

      expect(outputs).toEqual([]);
    });
  });
});
