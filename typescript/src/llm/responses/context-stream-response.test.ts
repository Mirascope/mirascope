/**
 * Tests for ContextStreamResponse.
 */

import { describe, it, expect, vi } from 'vitest';
import type { ToolCall } from '@/llm/content/tool-call';
import {
  textStart,
  textChunk,
  textEnd,
  toolCallStart,
  toolCallChunk,
  toolCallEnd,
} from '@/llm/content';
import { createContext, type Context } from '@/llm/context';
import { user } from '@/llm/messages';
import { ContextStreamResponse } from '@/llm/responses/context-stream-response';
import type { StreamResponseChunk } from '@/llm/responses/chunks';
import { defineTool, defineContextTool, ContextToolkit } from '@/llm/tools';
import type { ToolParameterSchema } from '@/llm/tools/tool-schema';

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

  // Helper to create a mock schema
  function createMockSchema(
    properties: Record<string, { type: string }>,
    required: string[] = []
  ): ToolParameterSchema {
    return {
      type: 'object',
      properties,
      required,
      additionalProperties: false,
    };
  }

  describe('constructor', () => {
    it('inherits properties from StreamResponse', async () => {
      const response = createTestStreamResponse();

      expect(response.providerId).toBe('anthropic');
      expect(response.modelId).toBe('anthropic/claude-sonnet-4-20250514');

      // Consume stream to get text
      await response.consume();
      expect(response.text()).toBe('Hello!');
    });

    it('accepts ContextToolkit directly', () => {
      const schema = createMockSchema({ value: { type: 'string' } }, ['value']);

      const tool = defineContextTool<{ value: string }, TestDeps>({
        name: 'test_tool',
        description: 'Test tool',
        tool: (ctx, { value }) => `${ctx.deps.userId}: ${value}`,
        __schema: schema,
      });

      const toolkit = new ContextToolkit<TestDeps>([tool]);

      const chunks = [textStart(), textChunk('Hello!'), textEnd()];
      const response = new ContextStreamResponse<TestDeps>({
        providerId: 'anthropic',
        modelId: 'anthropic/claude-sonnet-4-20250514',
        providerModelName: 'claude-sonnet-4-20250514',
        params: {},
        inputMessages: [user('Hi')],
        chunkIterator: createMockChunkIterator(chunks),
        tools: toolkit,
      });

      expect(response.contextToolkit).toBe(toolkit);
    });
  });

  describe('executeTools', () => {
    it('executes context tools with context after consuming stream', async () => {
      const toolFn = vi.fn(
        (ctx: Context<TestDeps>, args: { query: string }) =>
          `${ctx.deps.userId} searched: ${args.query}`
      );

      const searchTool = defineContextTool<{ query: string }, TestDeps>({
        name: 'search',
        description: 'Search',
        tool: toolFn,
        __schema: createMockSchema({ query: { type: 'string' } }, ['query']),
      });

      const toolCall: ToolCall = {
        type: 'tool_call',
        id: 'call-1',
        name: 'search',
        args: JSON.stringify({ query: 'test' }),
      };

      const chunks: StreamResponseChunk[] = [
        textStart(),
        textChunk('I will search.'),
        textEnd(),
        toolCallStart(toolCall.id, toolCall.name),
        toolCallChunk(toolCall.id, toolCall.args),
        toolCallEnd(toolCall.id),
      ];

      const response = new ContextStreamResponse<TestDeps>({
        providerId: 'anthropic',
        modelId: 'anthropic/claude-sonnet-4-20250514',
        providerModelName: 'claude-sonnet-4-20250514',
        params: {},
        inputMessages: [user('Hi')],
        chunkIterator: createMockChunkIterator(chunks),
        tools: [searchTool],
      });

      // Consume stream first
      await response.consume();

      const ctx = createContext<TestDeps>({ userId: 'user-123' });
      const outputs = await response.executeTools(ctx);

      expect(outputs).toHaveLength(1);
      expect(outputs[0]?.result).toBe('user-123 searched: test');
      expect(outputs[0]?.error).toBeNull();
      expect(toolFn).toHaveBeenCalledWith(ctx, { query: 'test' });
    });

    it('executes mixed tools polymorphically', async () => {
      const regularFn = vi.fn(({ a, b }: { a: number; b: number }) => a + b);
      const contextFn = vi.fn(
        (ctx: Context<TestDeps>, { value }: { value: number }) =>
          value * parseInt(ctx.deps.userId, 10)
      );

      const addTool = defineTool<{ a: number; b: number }>({
        name: 'add',
        description: 'Add numbers',
        tool: regularFn,
        __schema: createMockSchema(
          { a: { type: 'number' }, b: { type: 'number' } },
          ['a', 'b']
        ),
      });

      const multiplyTool = defineContextTool<{ value: number }, TestDeps>({
        name: 'multiply',
        description: 'Multiply',
        tool: contextFn,
        __schema: createMockSchema({ value: { type: 'number' } }, ['value']),
      });

      const addCall: ToolCall = {
        type: 'tool_call',
        id: 'call-1',
        name: 'add',
        args: JSON.stringify({ a: 5, b: 3 }),
      };

      const multiplyCall: ToolCall = {
        type: 'tool_call',
        id: 'call-2',
        name: 'multiply',
        args: JSON.stringify({ value: 7 }),
      };

      const chunks: StreamResponseChunk[] = [
        toolCallStart(addCall.id, addCall.name),
        toolCallChunk(addCall.id, addCall.args),
        toolCallEnd(addCall.id),
        toolCallStart(multiplyCall.id, multiplyCall.name),
        toolCallChunk(multiplyCall.id, multiplyCall.args),
        toolCallEnd(multiplyCall.id),
      ];

      const response = new ContextStreamResponse<TestDeps>({
        providerId: 'anthropic',
        modelId: 'anthropic/claude-sonnet-4-20250514',
        providerModelName: 'claude-sonnet-4-20250514',
        params: {},
        inputMessages: [user('Hi')],
        chunkIterator: createMockChunkIterator(chunks),
        tools: [addTool, multiplyTool],
      });

      // Consume stream first
      await response.consume();

      const ctx = createContext<TestDeps>({ userId: '10' });
      const outputs = await response.executeTools(ctx);

      expect(outputs).toHaveLength(2);
      // Regular tool - context not passed
      expect(outputs[0]?.result).toBe(8);
      expect(regularFn).toHaveBeenCalledWith({ a: 5, b: 3 });
      // Context tool - context passed
      expect(outputs[1]?.result).toBe(70); // 7 * 10
      expect(contextFn).toHaveBeenCalledWith(ctx, { value: 7 });
    });
  });
});
