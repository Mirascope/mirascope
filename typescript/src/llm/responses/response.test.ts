/**
 * Tests for Response.
 */

import { describe, it, expect, vi } from 'vitest';
import { user, assistant } from '@/llm/messages';
import { Response } from '@/llm/responses/response';
import { createUsage } from '@/llm/responses/usage';
import { defineTool, Toolkit } from '@/llm/tools';

describe('Response', () => {
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

  describe('constructor', () => {
    it('accepts Toolkit directly', () => {
      const searchFn = vi.fn(
        ({ query }: { query: string }) => `searched: ${query}`
      );
      const searchTool = defineTool({
        name: 'search',
        description: 'Search for something',
        tool: searchFn,
        __schema: {
          type: 'object',
          properties: { query: { type: 'string' } },
          required: ['query'],
          additionalProperties: false,
        },
      });
      const toolkit = new Toolkit([searchTool]);

      const response = new Response({
        raw: { test: 'raw' },
        providerId: 'anthropic',
        modelId: 'anthropic/claude-sonnet-4-20250514',
        providerModelName: 'claude-sonnet-4-20250514',
        params: {},
        inputMessages: [user('Hi')],
        assistantMessage: mockAssistantMessage,
        finishReason: null,
        usage: mockUsage,
        tools: toolkit,
      });

      expect(response.toolkit).toBe(toolkit);
    });
  });
});
