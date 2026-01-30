/**
 * Stream classes for streaming assistant content parts.
 *
 * Each stream wraps a chunk iterator and provides:
 * - Async iteration via [Symbol.asyncIterator]() yielding delta strings
 * - collect() to consume remaining chunks and return the final content object
 * - Partial accumulation properties to track content as it arrives
 */

import type {
  Text,
  TextChunk,
  Thought,
  ThoughtChunk,
  ToolCall,
  ToolCallChunk,
} from '@/llm/content';

/**
 * Stream for text content.
 *
 * Wraps a TextChunk iterator and yields text delta strings.
 * Accumulates text in partialText as chunks are consumed.
 */
export class TextStream {
  readonly type = 'text_stream' as const;
  readonly contentType = 'text' as const;

  /** The accumulated text content as chunks are received. */
  partialText: string = '';

  private _chunkIterator: AsyncIterator<TextChunk>;

  constructor(chunkIterator: AsyncIterator<TextChunk>) {
    this._chunkIterator = chunkIterator;
  }

  /**
   * Iterate over text deltas as they are received.
   */
  async *[Symbol.asyncIterator](): AsyncGenerator<string> {
    let result = await this._chunkIterator.next();
    while (!result.done) {
      const delta = result.value.delta;
      this.partialText += delta;
      yield delta;
      result = await this._chunkIterator.next();
    }
  }

  /**
   * Collect all chunks and return the final Text content.
   */
  async collect(): Promise<Text> {
    for await (const _ of this) {
      // Just consume
    }
    return { type: 'text', text: this.partialText };
  }
}

/**
 * Stream for thought/reasoning content.
 *
 * Wraps a ThoughtChunk iterator and yields thought delta strings.
 * Accumulates thought in partialThought as chunks are consumed.
 */
export class ThoughtStream {
  readonly type = 'thought_stream' as const;
  readonly contentType = 'thought' as const;

  /** The accumulated thought content as chunks are received. */
  partialThought: string = '';

  private _chunkIterator: AsyncIterator<ThoughtChunk>;

  constructor(chunkIterator: AsyncIterator<ThoughtChunk>) {
    this._chunkIterator = chunkIterator;
  }

  /**
   * Iterate over thought deltas as they are received.
   */
  async *[Symbol.asyncIterator](): AsyncGenerator<string> {
    let result = await this._chunkIterator.next();
    while (!result.done) {
      const delta = result.value.delta;
      this.partialThought += delta;
      yield delta;
      result = await this._chunkIterator.next();
    }
  }

  /**
   * Collect all chunks and return the final Thought content.
   */
  async collect(): Promise<Thought> {
    for await (const _ of this) {
      // Just consume
    }
    return { type: 'thought', thought: this.partialThought };
  }
}

/**
 * Stream for tool call content.
 *
 * Wraps a ToolCallChunk iterator and yields argument delta strings.
 * Accumulates args in partialArgs as chunks are consumed.
 */
export class ToolCallStream {
  readonly type = 'tool_call_stream' as const;
  readonly contentType = 'tool_call' as const;

  /** A unique identifier for this tool call. */
  readonly toolId: string;

  /** The name of the tool being called. */
  readonly toolName: string;

  /** The accumulated tool arguments as chunks are received. */
  partialArgs: string = '';

  private _chunkIterator: AsyncIterator<ToolCallChunk>;

  constructor(
    toolId: string,
    toolName: string,
    chunkIterator: AsyncIterator<ToolCallChunk>
  ) {
    this.toolId = toolId;
    this.toolName = toolName;
    this._chunkIterator = chunkIterator;
  }

  /**
   * Iterate over tool call argument deltas as they are received.
   */
  async *[Symbol.asyncIterator](): AsyncGenerator<string> {
    let result = await this._chunkIterator.next();
    while (!result.done) {
      const delta = result.value.delta;
      this.partialArgs += delta;
      yield delta;
      result = await this._chunkIterator.next();
    }
  }

  /**
   * Collect all chunks and return the final ToolCall content.
   */
  async collect(): Promise<ToolCall> {
    for await (const _ of this) {
      // Just consume
    }
    return {
      type: 'tool_call',
      id: this.toolId,
      name: this.toolName,
      args: this.partialArgs,
    };
  }
}

/**
 * A stream for any assistant content type.
 */
export type Stream = TextStream | ThoughtStream | ToolCallStream;
