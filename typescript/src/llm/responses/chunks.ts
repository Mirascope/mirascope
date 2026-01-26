/**
 * Streaming chunk types for provider-agnostic streaming responses.
 *
 * Chunks follow a three-phase streaming pattern:
 * - Start: Signals beginning of a content block
 * - Delta: Contains incremental content updates
 * - End: Signals completion of a content block
 *
 * All chunks use discriminated unions via the `type` field.
 */

import type { FinishReason } from '@/llm/responses/finish-reason';
import type { Jsonable } from '@/llm/types/jsonable';

// ============================================================================
// Text Chunks
// ============================================================================

/**
 * Signals the start of a text content block in the stream.
 */
export interface TextStartChunk {
  readonly type: 'text_start_chunk';
  readonly contentType: 'text';
}

/**
 * Contains incremental text content.
 */
export interface TextChunk {
  readonly type: 'text_chunk';
  readonly contentType: 'text';
  /** The incremental text added in this chunk */
  readonly delta: string;
}

/**
 * Signals the end of a text content block in the stream.
 */
export interface TextEndChunk {
  readonly type: 'text_end_chunk';
  readonly contentType: 'text';
}

// ============================================================================
// Thought Chunks
// ============================================================================

/**
 * Signals the start of a thought/reasoning content block in the stream.
 */
export interface ThoughtStartChunk {
  readonly type: 'thought_start_chunk';
  readonly contentType: 'thought';
}

/**
 * Contains incremental thought/reasoning content.
 */
export interface ThoughtChunk {
  readonly type: 'thought_chunk';
  readonly contentType: 'thought';
  /** The incremental thought text added in this chunk */
  readonly delta: string;
}

/**
 * Signals the end of a thought/reasoning content block in the stream.
 */
export interface ThoughtEndChunk {
  readonly type: 'thought_end_chunk';
  readonly contentType: 'thought';
}

// ============================================================================
// Tool Call Chunks (for future tools support)
// ============================================================================

/**
 * Signals the start of a tool call in the stream.
 */
export interface ToolCallStartChunk {
  readonly type: 'tool_call_start_chunk';
  readonly contentType: 'tool_call';
  /** Unique identifier for this tool call */
  readonly id: string;
  /** The name of the tool to call */
  readonly name: string;
}

/**
 * Contains incremental tool call arguments (JSON).
 */
export interface ToolCallChunk {
  readonly type: 'tool_call_chunk';
  readonly contentType: 'tool_call';
  /** Unique identifier for this tool call */
  readonly id: string;
  /** The incremental JSON args added in this chunk */
  readonly delta: string;
}

/**
 * Signals the end of a tool call in the stream.
 */
export interface ToolCallEndChunk {
  readonly type: 'tool_call_end_chunk';
  readonly contentType: 'tool_call';
  /** Unique identifier for this tool call */
  readonly id: string;
}

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
 * Content chunks that can appear in assistant messages.
 */
export type AssistantContentChunk =
  | TextStartChunk
  | TextChunk
  | TextEndChunk
  | ThoughtStartChunk
  | ThoughtChunk
  | ThoughtEndChunk
  | ToolCallStartChunk
  | ToolCallChunk
  | ToolCallEndChunk;

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

/** Create a TextStartChunk */
export function textStart(): TextStartChunk {
  return { type: 'text_start_chunk', contentType: 'text' };
}

/** Create a TextChunk */
export function textChunk(delta: string): TextChunk {
  return { type: 'text_chunk', contentType: 'text', delta };
}

/** Create a TextEndChunk */
export function textEnd(): TextEndChunk {
  return { type: 'text_end_chunk', contentType: 'text' };
}

/** Create a ThoughtStartChunk */
export function thoughtStart(): ThoughtStartChunk {
  return { type: 'thought_start_chunk', contentType: 'thought' };
}

/** Create a ThoughtChunk */
export function thoughtChunk(delta: string): ThoughtChunk {
  return { type: 'thought_chunk', contentType: 'thought', delta };
}

/** Create a ThoughtEndChunk */
export function thoughtEnd(): ThoughtEndChunk {
  return { type: 'thought_end_chunk', contentType: 'thought' };
}

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
