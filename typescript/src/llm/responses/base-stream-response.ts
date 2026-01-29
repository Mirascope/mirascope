/**
 * BaseStreamResponse class for handling streaming LLM responses.
 *
 * Extends RootResponse to provide the standard response interface while adding
 * streaming-specific methods:
 * - chunkStream(): Raw chunks as async iterator (with caching for replay)
 * - textStream(): Text deltas only
 * - thoughtStream(): Thought deltas only
 *
 * Accumulates content as chunks arrive, with final state accessible via
 * the standard RootResponse interface (text(), content, finishReason, usage, etc.).
 *
 * This base class contains all streaming logic but no resume methods.
 * StreamResponse and ContextStreamResponse extend this class and add their
 * own resume methods with appropriate signatures.
 */

import type {
  AssistantContentPart,
  Text,
  Thought,
  ToolCall,
} from '@/llm/content';
import type { AssistantMessage, Message } from '@/llm/messages';
import type { Params } from '@/llm/models';
import type { ModelId, ProviderId } from '@/llm/providers';
import type { FinishReason } from '@/llm/responses/finish-reason';
import { RootResponse } from '@/llm/responses/root-response';
import type { Usage } from '@/llm/responses/usage';
import { createUsage } from '@/llm/responses/usage';
import type {
  AssistantContentChunk,
  StreamResponseChunk,
  TextChunk,
  ThoughtChunk,
  ToolCallChunk,
} from '@/llm/responses/chunks';
import {
  TextStream,
  ThoughtStream,
  ToolCallStream,
  type Stream,
} from '@/llm/responses/streams';
import type { Jsonable } from '@/llm/types/jsonable';
import type { BaseToolkit } from '@/llm/tools';

/**
 * Arguments for constructing a BaseStreamResponse.
 */
export interface BaseStreamResponseInit {
  /** The provider ID (e.g., 'anthropic', 'openai') */
  providerId: ProviderId;

  /** The model ID (e.g., 'anthropic/claude-sonnet-4-20250514') */
  modelId: ModelId;

  /** The provider's model name from the response */
  providerModelName: string;

  /** Parameters used for the request */
  params: Params;

  /** The toolkit containing all tools available for this response */
  toolkit: BaseToolkit;

  /** Input messages sent in the request */
  inputMessages: readonly Message[];

  /** Async iterator of streaming chunks from the provider */
  chunkIterator: AsyncIterator<StreamResponseChunk>;
}

/**
 * Base streaming response that consumes chunks from an async iterator.
 *
 * Extends RootResponse to provide the standard response interface. Chunks are
 * processed lazily and cached for replay. Content is accumulated as chunks
 * arrive, with text/thought objects mutated in place for efficiency.
 *
 * This class contains all streaming logic but no resume methods. Subclasses
 * (StreamResponse, ContextStreamResponse) add their own resume methods.
 */
export class BaseStreamResponse extends RootResponse {
  // ===== RootResponse Implementation =====

  /** Raw stream events from provider */
  get raw(): readonly unknown[] {
    return this._rawStreamEvents;
  }

  readonly providerId: ProviderId;
  readonly modelId: ModelId;
  readonly providerModelName: string;
  readonly params: Params;
  readonly toolkit: BaseToolkit;

  /** Input messages sent in the request */
  readonly inputMessages: readonly Message[];

  get messages(): readonly Message[] {
    return [...this.inputMessages, this.assistantMessage];
  }

  get content(): readonly AssistantContentPart[] {
    return this._content;
  }

  get texts(): readonly Text[] {
    return this._texts;
  }

  get toolCalls(): readonly ToolCall[] {
    return this._toolCalls;
  }

  get thoughts(): readonly Thought[] {
    return this._thoughts;
  }

  get finishReason(): FinishReason | null {
    return this._finishReason;
  }

  get usage(): Usage | null {
    return this._usage;
  }

  // ===== Streaming-Specific Properties =====

  /** Cached chunks for replay */
  private readonly _chunks: AssistantContentChunk[] = [];
  /** Accumulated content parts */
  private readonly _content: AssistantContentPart[] = [];
  /** Accumulated text parts */
  private readonly _texts: Text[] = [];
  /** Accumulated thought parts */
  private readonly _thoughts: Thought[] = [];
  /** Accumulated tool calls */
  private readonly _toolCalls: ToolCall[] = [];
  /** Raw stream events from provider */
  private readonly _rawStreamEvents: unknown[] = [];

