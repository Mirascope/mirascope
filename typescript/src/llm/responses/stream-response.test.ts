import { describe, expect, it } from 'vitest';
import { StreamResponse } from '@/llm/responses/stream-response';
import type { StreamResponseChunk } from '@/llm/responses/chunks';
import { FinishReason } from '@/llm/responses/finish-reason';
import type { UserMessage } from '@/llm/messages';

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

describe('StreamResponse', () => {
  describe('wrapChunkIterator', () => {
    it('wraps the chunk iterator with a custom wrapper', async () => {
      const chunks: StreamResponseChunk[] = [
        { type: 'text_start_chunk', contentType: 'text' },
        { type: 'text_chunk', contentType: 'text', delta: 'hello' },
        { type: 'text_end_chunk', contentType: 'text' },
      ];

      const response = createTestStreamResponse(chunks);

      // Wrap with a pass-through wrapper that tracks calls
      const wrappedChunks: StreamResponseChunk[] = [];
      response.wrapChunkIterator((iterator) => {
        return (async function* () {
          let result = await iterator.next();
          while (!result.done) {
            wrappedChunks.push(result.value);
            yield result.value;
            result = await iterator.next();
          }
        })();
      });

      // Consume the stream
      await response.consume();

      // Verify the wrapper was called
      expect(wrappedChunks).toHaveLength(3);
      expect(wrappedChunks[0]?.type).toBe('text_start_chunk');
    });

    it('allows error wrapping during iteration', async () => {
      const chunks: StreamResponseChunk[] = [
        { type: 'text_start_chunk', contentType: 'text' },
        { type: 'text_chunk', contentType: 'text', delta: 'hello' },
      ];

      const response = createTestStreamResponse(chunks);

      // Wrap with an error-throwing wrapper
      response.wrapChunkIterator((iterator) => {
        return (async function* () {
          let result = await iterator.next();
          while (!result.done) {
            if (result.value.type === 'text_chunk') {
              throw new Error('Simulated streaming error');
            }
            yield result.value;
            result = await iterator.next();
          }
        })();
      });

      // Consuming should throw
      await expect(response.consume()).rejects.toThrow(
        'Simulated streaming error'
      );
    });
  });

  describe('textStream', () => {
    it('streams only text deltas', async () => {
      const chunks: StreamResponseChunk[] = [
        { type: 'text_start_chunk', contentType: 'text' },
        { type: 'text_chunk', contentType: 'text', delta: 'hello ' },
        { type: 'text_chunk', contentType: 'text', delta: 'world' },
        { type: 'text_end_chunk', contentType: 'text' },
      ];

      const response = createTestStreamResponse(chunks);

      const texts: string[] = [];
      for await (const text of response.textStream()) {
        texts.push(text);
      }

      expect(texts).toEqual(['hello ', 'world']);
    });
  });

  describe('thoughtStream', () => {
    it('streams only thought deltas', async () => {
      const chunks: StreamResponseChunk[] = [
        { type: 'thought_start_chunk', contentType: 'thought' },
        { type: 'thought_chunk', contentType: 'thought', delta: 'thinking ' },
        { type: 'thought_chunk', contentType: 'thought', delta: 'deeply' },
        { type: 'thought_end_chunk', contentType: 'thought' },
      ];

      const response = createTestStreamResponse(chunks);

      const thoughts: string[] = [];
      for await (const thought of response.thoughtStream()) {
        thoughts.push(thought);
      }

      expect(thoughts).toEqual(['thinking ', 'deeply']);
    });
  });

  describe('consume', () => {
    it('consumes the entire stream', async () => {
      const chunks: StreamResponseChunk[] = [
        { type: 'text_start_chunk', contentType: 'text' },
        { type: 'text_chunk', contentType: 'text', delta: 'hello' },
        { type: 'text_end_chunk', contentType: 'text' },
      ];

      const response = createTestStreamResponse(chunks);

      expect(response.consumed).toBe(false);
      await response.consume();
      expect(response.consumed).toBe(true);
    });
  });

  describe('chunkStream replay', () => {
    it('replays cached chunks on second iteration', async () => {
      const chunks: StreamResponseChunk[] = [
        { type: 'text_start_chunk', contentType: 'text' },
        { type: 'text_chunk', contentType: 'text', delta: 'hello' },
        { type: 'text_end_chunk', contentType: 'text' },
      ];

      const response = createTestStreamResponse(chunks);

      // First iteration - consumes from iterator
      const firstPass: string[] = [];
      for await (const chunk of response.chunkStream()) {
        if (chunk.type === 'text_chunk') {
          firstPass.push(chunk.delta);
        }
      }
      expect(firstPass).toEqual(['hello']);
      expect(response.consumed).toBe(true);

      // Second iteration - replays from cache
      const secondPass: string[] = [];
      for await (const chunk of response.chunkStream()) {
        if (chunk.type === 'text_chunk') {
          secondPass.push(chunk.delta);
        }
      }
      expect(secondPass).toEqual(['hello']);
    });

    it('returns early when stream is already consumed', async () => {
      const chunks: StreamResponseChunk[] = [
        { type: 'text_start_chunk', contentType: 'text' },
        { type: 'text_chunk', contentType: 'text', delta: 'hello' },
        { type: 'text_end_chunk', contentType: 'text' },
      ];

      const response = createTestStreamResponse(chunks);

      // Consume the stream
      await response.consume();
      expect(response.consumed).toBe(true);

      // Calling chunkStream again should replay cached chunks and return
      const replayedChunks: string[] = [];
      for await (const chunk of response.chunkStream()) {
        if (chunk.type === 'text_chunk') {
          replayedChunks.push(chunk.delta);
        }
      }
      expect(replayedChunks).toEqual(['hello']);
    });
  });

  describe('metadata chunk processing', () => {
    it('processes raw_stream_event_chunk', async () => {
      const rawEvent = { type: 'some_event', data: 'test' };
      const chunks: StreamResponseChunk[] = [
        { type: 'raw_stream_event_chunk', rawStreamEvent: rawEvent },
        { type: 'text_start_chunk', contentType: 'text' },
        { type: 'text_chunk', contentType: 'text', delta: 'hello' },
        { type: 'text_end_chunk', contentType: 'text' },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.raw).toContainEqual(rawEvent);
    });

    it('processes raw_message_chunk', async () => {
      const rawMessage = { id: 'msg_123', model: 'test-model' };
      const chunks: StreamResponseChunk[] = [
        { type: 'raw_message_chunk', rawMessage },
        { type: 'text_start_chunk', contentType: 'text' },
        { type: 'text_end_chunk', contentType: 'text' },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.assistantMessage.rawMessage).toEqual(rawMessage);
    });

    it('processes finish_reason_chunk', async () => {
      const chunks: StreamResponseChunk[] = [
        { type: 'text_start_chunk', contentType: 'text' },
        { type: 'text_chunk', contentType: 'text', delta: 'partial' },
        { type: 'text_end_chunk', contentType: 'text' },
        { type: 'finish_reason_chunk', finishReason: FinishReason.MAX_TOKENS },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.finishReason).toBe(FinishReason.MAX_TOKENS);
    });

    it('accumulates usage_delta_chunk', async () => {
      const chunks: StreamResponseChunk[] = [
        {
          type: 'usage_delta_chunk',
          inputTokens: 10,
          outputTokens: 0,
          cacheReadTokens: 5,
          cacheWriteTokens: 0,
          reasoningTokens: 0,
        },
        { type: 'text_start_chunk', contentType: 'text' },
        { type: 'text_chunk', contentType: 'text', delta: 'hello' },
        { type: 'text_end_chunk', contentType: 'text' },
        {
          type: 'usage_delta_chunk',
          inputTokens: 0,
          outputTokens: 20,
          cacheReadTokens: 0,
          cacheWriteTokens: 3,
          reasoningTokens: 15,
        },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.usage).not.toBeNull();
      expect(response.usage?.inputTokens).toBe(10);
      expect(response.usage?.outputTokens).toBe(20);
      expect(response.usage?.cacheReadTokens).toBe(5);
      expect(response.usage?.cacheWriteTokens).toBe(3);
      expect(response.usage?.reasoningTokens).toBe(15);
    });
  });

  describe('property getters', () => {
    it('returns toolCalls via getter (empty when no tool calls)', async () => {
      const chunks: StreamResponseChunk[] = [
        { type: 'text_start_chunk', contentType: 'text' },
        { type: 'text_chunk', contentType: 'text', delta: 'hello' },
        { type: 'text_end_chunk', contentType: 'text' },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.toolCalls).toEqual([]);
    });

    it('returns thoughts via getter', async () => {
      const chunks: StreamResponseChunk[] = [
        { type: 'thought_start_chunk', contentType: 'thought' },
        { type: 'thought_chunk', contentType: 'thought', delta: 'thinking ' },
        { type: 'thought_chunk', contentType: 'thought', delta: 'about it' },
        { type: 'thought_end_chunk', contentType: 'thought' },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.thoughts).toHaveLength(1);
      expect(response.thoughts[0]?.thought).toBe('thinking about it');
    });

    it('returns chunks via getter', async () => {
      const chunks: StreamResponseChunk[] = [
        { type: 'text_start_chunk', contentType: 'text' },
        { type: 'text_chunk', contentType: 'text', delta: 'hi' },
        { type: 'text_end_chunk', contentType: 'text' },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.chunks).toHaveLength(3);
      expect(response.chunks[0]?.type).toBe('text_start_chunk');
      expect(response.chunks[1]?.type).toBe('text_chunk');
      expect(response.chunks[2]?.type).toBe('text_end_chunk');
    });

    it('returns texts via getter', async () => {
      const chunks: StreamResponseChunk[] = [
        { type: 'text_start_chunk', contentType: 'text' },
        { type: 'text_chunk', contentType: 'text', delta: 'hello ' },
        { type: 'text_chunk', contentType: 'text', delta: 'world' },
        { type: 'text_end_chunk', contentType: 'text' },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.texts).toHaveLength(1);
      expect(response.texts[0]?.text).toBe('hello world');
    });

    it('thought() joins with default separator', async () => {
      const chunks: StreamResponseChunk[] = [
        { type: 'thought_start_chunk', contentType: 'thought' },
        { type: 'thought_chunk', contentType: 'thought', delta: 'first' },
        { type: 'thought_end_chunk', contentType: 'thought' },
        { type: 'thought_start_chunk', contentType: 'thought' },
        { type: 'thought_chunk', contentType: 'thought', delta: 'second' },
        { type: 'thought_end_chunk', contentType: 'thought' },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.thought()).toBe('first\nsecond');
    });

    it('thought() joins with custom separator', async () => {
      const chunks: StreamResponseChunk[] = [
        { type: 'thought_start_chunk', contentType: 'thought' },
        { type: 'thought_chunk', contentType: 'thought', delta: 'first' },
        { type: 'thought_end_chunk', contentType: 'thought' },
        { type: 'thought_start_chunk', contentType: 'thought' },
        { type: 'thought_chunk', contentType: 'thought', delta: 'second' },
        { type: 'thought_end_chunk', contentType: 'thought' },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.thought(' | ')).toBe('first | second');
    });

    it('builds messages array with input and assistant', async () => {
      const inputMessage: UserMessage = {
        role: 'user',
        content: [{ type: 'text', text: 'hello' }],
        name: null,
      };

      const textChunks: StreamResponseChunk[] = [
        { type: 'text_start_chunk', contentType: 'text' },
        { type: 'text_chunk', contentType: 'text', delta: 'hi there' },
        { type: 'text_end_chunk', contentType: 'text' },
      ];

      const iterator = arrayToAsyncIterator(textChunks);
      const response = new StreamResponse({
        providerId: 'anthropic',
        modelId: 'anthropic/claude-sonnet-4-20250514',
        providerModelName: 'claude-sonnet-4-20250514',
        params: {},
        inputMessages: [inputMessage],
        chunkIterator: iterator,
      });

      await response.consume();

      expect(response.messages).toHaveLength(2);
      expect(response.messages[0]?.role).toBe('user');
      expect(response.messages[1]?.role).toBe('assistant');
    });

    it('builds assistantMessage with correct properties', async () => {
      const rawMessage = { id: 'msg_123' };
      const chunks: StreamResponseChunk[] = [
        { type: 'raw_message_chunk', rawMessage },
        { type: 'text_start_chunk', contentType: 'text' },
        { type: 'text_chunk', contentType: 'text', delta: 'response' },
        { type: 'text_end_chunk', contentType: 'text' },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      const msg = response.assistantMessage;
      expect(msg.role).toBe('assistant');
      expect(msg.content).toHaveLength(1);
      expect(msg.content[0]?.type).toBe('text');
      expect(msg.providerId).toBe('anthropic');
      expect(msg.modelId).toBe('anthropic/claude-sonnet-4-20250514');
      expect(msg.providerModelName).toBe('claude-sonnet-4-20250514');
      expect(msg.rawMessage).toEqual(rawMessage);
    });
  });

  describe('content accumulation', () => {
    it('accumulates text content correctly', async () => {
      const chunks: StreamResponseChunk[] = [
        { type: 'text_start_chunk', contentType: 'text' },
        { type: 'text_chunk', contentType: 'text', delta: 'Hello ' },
        { type: 'text_chunk', contentType: 'text', delta: 'World!' },
        { type: 'text_end_chunk', contentType: 'text' },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.content).toHaveLength(1);
      expect(response.content[0]?.type).toBe('text');
      expect(response.text()).toBe('Hello World!');
    });

    it('accumulates thought content correctly', async () => {
      const chunks: StreamResponseChunk[] = [
        { type: 'thought_start_chunk', contentType: 'thought' },
        { type: 'thought_chunk', contentType: 'thought', delta: 'Let me ' },
        { type: 'thought_chunk', contentType: 'thought', delta: 'think...' },
        { type: 'thought_end_chunk', contentType: 'thought' },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.content).toHaveLength(1);
      expect(response.content[0]?.type).toBe('thought');
      expect(response.thought()).toBe('Let me think...');
    });

    it('accumulates mixed content correctly', async () => {
      const chunks: StreamResponseChunk[] = [
        { type: 'thought_start_chunk', contentType: 'thought' },
        { type: 'thought_chunk', contentType: 'thought', delta: 'thinking' },
        { type: 'thought_end_chunk', contentType: 'thought' },
        { type: 'text_start_chunk', contentType: 'text' },
        { type: 'text_chunk', contentType: 'text', delta: 'answer' },
        { type: 'text_end_chunk', contentType: 'text' },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.content).toHaveLength(2);
      expect(response.content[0]?.type).toBe('thought');
      expect(response.content[1]?.type).toBe('text');
      expect(response.thought()).toBe('thinking');
      expect(response.text()).toBe('answer');
    });
  });
});
