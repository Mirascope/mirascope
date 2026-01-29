/**
 * Anthropic stream decoding utilities.
 *
 * Converts Anthropic MessageStreamEvent to Mirascope StreamResponseChunk.
 * The standard Anthropic API supports thinking blocks when extended thinking is enabled.
 */

import type { MessageStreamEvent } from '@anthropic-ai/sdk/resources/messages';

import type { StreamResponseChunk } from '@/llm/responses/chunks';
import {
  textStart,
  textChunk,
  textEnd,
  thoughtStart,
  thoughtChunk,
  thoughtEnd,
  finishReasonChunk,
  usageDeltaChunk,
  rawStreamEventChunk,
  rawMessageChunk,
} from '@/llm/responses/chunks';
import { FinishReason } from '@/llm/responses/finish-reason';
import type { Jsonable } from '@/llm/types/jsonable';

/**
 * State tracking for stream decoding.
 */
interface DecodeState {
  /** Index of current content block being streamed */
  currentBlockIndex: number;
  /** Type of current content block */
  currentBlockType: 'text' | 'thinking' | null;
  /** Whether to include thoughts in output */
  includeThoughts: boolean;
}

/**
 * Create a new decode state for a fresh stream.
 */
export function createDecodeState(includeThoughts: boolean): DecodeState {
  return {
    currentBlockIndex: -1,
    currentBlockType: null,
    includeThoughts,
  };
}

/**
 * Decode an Anthropic MessageStreamEvent to Mirascope chunks.
 *
 * @param event - The Anthropic stream event
 * @param state - Mutable state tracking current block
 * @returns Array of Mirascope chunks (may be empty or multiple)
 */
export function decodeStreamEvent(
  event: MessageStreamEvent,
  state: DecodeState
): StreamResponseChunk[] {
  const chunks: StreamResponseChunk[] = [];

  // Always emit raw event chunk for debugging/passthrough
  chunks.push(rawStreamEventChunk(event));

  switch (event.type) {
    case 'message_start':
      // Emit raw message chunk with initial message data
      chunks.push(rawMessageChunk(event.message as unknown as Jsonable));
      // Emit initial usage if available
      if (event.message.usage) {
        chunks.push(
          usageDeltaChunk({
            inputTokens: event.message.usage.input_tokens,
            outputTokens: event.message.usage.output_tokens,
          })
        );
      }
      break;

    case 'content_block_start':
      state.currentBlockIndex = event.index;
      if (event.content_block.type === 'text') {
        state.currentBlockType = 'text';
        chunks.push(textStart());
        // If there's initial text, emit it
        /* v8 ignore start - initial text in start event is rare */
        if (event.content_block.text) {
          chunks.push(textChunk(event.content_block.text));
        }
        /* v8 ignore stop */
      } else if (event.content_block.type === 'thinking') {
        state.currentBlockType = 'thinking';
        if (state.includeThoughts) {
          chunks.push(thoughtStart());
          // If there's initial thinking text, emit it
          /* v8 ignore start - initial thinking in start event is rare */
          if (event.content_block.thinking) {
            chunks.push(thoughtChunk(event.content_block.thinking));
          }
          /* v8 ignore stop */
        }
      }
      // Note: tool_use and redacted_thinking blocks not yet supported
      break;

    case 'content_block_delta':
      if (event.delta.type === 'text_delta') {
        chunks.push(textChunk(event.delta.text));
      } else if (event.delta.type === 'thinking_delta') {
        if (state.includeThoughts) {
          chunks.push(thoughtChunk(event.delta.thinking));
        }
      }
      // Note: input_json_delta for tools not yet supported
      break;

    case 'content_block_stop':
      if (state.currentBlockType === 'text') {
        chunks.push(textEnd());
      } else if (
        state.currentBlockType === 'thinking' &&
        state.includeThoughts
      ) {
        chunks.push(thoughtEnd());
      }
      state.currentBlockType = null;
      break;

    case 'message_delta':
      if (event.delta.stop_reason) {
        const finishReason = decodeStopReason(event.delta.stop_reason);
        if (finishReason) {
          chunks.push(finishReasonChunk(finishReason));
        }
      }
      if (event.usage) {
        chunks.push(
          usageDeltaChunk({
            outputTokens: event.usage.output_tokens,
          })
        );
      }
      break;

    case 'message_stop':
      // Stream complete - no additional chunks needed
      break;
  }

  return chunks;
}

/**
 * Convert Anthropic stop reason to Mirascope FinishReason.
 */
function decodeStopReason(
  stopReason:
    | 'end_turn'
    | 'max_tokens'
    | 'stop_sequence'
    | 'tool_use'
    | 'refusal'
    | 'pause_turn'
    | null
): FinishReason | null {
  switch (stopReason) {
    case 'max_tokens':
      return FinishReason.MAX_TOKENS;
    /* v8 ignore next 2 - refusal is rare and hard to trigger reliably */
    case 'refusal':
      return FinishReason.REFUSAL;
    case 'end_turn':
    case 'stop_sequence':
    case 'tool_use':
    case 'pause_turn':
      return null; // Normal completion
    /* v8 ignore start - exhaustive switch default */
    default:
      return null;
    /* v8 ignore stop */
  }
}

/**
 * Create an async iterator that decodes Anthropic stream events to Mirascope chunks.
 *
 * @param stream - The Anthropic message stream
 * @param includeThoughts - Whether to include thinking blocks as thought chunks
 * @returns Async iterator of Mirascope chunks
 */
export async function* decodeStream(
  stream: AsyncIterable<MessageStreamEvent>,
  includeThoughts: boolean
): AsyncGenerator<StreamResponseChunk> {
  const state = createDecodeState(includeThoughts);

  for await (const event of stream) {
    const chunks = decodeStreamEvent(event, state);
    for (const chunk of chunks) {
      yield chunk;
    }
  }
}