  /** The chunk iterator from the provider */
  private _chunkIterator: AsyncIterator<StreamResponseChunk>;
  /** Current content block being built (Text or Thought) */
  private _currentContent:
    | (Text & { text: string })
    | (Thought & { thought: string })
    | null = null;
  /** In-progress tool calls tracked by ID (for interleaved streaming) */
  private readonly _currentToolCalls = new Map<
    string,
    ToolCall & { args: string }
  >();
  /** Whether the iterator has been fully consumed */
  private _consumed = false;

  /** Finish reason once stream is complete */
  private _finishReason: FinishReason | null = null;
  /** Accumulated usage statistics */
  private _usage: Usage | null = null;
  /** Raw message from provider */
  private _rawMessage: Jsonable = null;

  constructor(args: BaseStreamResponseInit) {
    super();
    this.providerId = args.providerId;
    this.modelId = args.modelId;
    this.providerModelName = args.providerModelName;
    this.params = args.params;
    this.toolkit = args.toolkit;
    this.inputMessages = args.inputMessages;
    this._chunkIterator = args.chunkIterator;
  }

  // ===== Streaming-Specific Methods =====

  /**
   * Get the cached chunks.
   */
  get chunks(): readonly AssistantContentChunk[] {
    return this._chunks;
  }

  /**
   * Whether the stream has been fully consumed.
   */
  get consumed(): boolean {
    return this._consumed;
  }

  /**
   * Get the accumulated thought content.
   * Joins all thought parts with the specified separator.
   */
  thought(separator = '\n'): string {
    return this._thoughts.map((t) => t.thought).join(separator);
  }

  /**
   * Build the assistant message from accumulated content.
   */
  get assistantMessage(): AssistantMessage {
    return {
      role: 'assistant',
      content: [...this._content],
      name: null,
      providerId: this.providerId,
      modelId: this.modelId,
      providerModelName: this.providerModelName,
      rawMessage: this._rawMessage,
    };
  }

  /**
   * Stream content chunks with caching for replay.
   *
   * First yields any cached chunks, then continues consuming from the iterator.
   * All chunks are cached so subsequent calls can replay from the beginning.
   */
  async *chunkStream(): AsyncGenerator<AssistantContentChunk> {
    // First, yield all cached chunks (replay mechanism)
    for (const chunk of this._chunks) {
      yield chunk;
    }

    // If stream is already fully consumed, stop
    if (this._consumed) {
      return;
    }

    // Consume fresh chunks from the iterator
    let result = await this._chunkIterator.next();
    while (!result.done) {
      const chunk = result.value;
      const contentChunk = this._processChunk(chunk);
      if (contentChunk) {
        yield contentChunk;
      }
      result = await this._chunkIterator.next();
    }

    // Mark stream as fully consumed
    this._consumed = true;
  }

  /**
   * Stream only text deltas.
   *
   * Yields the text string from each TextChunk, filtering out other chunk types.
   */
  async *textStream(): AsyncGenerator<string> {
    for await (const chunk of this.chunkStream()) {
      if (chunk.type === 'text_chunk') {
        yield chunk.delta;
      }
    }
  }

  /**
   * Stream only thought deltas.
   *
   * Yields the thought string from each ThoughtChunk, filtering out other chunk types.
   */
  async *thoughtStream(): AsyncGenerator<string> {
    for await (const chunk of this.chunkStream()) {
      if (chunk.type === 'thought_chunk') {
        yield chunk.delta;
      }
    }
  }

  /**
   * Consume the entire stream without processing chunks.
   * Useful when you just want the final accumulated state.
   */
  async consume(): Promise<void> {
    for await (const _ of this.chunkStream()) {
      // Just consume
    }
  }

