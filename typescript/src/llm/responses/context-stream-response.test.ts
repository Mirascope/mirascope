/**
 * Tests for ContextStreamResponse.
 */

import { describe, it, expect, vi } from 'vitest';
import { createContext } from '@/llm/context';
import { user } from '@/llm/messages';
import { ContextStreamResponse } from '@/llm/responses/context-stream-response';
import { textStart, textChunk, textEnd } from '@/llm/responses/chunks';
import type { StreamResponseChunk } from '@/llm/responses/chunks';

// Mock the provider registry to return our mock provider
vi.mock('@/llm/providers/registry', () => ({
  getProviderForModel: vi.fn(),
}));

import { getProviderForModel } from '@/llm/providers/registry';

describe('ContextStreamResponse', () => {
  interface TestDeps {
    userId: string;
  }

  function createMockChunkIterator(
    chunks: StreamResponseChunk[]
  ): AsyncIterator<StreamResponseChunk> {
    let index = 0;
    return {
      next(): Promise<IteratorResult<StreamResponseChunk>> {
        if (index < chunks.length) {
          return Promise.resolve({ done: false, value: chunks[index++]! });
        }
        return Promise.resolve({ done: true, value: undefined });
      },
    };
  }

  function createTestStreamResponse(): ContextStreamResponse<TestDeps> {
    const chunks = [textStart(), textChunk('Hello!'), textEnd()];
    return new ContextStreamResponse({
      providerId: 'anthropic',
      modelId: 'anthropic/claude-sonnet-4-20250514',
      providerModelName: 'claude-sonnet-4-20250514',
      params: { temperature: 0.5 },
      inputMessages: [user('Hi')],
      chunkIterator: createMockChunkIterator(chunks),
    });
  }

  describe('constructor', () => {
    it('inherits properties from StreamResponse', async () => {
      const mockProvider = {
        contextStream: vi.fn(),
      };
      vi.mocked(getProviderForModel).mockReturnValue(mockProvider as never);

      const response = createTestStreamResponse();

      expect(response.providerId).toBe('anthropic');
      expect(response.modelId).toBe('anthropic/claude-sonnet-4-20250514');

      // Consume stream to get text
      await response.consume();
      expect(response.text()).toBe('Hello!');
    });
  });

  describe('executeTools()', () => {
    it('returns empty array (tools not yet implemented)', async () => {
      const mockProvider = {
        contextStream: vi.fn(),
      };
      vi.mocked(getProviderForModel).mockReturnValue(mockProvider as never);

      const response = createTestStreamResponse();
      await response.consume();
      const ctx = createContext<TestDeps>({ userId: '123' });

      const outputs = response.executeTools(ctx);

      expect(outputs).toEqual([]);
    });
  });
});
