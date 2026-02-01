import { describe, expect, it } from 'vitest';
import {
  TextStream,
  ThoughtStream,
  ToolCallStream,
} from '@/llm/responses/streams';
import { StreamResponse } from '@/llm/responses/stream-response';
import type { TextChunk, ThoughtChunk, ToolCallChunk } from '@/llm/content';
import type { StreamResponseChunk } from '@/llm/responses/chunks';
import { FinishReason } from '@/llm/responses/finish-reason';

/**
 * Helper to create async iterator from array
 */
// eslint-disable-next-line @typescript-eslint/require-await
async function* arrayToAsyncIterator<T>(
  items: T[]
): AsyncGenerator<T, void, undefined> {
  for (const item of items) {
    yield item;
  }
}

/**
 * Helper to create a minimal StreamResponse for testing
 */
function createTestStreamResponse(
  chunks: StreamResponseChunk[]
): StreamResponse {
  const iterator = arrayToAsyncIterator(chunks);
  return new StreamResponse({
    providerId: 'anthropic',
    modelId: 'anthropic/claude-sonnet-4-20250514',
    providerModelName: 'claude-sonnet-4-20250514',
    params: {},
    inputMessages: [],
    chunkIterator: iterator,
  });
}

describe('TextStream', () => {
  it('iterates over text deltas and accumulates partialText', async () => {
    const chunks: TextChunk[] = [
      { type: 'text_chunk', contentType: 'text', delta: 'Hello ' },
      { type: 'text_chunk', contentType: 'text', delta: 'World!' },
    ];

    const stream = new TextStream(arrayToAsyncIterator(chunks));

    expect(stream.type).toBe('text_stream');
    expect(stream.contentType).toBe('text');
    expect(stream.partialText).toBe('');

    const deltas: string[] = [];
    for await (const delta of stream) {
      deltas.push(delta);
    }

    expect(deltas).toEqual(['Hello ', 'World!']);
    expect(stream.partialText).toBe('Hello World!');
  });

  it('collect() consumes stream and returns Text object', async () => {
    const chunks: TextChunk[] = [
      { type: 'text_chunk', contentType: 'text', delta: 'Complete ' },
      { type: 'text_chunk', contentType: 'text', delta: 'text.' },
    ];

    const stream = new TextStream(arrayToAsyncIterator(chunks));
    const result = await stream.collect();

    expect(result).toEqual({ type: 'text', text: 'Complete text.' });
    expect(stream.partialText).toBe('Complete text.');
  });

  it('handles empty stream', async () => {
    const chunks: TextChunk[] = [];
    const stream = new TextStream(arrayToAsyncIterator(chunks));

    const result = await stream.collect();

    expect(result).toEqual({ type: 'text', text: '' });
    expect(stream.partialText).toBe('');
  });
});

describe('ThoughtStream', () => {
  it('iterates over thought deltas and accumulates partialThought', async () => {
    const chunks: ThoughtChunk[] = [
      { type: 'thought_chunk', contentType: 'thought', delta: 'Let me ' },
      { type: 'thought_chunk', contentType: 'thought', delta: 'think...' },
    ];

    const stream = new ThoughtStream(arrayToAsyncIterator(chunks));

    expect(stream.type).toBe('thought_stream');
    expect(stream.contentType).toBe('thought');
    expect(stream.partialThought).toBe('');

    const deltas: string[] = [];
    for await (const delta of stream) {
      deltas.push(delta);
    }

    expect(deltas).toEqual(['Let me ', 'think...']);
    expect(stream.partialThought).toBe('Let me think...');
  });

  it('collect() consumes stream and returns Thought object', async () => {
    const chunks: ThoughtChunk[] = [
      { type: 'thought_chunk', contentType: 'thought', delta: 'Deep ' },
      { type: 'thought_chunk', contentType: 'thought', delta: 'thinking.' },
    ];

    const stream = new ThoughtStream(arrayToAsyncIterator(chunks));
    const result = await stream.collect();

    expect(result).toEqual({ type: 'thought', thought: 'Deep thinking.' });
    expect(stream.partialThought).toBe('Deep thinking.');
  });

  it('handles empty stream', async () => {
    const chunks: ThoughtChunk[] = [];
    const stream = new ThoughtStream(arrayToAsyncIterator(chunks));

    const result = await stream.collect();

    expect(result).toEqual({ type: 'thought', thought: '' });
    expect(stream.partialThought).toBe('');
  });
});