  /**
   * Returns an async iterator that yields streams for each content part in the response.
   *
   * Each content part in the response will correspond to one stream, which will yield
   * chunks of content as they come in from the underlying LLM.
   *
   * Fully iterating through this iterator will fully consume the underlying stream,
   * updating the Response with all collected content.
   *
   * As content is consumed, it is cached on the StreamResponse. If a new iterator
   * is constructed via calling `streams()`, it will start by replaying the cached
   * content from the response, and (if there is still more content to consume from
   * the LLM), it will proceed to consume it once it has iterated through all the
   * cached chunks.
   */
  async *streams(): AsyncGenerator<Stream> {
    const chunkIter = this.chunkStream();

    // Use manual iteration to avoid closing the iterator on early return.
    // Using for-await-of would call iter.return() when the inner generator
    // returns, which would close chunkIter and prevent _consumed from being set.
    let result = await chunkIter.next();
    while (!result.done) {
      const startChunk = result.value;

      // At the start of this loop, we always expect to find a start chunk. Then,
      // before proceeding, we will collect from the stream we create (in case the
      // user did not exhaust it), which ensures we will be expecting a start chunk
      // again on the next iteration
      let stream: Stream;

      switch (startChunk.type) {
        case 'text_start_chunk': {
          const textStreamIterator = async function* (
            iter: AsyncGenerator<AssistantContentChunk>
          ): AsyncGenerator<TextChunk> {
            // Use manual iteration to avoid closing the outer iterator
            let innerResult = await iter.next();
            while (!innerResult.done) {
              const chunk = innerResult.value;
              if (chunk.type === 'text_chunk') {
                yield chunk;
                innerResult = await iter.next();
              } else {
                return; // Stream finished
              }
            }
          };
          stream = new TextStream(textStreamIterator(chunkIter));
          yield stream;
          break;
        }

        case 'thought_start_chunk': {
          const thoughtStreamIterator = async function* (
            iter: AsyncGenerator<AssistantContentChunk>
          ): AsyncGenerator<ThoughtChunk> {
            // Use manual iteration to avoid closing the outer iterator
            let innerResult = await iter.next();
            while (!innerResult.done) {
              const chunk = innerResult.value;
              if (chunk.type === 'thought_chunk') {
                yield chunk;
                innerResult = await iter.next();
              } else {
                return; // Stream finished
              }
            }
          };
          stream = new ThoughtStream(thoughtStreamIterator(chunkIter));
          yield stream;
          break;
        }

        case 'tool_call_start_chunk': {
          const toolId = startChunk.id;
          const toolName = startChunk.name;

          const toolCallStreamIterator = async function* (
            iter: AsyncGenerator<AssistantContentChunk>
          ): AsyncGenerator<ToolCallChunk> {
            // Use manual iteration to avoid closing the outer iterator
            let innerResult = await iter.next();
            while (!innerResult.done) {
              const chunk = innerResult.value;
              if (chunk.type === 'tool_call_chunk') {
                yield chunk;
                innerResult = await iter.next();
              } else {
                return; // Stream finished
              }
            }
          };
          stream = new ToolCallStream(
            toolId,
            toolName,
            toolCallStreamIterator(chunkIter)
          );
          yield stream;
          break;
        }

        default:
          throw new Error(`Expected start chunk, got: ${startChunk.type}`);
      }

      // Before continuing to the next stream, make sure the last stream is consumed
      // (If the user did not do so when we yielded it)
      await stream.collect();

      result = await chunkIter.next();
    }
  }

  /**
   * Replace the chunk iterator with a wrapped version.
   * Used internally by providers to wrap errors during iteration.
   * @internal
   */
  wrapChunkIterator(
    wrapper: (
      iterator: AsyncIterator<StreamResponseChunk>
    ) => AsyncIterator<StreamResponseChunk>
  ): void {
    this._chunkIterator = wrapper(this._chunkIterator);
  }

  // ===== Private Helpers =====

  /**
   * Process a single chunk, handling metadata and content accumulation.
   * Returns the content chunk if it should be yielded, null otherwise.
   */
  private _processChunk(
    chunk: StreamResponseChunk
  ): AssistantContentChunk | null {
    switch (chunk.type) {
      // Metadata chunks - handle internally, don't yield
      case 'raw_stream_event_chunk':
        this._rawStreamEvents.push(chunk.rawStreamEvent);
        return null;

      case 'raw_message_chunk':
        this._rawMessage = chunk.rawMessage;
        return null;

      case 'finish_reason_chunk':
        this._finishReason = chunk.finishReason;
        return null;

      case 'usage_delta_chunk':
        this._accumulateUsage(chunk);
        return null;

      case 'text_start_chunk':
      case 'text_chunk':
      case 'text_end_chunk':
        return this._handleTextChunk(chunk);

      case 'thought_start_chunk':
      case 'thought_chunk':
      case 'thought_end_chunk':
        return this._handleThoughtChunk(chunk);

      case 'tool_call_start_chunk':
      case 'tool_call_chunk':
      case 'tool_call_end_chunk':
        return this._handleToolCallChunk(chunk);
    }
  }

  /**
   * Handle text chunks, accumulating content.
   */
  private _handleTextChunk(
    chunk:
      | { type: 'text_start_chunk'; contentType: 'text' }
      | { type: 'text_chunk'; contentType: 'text'; delta: string }
      | { type: 'text_end_chunk'; contentType: 'text' }
  ): AssistantContentChunk {
    if (chunk.type === 'text_start_chunk') {
      // Create new Text object and add to content immediately
      const text: Text & { text: string } = { type: 'text', text: '' };
      this._currentContent = text;
      this._content.push(text);
      this._texts.push(text);
    } else if (chunk.type === 'text_chunk') {
      // Mutate the existing Text object in place
      if (this._currentContent && 'text' in this._currentContent) {
        this._currentContent.text += chunk.delta;
      }
    } else if (chunk.type === 'text_end_chunk') {
      // Mark text as complete
      this._currentContent = null;
    }

    // Cache and return the chunk
    this._chunks.push(chunk);
    return chunk;
  }

