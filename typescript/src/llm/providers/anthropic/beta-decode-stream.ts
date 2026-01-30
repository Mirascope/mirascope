/**
 * Anthropic Beta stream decoding utilities.
 *
 * Converts Anthropic Beta MessageStreamEvent to Mirascope StreamResponseChunk.
 * The Beta API supports thinking blocks which are decoded as thought chunks.
 *
 * Note: This module is only used when shouldUseBeta() returns true, which requires
 * strict mode features that are not yet implemented. The code is marked with v8 ignore
 * to avoid coverage requirements for feature-gated code.
 */

/* v8 ignore start - beta streaming is feature-gated behind shouldUseBeta() */

import type { BetaRawMessageStreamEvent } from '@anthropic-ai/sdk/resources/beta/messages/messages';

import {
  textStart,
  textChunk,
  textEnd,
  thoughtStart,
  thoughtChunk,
  thoughtEnd,
} from '@/llm/content';
import type { StreamResponseChunk } from '@/llm/responses/chunks';
import {
  finishReasonChunk,
  usageDeltaChunk,
  rawStreamEventChunk,
} from '@/llm/responses/chunks';
import { FinishReason } from '@/llm/responses/finish-reason';

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
export function createBetaDecodeState(includeThoughts: boolean): DecodeState {
  return {
    currentBlockIndex: -1,
    currentBlockType: null,
    includeThoughts,
  };
}

/**
 * Decode an Anthropic Beta MessageStreamEvent to Mirascope chunks.
 *
 * @param event - The Anthropic Beta stream event
 * @param state - Mutable state tracking current block
 * @returns Array of Mirascope chunks (may be empty or multiple)
 */
export function decodeBetaStreamEvent(
  event: BetaRawMessageStreamEvent,
  state: DecodeState
): StreamResponseChunk[] {
  const chunks: StreamResponseChunk[] = [];

  // Always emit raw event chunk for debugging/passthrough
  chunks.push(rawStreamEventChunk(event));

  switch (event.type) {
    case 'message_start':
      // Note: We don't emit rawMessageChunk here because event.message contains
      // fields like 'model' and 'id' that aren't valid in resume requests.
      // For streaming, we let rawMessage remain null - the encodeMessages function
      // will encode from content parts instead.
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
        if (event.content_block.text) {
          chunks.push(textChunk(event.content_block.text));
        }
      } else if (event.content_block.type === 'thinking') {
        state.currentBlockType = 'thinking';
        // Only emit thought chunks if includeThoughts is true
        if (state.includeThoughts) {
          chunks.push(thoughtStart());
          // If there's initial thinking text, emit it
          if (event.content_block.thinking) {
            chunks.push(thoughtChunk(event.content_block.thinking));
          }
        }
      }
      // Note: tool_use and redacted_thinking blocks not yet fully supported
      break;

    case 'content_block_delta':
      if (event.delta.type === 'text_delta') {
        chunks.push(textChunk(event.delta.text));
      } else if (event.delta.type === 'thinking_delta') {
        // Only emit thought chunks if includeThoughts is true
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
      // Handle finish reason
      if (event.delta.stop_reason) {
        const finishReason = decodeBetaStopReason(event.delta.stop_reason);
        if (finishReason) {
          chunks.push(finishReasonChunk(finishReason));
        }
      }
      // Handle output token usage delta
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
 * Convert Anthropic Beta stop reason to Mirascope FinishReason.
 */
function decodeBetaStopReason(
  stopReason:
    | 'end_turn'
    | 'max_tokens'
    | 'stop_sequence'
    | 'tool_use'
    | 'refusal'
    | 'pause_turn'
    | 'model_context_window_exceeded'
    | null
): FinishReason | null {
  switch (stopReason) {
    case 'max_tokens':
    case 'model_context_window_exceeded':
      return FinishReason.MAX_TOKENS;
    case 'refusal':
      return FinishReason.REFUSAL;
    case 'end_turn':
    case 'stop_sequence':
    case 'tool_use':
    case 'pause_turn':
      return null; // Normal completion
    default:
      return null;
  }
}

/**
 * Create an async iterator that decodes Anthropic Beta stream events to Mirascope chunks.
 *
 * @param stream - The Anthropic Beta message stream
 * @param includeThoughts - Whether to include thinking blocks as thought chunks
 * @returns Async iterator of Mirascope chunks
 */
export async function* decodeBetaStream(
  stream: AsyncIterable<BetaRawMessageStreamEvent>,
  includeThoughts: boolean
): AsyncGenerator<StreamResponseChunk> {
  const state = createBetaDecodeState(includeThoughts);

  for await (const event of stream) {
    const chunks = decodeBetaStreamEvent(event, state);
    for (const chunk of chunks) {
      yield chunk;
    }
  }
}

/* v8 ignore stop */