describe('ToolCallStream', () => {
  it('iterates over tool call deltas and accumulates partialArgs', async () => {
    const chunks: ToolCallChunk[] = [
      {
        type: 'tool_call_chunk',
        contentType: 'tool_call',
        id: 'call-1',
        delta: '{"query"',
      },
      {
        type: 'tool_call_chunk',
        contentType: 'tool_call',
        id: 'call-1',
        delta: ': "test"}',
      },
    ];

    const stream = new ToolCallStream(
      'call-1',
      'search',
      arrayToAsyncIterator(chunks)
    );

    expect(stream.type).toBe('tool_call_stream');
    expect(stream.contentType).toBe('tool_call');
    expect(stream.toolId).toBe('call-1');
    expect(stream.toolName).toBe('search');
    expect(stream.partialArgs).toBe('');

    const deltas: string[] = [];
    for await (const delta of stream) {
      deltas.push(delta);
    }

    expect(deltas).toEqual(['{"query"', ': "test"}']);
    expect(stream.partialArgs).toBe('{"query": "test"}');
  });

  it('collect() consumes stream and returns ToolCall object', async () => {
    const chunks: ToolCallChunk[] = [
      {
        type: 'tool_call_chunk',
        contentType: 'tool_call',
        id: 'call-2',
        delta: '{"a": 1}',
      },
    ];

    const stream = new ToolCallStream(
      'call-2',
      'calculator',
      arrayToAsyncIterator(chunks)
    );
    const result = await stream.collect();

    expect(result).toEqual({
      type: 'tool_call',
      id: 'call-2',
      name: 'calculator',
      args: '{"a": 1}',
    });
    expect(stream.partialArgs).toBe('{"a": 1}');
  });

  it('handles empty stream', async () => {
    const chunks: ToolCallChunk[] = [];
    const stream = new ToolCallStream(
      'call-3',
      'no_args_tool',
      arrayToAsyncIterator(chunks)
    );

    const result = await stream.collect();

    expect(result).toEqual({
      type: 'tool_call',
      id: 'call-3',
      name: 'no_args_tool',
      args: '',
    });
    expect(stream.partialArgs).toBe('');
  });
});