  /**
   * Handle thought chunks, accumulating content.
   */
  private _handleThoughtChunk(
    chunk:
      | { type: 'thought_start_chunk'; contentType: 'thought' }
      | { type: 'thought_chunk'; contentType: 'thought'; delta: string }
      | { type: 'thought_end_chunk'; contentType: 'thought' }
  ): AssistantContentChunk {
    if (chunk.type === 'thought_start_chunk') {
      // Create new Thought object and add to content immediately
      const thought: Thought & { thought: string } = {
        type: 'thought',
        thought: '',
      };
      this._currentContent = thought;
      this._content.push(thought);
      this._thoughts.push(thought);
    } else if (chunk.type === 'thought_chunk') {
      // Mutate the existing Thought object in place
      if (this._currentContent && 'thought' in this._currentContent) {
        this._currentContent.thought += chunk.delta;
      }
    } else if (chunk.type === 'thought_end_chunk') {
      // Mark thought as complete
      this._currentContent = null;
    }

    // Cache and return the chunk
    this._chunks.push(chunk);
    return chunk;
  }

  /**
   * Handle tool call chunks, accumulating content.
   *
   * Unlike text/thought which are added immediately to content,
   * tool calls are only added once the end chunk is received.
   * Multiple tool calls can be in progress simultaneously (interleaved).
   */
  private _handleToolCallChunk(
    chunk:
      | {
          type: 'tool_call_start_chunk';
          contentType: 'tool_call';
          id: string;
          name: string;
        }
      | {
          type: 'tool_call_chunk';
          contentType: 'tool_call';
          id: string;
          delta: string;
        }
      | { type: 'tool_call_end_chunk'; contentType: 'tool_call'; id: string }
  ): AssistantContentChunk {
    if (chunk.type === 'tool_call_start_chunk') {
      // Create new ToolCall and track by ID
      if (this._currentToolCalls.has(chunk.id)) {
        throw new Error(
          `Received tool_call_start_chunk with duplicate id: ${chunk.id}`
        );
      }
      const toolCall: ToolCall & { args: string } = {
        type: 'tool_call',
        id: chunk.id,
        name: chunk.name,
        args: '',
      };
      this._currentToolCalls.set(chunk.id, toolCall);
    } else if (chunk.type === 'tool_call_chunk') {
      // Append delta to existing tool call's args
      const toolCall = this._currentToolCalls.get(chunk.id);
      if (!toolCall) {
        throw new Error(
          `Received tool_call_chunk for unknown tool call ID: ${chunk.id}`
        );
      }
      toolCall.args += chunk.delta;
    } else if (chunk.type === 'tool_call_end_chunk') {
      // Finalize tool call and add to content
      const toolCall = this._currentToolCalls.get(chunk.id);
      if (!toolCall) {
        throw new Error(
          `Received tool_call_end_chunk for unknown tool call ID: ${chunk.id}`
        );
      }
      // Default empty args to empty object (matches Python behavior)
      if (!toolCall.args) {
        toolCall.args = '{}';
      }
      this._content.push(toolCall);
      this._toolCalls.push(toolCall);
      this._currentToolCalls.delete(chunk.id);
    }

    // Cache and return the chunk
    this._chunks.push(chunk);
    return chunk;
  }

  /**
   * Accumulate usage statistics from a usage delta chunk.
   */
  private _accumulateUsage(chunk: {
    type: 'usage_delta_chunk';
    inputTokens: number;
    outputTokens: number;
    cacheReadTokens: number;
    cacheWriteTokens: number;
    reasoningTokens: number;
  }): void {
    if (this._usage === null) {
      this._usage = createUsage({
        inputTokens: 0,
        outputTokens: 0,
        cacheReadTokens: 0,
        cacheWriteTokens: 0,
        reasoningTokens: 0,
        raw: null,
      });
    }

    // Accumulate token counts
    // Note: Usage is frozen by createUsage, so we need to create a new one
    this._usage = createUsage({
      inputTokens: this._usage.inputTokens + chunk.inputTokens,
      outputTokens: this._usage.outputTokens + chunk.outputTokens,
      cacheReadTokens: this._usage.cacheReadTokens + chunk.cacheReadTokens,
      cacheWriteTokens: this._usage.cacheWriteTokens + chunk.cacheWriteTokens,
      reasoningTokens: this._usage.reasoningTokens + chunk.reasoningTokens,
      raw: this._usage.raw,
    });
  }
}
