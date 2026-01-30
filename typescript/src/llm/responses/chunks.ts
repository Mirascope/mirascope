/**
 * Streaming metadata chunk types for provider-agnostic streaming responses.
 *
 * Content-specific chunks (Text, Thought, ToolCall) are defined in content/.
 * This file only contains metadata chunks.
 */

import type { FinishReason } from '@/llm/responses/finish-reason';
import type { Jsonable } from '@/llm/types/jsonable';
import type { AssistantContentChunk } from '@/llm/content';

// ============================================================================
// Metadata Chunks
// ============================================================================

/**
 * Contains the finish reason when the stream completes.
 */
export interface FinishReasonChunk {
  readonly type: 'finish_reason_chunk';
  /** The reason the stream finished */
  readonly finishReason: FinishReason;
}

/**
 * Contains incremental token usage information.
 */
export interface UsageDeltaChunk {
  readonly type: 'usage_delta_chunk';
  /** Delta in input tokens */
  readonly inputTokens: number;
  /** Delta in output tokens */
  readonly outputTokens: number;
  /** Delta in cache read tokens */
  readonly cacheReadTokens: number;
  /** Delta in cache write tokens */
  readonly cacheWriteTokens: number;
  /** Delta in reasoning/thinking tokens */
  readonly reasoningTokens: number;
}

/**
 * Contains a raw stream event from the underlying provider.
 */
export interface RawStreamEventChunk {
  readonly type: 'raw_stream_event_chunk';
  /** The raw stream event from the underlying provider */
  readonly rawStreamEvent: unknown;
}

/**
 * Contains provider-specific raw message content.
 */
export interface RawMessageChunk {
  readonly type: 'raw_message_chunk';
  /** Provider-specific raw content */
  readonly rawMessage: Jsonable;
}

// ============================================================================
// Type Aliases
// ============================================================================

/**
 * All possible chunk types in a streaming response.
 */
export type StreamResponseChunk =
  | AssistantContentChunk
  | FinishReasonChunk
  | UsageDeltaChunk
  | RawStreamEventChunk
  | RawMessageChunk;

/**
 * Async iterator type for streaming chunks.
 */
export type AsyncChunkIterator = AsyncIterator<StreamResponseChunk>;

// ============================================================================
// Factory Functions
// ============================================================================

/** Create a FinishReasonChunk */
export function finishReasonChunk(
  finishReason: FinishReason
): FinishReasonChunk {
  return { type: 'finish_reason_chunk', finishReason };
}

/** Create a UsageDeltaChunk */
/* v8 ignore start - optional fields default to 0 */
export function usageDeltaChunk(usage: {
  inputTokens?: number;
  outputTokens?: number;
  cacheReadTokens?: number;
  cacheWriteTokens?: number;
  reasoningTokens?: number;
}): UsageDeltaChunk {
  return {
    type: 'usage_delta_chunk',
    inputTokens: usage.inputTokens ?? 0,
    outputTokens: usage.outputTokens ?? 0,
    cacheReadTokens: usage.cacheReadTokens ?? 0,
    cacheWriteTokens: usage.cacheWriteTokens ?? 0,
    reasoningTokens: usage.reasoningTokens ?? 0,
  };
}
/* v8 ignore stop */

/** Create a RawStreamEventChunk */
export function rawStreamEventChunk(
  rawStreamEvent: unknown
): RawStreamEventChunk {
  return { type: 'raw_stream_event_chunk', rawStreamEvent };
}

/** Create a RawMessageChunk */
export function rawMessageChunk(rawMessage: Jsonable): RawMessageChunk {
  return { type: 'raw_message_chunk', rawMessage };
}
