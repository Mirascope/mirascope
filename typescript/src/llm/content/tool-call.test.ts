import { describe, expect, it } from 'vitest';

import type { ToolCall } from '@/llm/content/tool-call';

describe('ToolCall', () => {
  it('has correct type discriminator', () => {
    const toolCall: ToolCall = {
      type: 'tool_call',
      id: 'call_123',
      name: 'get_weather',
      args: '{"location": "NYC"}',
    };
    expect(toolCall.type).toBe('tool_call');
  });

  it('stores tool call id', () => {
    const toolCall: ToolCall = {
      type: 'tool_call',
      id: 'call_abc123',
      name: 'calculator',
      args: '{}',
    };
    expect(toolCall.id).toBe('call_abc123');
  });

  it('stores tool name', () => {
    const toolCall: ToolCall = {
      type: 'tool_call',
      id: 'id',
      name: 'search_web',
      args: '{}',
    };
    expect(toolCall.name).toBe('search_web');
  });

  it('stores stringified JSON args', () => {
    const args = JSON.stringify({ query: 'test', limit: 10 });
    const toolCall: ToolCall = {
      type: 'tool_call',
      id: 'id',
      name: 'search',
      args,
    };
    expect(toolCall.args).toBe('{"query":"test","limit":10}');
    expect(JSON.parse(toolCall.args)).toEqual({ query: 'test', limit: 10 });
  });

  it('supports empty args', () => {
    const toolCall: ToolCall = {
      type: 'tool_call',
      id: 'id',
      name: 'no_args_tool',
      args: '{}',
    };
    expect(toolCall.args).toBe('{}');
  });
});
