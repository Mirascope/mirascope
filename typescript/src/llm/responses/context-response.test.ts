/**
 * Tests for ContextResponse.
 */

import { describe, it, expect, vi } from 'vitest';
import type { ToolCall } from '@/llm/content/tool-call';
import { user, assistant } from '@/llm/messages';
import { ContextResponse } from '@/llm/responses/context-response';
import { createUsage } from '@/llm/responses/usage';
import { defineTool, defineContextTool, ContextToolkit } from '@/llm/tools';
import type { Context } from '@/llm/context';
import type { ToolParameterSchema } from '@/llm/tools/tool-schema';

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

    it('accepts ContextToolkit directly', () => {
      const schema: ToolParameterSchema = {
        type: 'object',
        properties: { value: { type: 'string' } },
        required: ['value'],
        additionalProperties: false,
      };

      const tool = defineContextTool<{ value: string }, TestDeps>({
        name: 'test_tool',
        description: 'Test tool',
        tool: (ctx, { value }) => `${ctx.deps.userId}: ${value}`,
        __schema: schema,
      });

      const toolkit = new ContextToolkit<TestDeps>([tool]);

      const response = new ContextResponse<TestDeps>({
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

      expect(response.contextToolkit).toBe(toolkit);
    });
  });

  describe('executeTools', () => {
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

    it('executes context tools with context', async () => {
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

      const assistantWithToolCall = assistant(
        [{ type: 'text', text: 'I will search.' }, toolCall],
        {
          providerId: 'anthropic',
          modelId: 'anthropic/claude-sonnet-4-20250514',
          providerModelName: 'claude-sonnet-4-20250514',
        }
      );

      const response = new ContextResponse<TestDeps>({
        raw: { test: 'raw' },
        providerId: 'anthropic',
        modelId: 'anthropic/claude-sonnet-4-20250514',
        providerModelName: 'claude-sonnet-4-20250514',
        params: {},
        inputMessages: [user('Hi')],
        assistantMessage: assistantWithToolCall,
        finishReason: null,
        usage: mockUsage,
        tools: [searchTool],
      });

      const ctx: Context<TestDeps> = { deps: { userId: 'user-123' } };
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

      const assistantWithToolCalls = assistant([addCall, multiplyCall], {
        providerId: 'anthropic',
        modelId: 'anthropic/claude-sonnet-4-20250514',
        providerModelName: 'claude-sonnet-4-20250514',
      });

      const response = new ContextResponse<TestDeps>({
        raw: { test: 'raw' },
        providerId: 'anthropic',
        modelId: 'anthropic/claude-sonnet-4-20250514',
        providerModelName: 'claude-sonnet-4-20250514',
        params: {},
        inputMessages: [user('Hi')],
        assistantMessage: assistantWithToolCalls,
        finishReason: null,
        usage: mockUsage,
        tools: [addTool, multiplyTool],
      });

      const ctx: Context<TestDeps> = { deps: { userId: '10' } };
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