describe('StreamResponse.streams()', () => {
  it('yields TextStream for text content', async () => {
    const chunks: StreamResponseChunk[] = [
      { type: 'text_start_chunk', contentType: 'text' },
      { type: 'text_chunk', contentType: 'text', delta: 'Hello ' },
      { type: 'text_chunk', contentType: 'text', delta: 'World!' },
      { type: 'text_end_chunk', contentType: 'text' },
    ];

    const response = createTestStreamResponse(chunks);

    const streams = [];
    for await (const stream of response.streams()) {
      streams.push(stream);
      expect(stream.contentType).toBe('text');

      // Iterate through the stream
      const deltas: string[] = [];
      for await (const delta of stream) {
        deltas.push(delta);
      }
      expect(deltas).toEqual(['Hello ', 'World!']);
    }

    expect(streams).toHaveLength(1);
    expect(response.consumed).toBe(true);
  });

  it('yields ThoughtStream for thought content', async () => {
    const chunks: StreamResponseChunk[] = [
      { type: 'thought_start_chunk', contentType: 'thought' },
      { type: 'thought_chunk', contentType: 'thought', delta: 'Thinking...' },
      { type: 'thought_end_chunk', contentType: 'thought' },
    ];

    const response = createTestStreamResponse(chunks);

    const streams = [];
    for await (const stream of response.streams()) {
      streams.push(stream);
      expect(stream.contentType).toBe('thought');

      const deltas: string[] = [];
      for await (const delta of stream) {
        deltas.push(delta);
      }
      expect(deltas).toEqual(['Thinking...']);
    }

    expect(streams).toHaveLength(1);
  });

  it('yields ToolCallStream for tool call content', async () => {
    const chunks: StreamResponseChunk[] = [
      {
        type: 'tool_call_start_chunk',
        contentType: 'tool_call',
        id: 'call-1',
        name: 'search',
      },
      {
        type: 'tool_call_chunk',
        contentType: 'tool_call',
        id: 'call-1',
        delta: '{"query": "test"}',
      },
      { type: 'tool_call_end_chunk', contentType: 'tool_call', id: 'call-1' },
    ];

    const response = createTestStreamResponse(chunks);

    const streams = [];
    for await (const stream of response.streams()) {
      streams.push(stream);
      expect(stream.contentType).toBe('tool_call');
      if (stream.contentType === 'tool_call') {
        expect(stream.toolId).toBe('call-1');
        expect(stream.toolName).toBe('search');
      }

      const deltas: string[] = [];
      for await (const delta of stream) {
        deltas.push(delta);
      }
      expect(deltas).toEqual(['{"query": "test"}']);
    }

    expect(streams).toHaveLength(1);
  });

  it('handles mixed content (thought -> text -> tool call)', async () => {
    const chunks: StreamResponseChunk[] = [
      // Thought
      { type: 'thought_start_chunk', contentType: 'thought' },
      { type: 'thought_chunk', contentType: 'thought', delta: 'Analyzing...' },
      { type: 'thought_end_chunk', contentType: 'thought' },
      // Text
      { type: 'text_start_chunk', contentType: 'text' },
      {
        type: 'text_chunk',
        contentType: 'text',
        delta: 'Here is my response.',
      },
      { type: 'text_end_chunk', contentType: 'text' },
      // Tool call
      {
        type: 'tool_call_start_chunk',
        contentType: 'tool_call',
        id: 'call-1',
        name: 'calculator',
      },
      {
        type: 'tool_call_chunk',
        contentType: 'tool_call',
        id: 'call-1',
        delta: '{"a": 5, "b": 3}',
      },
      { type: 'tool_call_end_chunk', contentType: 'tool_call', id: 'call-1' },
    ];

    const response = createTestStreamResponse(chunks);

    const contentTypes: string[] = [];
    for await (const stream of response.streams()) {
      contentTypes.push(stream.contentType);
      await stream.collect(); // Consume the stream
    }

    expect(contentTypes).toEqual(['thought', 'text', 'tool_call']);
    expect(response.consumed).toBe(true);
  });

  it('auto-consumes streams on each iteration', async () => {
    const chunks: StreamResponseChunk[] = [
      { type: 'text_start_chunk', contentType: 'text' },
      { type: 'text_chunk', contentType: 'text', delta: 'First' },
      { type: 'text_end_chunk', contentType: 'text' },
      { type: 'text_start_chunk', contentType: 'text' },
      { type: 'text_chunk', contentType: 'text', delta: 'Second' },
      { type: 'text_end_chunk', contentType: 'text' },
    ];

    const response = createTestStreamResponse(chunks);

    const partialTexts: string[] = [];
    for await (const stream of response.streams()) {
      // Don't iterate the stream - let auto-collect handle it
      // After the loop iteration, the stream should be collected
      partialTexts.push((stream as { partialText: string }).partialText);
    }

    // Both streams should have been auto-collected
    // The first one's partialText will be empty because we captured it before auto-collect
    // But the response should still be fully consumed
    expect(response.consumed).toBe(true);
    expect(response.texts).toHaveLength(2);
    expect(response.texts[0]?.text).toBe('First');
    expect(response.texts[1]?.text).toBe('Second');
  });

  it('handles empty stream', async () => {
    const chunks: StreamResponseChunk[] = [];

    const response = createTestStreamResponse(chunks);

    const streams = [];
    for await (const stream of response.streams()) {
      streams.push(stream);
    }

    expect(streams).toHaveLength(0);
    expect(response.consumed).toBe(true);
  });

  it('replays from cached chunks on second call', async () => {
    const chunks: StreamResponseChunk[] = [
      { type: 'text_start_chunk', contentType: 'text' },
      { type: 'text_chunk', contentType: 'text', delta: 'Hello' },
      { type: 'text_end_chunk', contentType: 'text' },
    ];

    const response = createTestStreamResponse(chunks);

    // First iteration
    const firstPassTypes: string[] = [];
    for await (const stream of response.streams()) {
      firstPassTypes.push(stream.contentType);
    }
    expect(firstPassTypes).toEqual(['text']);
    expect(response.consumed).toBe(true);

    // Second iteration - should replay from cache
    const secondPassTypes: string[] = [];
    for await (const stream of response.streams()) {
      secondPassTypes.push(stream.contentType);
    }
    expect(secondPassTypes).toEqual(['text']);
  });

  it('skips metadata chunks', async () => {
    const chunks: StreamResponseChunk[] = [
      { type: 'raw_stream_event_chunk', rawStreamEvent: { type: 'test' } },
      {
        type: 'usage_delta_chunk',
        inputTokens: 10,
        outputTokens: 0,
        cacheReadTokens: 0,
        cacheWriteTokens: 0,
        reasoningTokens: 0,
      },
      { type: 'text_start_chunk', contentType: 'text' },
      { type: 'text_chunk', contentType: 'text', delta: 'Hello' },
      { type: 'text_end_chunk', contentType: 'text' },
      { type: 'finish_reason_chunk', finishReason: FinishReason.MAX_TOKENS },
    ];

    const response = createTestStreamResponse(chunks);

    const contentTypes: string[] = [];
    for await (const stream of response.streams()) {
      contentTypes.push(stream.contentType);
    }

    // Should only yield the text stream, not metadata
    expect(contentTypes).toEqual(['text']);
    expect(response.usage?.inputTokens).toBe(10);
  });

  it('throws error for unexpected start chunk', async () => {
    // Create a response and manually manipulate to test error handling
    // This simulates an unexpected chunk type in the streams() switch
    const chunks: StreamResponseChunk[] = [
      // text_end_chunk without a start - this should trigger the default case
      { type: 'text_end_chunk', contentType: 'text' },
    ];

    const response = createTestStreamResponse(chunks);

    await expect(async () => {
      for await (const _ of response.streams()) {
        // Should throw before yielding anything
      }
    }).rejects.toThrow('Expected start chunk, got: text_end_chunk');
  });
});
