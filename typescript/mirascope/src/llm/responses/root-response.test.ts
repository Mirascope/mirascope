/**
 * Tests for RootResponse.
 */

import { describe, it, expect } from 'vitest';
import type {
  AssistantContentPart,
  Text,
  Thought,
  ToolCall,
} from '@/llm/content';
import type { Message } from '@/llm/messages';
import type { Params } from '@/llm/models';
import type { ModelId, ProviderId } from '@/llm/providers';
import type { FinishReason } from '@/llm/responses/finish-reason';
import type { Usage } from '@/llm/responses/usage';
import { RootResponse } from '@/llm/responses/root-response';

// Concrete implementation for testing
class TestResponse extends RootResponse {
  readonly raw: unknown;
  readonly providerId: ProviderId;
  readonly modelId: ModelId;
  readonly providerModelName: string;
  readonly params: Params;
  readonly messages: readonly Message[];
  readonly content: readonly AssistantContentPart[];
  readonly texts: readonly Text[];
  readonly toolCalls: readonly ToolCall[];
  readonly thoughts: readonly Thought[];
  readonly finishReason: FinishReason | null;
  readonly usage: Usage | null;

  constructor(content: readonly AssistantContentPart[]) {
    super();
    this.raw = {};
    this.providerId = 'anthropic';
    this.modelId = 'anthropic/claude-sonnet-4-20250514';
    this.providerModelName = 'claude-sonnet-4-20250514';
    this.params = {};
    this.messages = [];
    this.content = content;
    this.texts = content.filter((c): c is Text => c.type === 'text');
    this.toolCalls = content.filter(
      (c): c is ToolCall => c.type === 'tool_call'
    );
    this.thoughts = content.filter((c): c is Thought => c.type === 'thought');
    this.finishReason = null;
    this.usage = null;
  }
}

describe('RootResponse', () => {
  describe('text()', () => {
    it('returns empty string when no text content', () => {
      const response = new TestResponse([]);
      expect(response.text()).toBe('');
    });

    it('returns single text content', () => {
      const response = new TestResponse([{ type: 'text', text: 'Hello!' }]);
      expect(response.text()).toBe('Hello!');
    });

    it('joins multiple text parts with newline by default', () => {
      const response = new TestResponse([
        { type: 'text', text: 'Hello' },
        { type: 'text', text: 'World' },
      ]);
      expect(response.text()).toBe('Hello\nWorld');
    });

    it('joins with custom separator', () => {
      const response = new TestResponse([
        { type: 'text', text: 'Hello' },
        { type: 'text', text: 'World' },
      ]);
      expect(response.text(' ')).toBe('Hello World');
      expect(response.text('')).toBe('HelloWorld');
    });
  });

  describe('pretty()', () => {
    it('returns empty string for empty content', () => {
      const response = new TestResponse([]);
      expect(response.pretty()).toBe('');
    });

    it('formats text content', () => {
      const response = new TestResponse([{ type: 'text', text: 'Hello!' }]);
      expect(response.pretty()).toBe('Hello!');
    });

    it('formats tool call content', () => {
      const response = new TestResponse([
        {
          type: 'tool_call',
          id: 'call_1',
          name: 'calculator',
          args: '{"a": 1, "b": 2}',
        },
      ]);
      expect(response.pretty()).toBe(
        '**ToolCall (calculator):** {"a": 1, "b": 2}'
      );
    });

    it('formats thought content with indentation', () => {
      const response = new TestResponse([
        {
          type: 'thought',
          thought: 'Let me think about this.\nIt seems complex.',
        },
      ]);
      expect(response.pretty()).toBe(
        '**Thinking:**\n  Let me think about this.\n  It seems complex.'
      );
    });

    it('formats mixed content with double newlines', () => {
      const response = new TestResponse([
        { type: 'thought', thought: 'Thinking first' },
        {
          type: 'tool_call',
          id: 'call_1',
          name: 'calc',
          args: '{"op": "add"}',
        },
        { type: 'text', text: 'Here is my answer!' },
      ]);

      const expected = [
        '**Thinking:**\n  Thinking first',
        '**ToolCall (calc):** {"op": "add"}',
        'Here is my answer!',
      ].join('\n\n');

      expect(response.pretty()).toBe(expected);
    });
  });
});
