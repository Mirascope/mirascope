/**
 * Google stream decoding utilities.
 *
 * Converts Google GenerateContentResponse chunks to Mirascope StreamResponseChunk.
 * Google streaming returns complete parts in each chunk, not deltas.
 */

import type {
  GenerateContentResponse,
  FinishReason as GoogleFinishReasonType,
} from '@google/genai';
import { FinishReason as GoogleFinishReason } from '@google/genai';

import type { StreamResponseChunk } from '@/llm/responses/chunks';
import {
  textStart,
  textChunk,
  textEnd,
  thoughtStart,
  thoughtChunk,
  thoughtEnd,
  toolCallStartChunk,
  toolCallChunk,
  toolCallEndChunk,
  finishReasonChunk,
  usageDeltaChunk,
  rawStreamEventChunk,
  rawMessageChunk,
} from '@/llm/responses/chunks';
import { FinishReason } from '@/llm/responses/finish-reason';
import type { Jsonable } from '@/llm/types/jsonable';

/**
 * Default tool ID for Google function calls when no ID is provided.
 * Google doesn't always provide tool IDs, so we use this as a fallback.
 */
const UNKNOWN_TOOL_ID = 'google_unknown_tool_id';

/**
 * State tracking for stream decoding.
 */
interface DecodeState {
  /** Whether we're in a text block */
  inTextBlock: boolean;
  /** Whether we're in a thought block */
  inThoughtBlock: boolean;
  /** Whether to include thoughts in output */
  includeThoughts: boolean;
  /** Accumulated parts for raw message */
  accumulatedParts: unknown[];
}

/**
 * Create a new decode state for a fresh stream.
 */
export function createDecodeState(includeThoughts: boolean): DecodeState {
  return {
    inTextBlock: false,
    inThoughtBlock: false,
    includeThoughts,
    accumulatedParts: [],
  };
}

/**
 * Decode a Google GenerateContentResponse to Mirascope chunks.
 *
 * Unlike Anthropic which streams character-by-character deltas,
 * Google streams complete parts. We still emit start/chunk/end
 * to maintain a consistent interface.
 *
 * @param response - The Google stream response chunk
 * @param state - Mutable state tracking current blocks
 * @returns Array of Mirascope chunks
 */
export function decodeStreamEvent(
  response: GenerateContentResponse,
  state: DecodeState
): StreamResponseChunk[] {
  const chunks: StreamResponseChunk[] = [];

  // Always emit raw event chunk
  chunks.push(rawStreamEventChunk(response));

  const candidate = response.candidates?.[0];
  const parts = candidate?.content?.parts ?? [];

  // Accumulate parts for raw message (matching Python's accumulated_parts)
  for (const part of parts) {
    state.accumulatedParts.push(part);
  }

  for (const part of parts) {
    if (part.thought && part.text !== undefined) {
      if (state.includeThoughts) {
        // Emit thought start if not already in a thought block
        if (!state.inThoughtBlock) {
          // Close any open text block first
          /* v8 ignore start - edge case when thoughts follow text */
          if (state.inTextBlock) {
            chunks.push(textEnd());
            state.inTextBlock = false;
          }
          /* v8 ignore stop */
          chunks.push(thoughtStart());
          state.inThoughtBlock = true;
        }
        chunks.push(thoughtChunk(part.text));
      }
    } else if (part.text !== undefined) {
      if (!state.inTextBlock) {
        // Close any open thought block first
        if (state.inThoughtBlock) {
          chunks.push(thoughtEnd());
          state.inThoughtBlock = false;
        }
        chunks.push(textStart());
        state.inTextBlock = true;
      }
      chunks.push(textChunk(part.text));
    } else if (part.functionCall) {
      const functionCall = part.functionCall;
      const toolId = functionCall.id ?? UNKNOWN_TOOL_ID;
      const toolName = functionCall.name;

      /* v8 ignore start - defensive check for malformed Google API response */
      if (!toolName) {
        throw new Error('Required name missing on Google function call');
      }
      /* v8 ignore stop */

      // Close any open blocks before emitting tool call
      /* v8 ignore start - Google doesn't send text and function calls together */
      if (state.inTextBlock) {
        chunks.push(textEnd());
        state.inTextBlock = false;
      }
      /* v8 ignore stop */
      /* v8 ignore start - edge case when thought block open at function call */
      if (state.inThoughtBlock) {
        chunks.push(thoughtEnd());
        state.inThoughtBlock = false;
      }
      /* v8 ignore stop */

      // Google sends complete function calls, so we emit start/chunk/end together
      chunks.push(toolCallStartChunk(toolId, toolName));
      chunks.push(
        toolCallChunk(
          toolId,
          /* v8 ignore next 1 - empty args branch */
          functionCall.args ? JSON.stringify(functionCall.args) : '{}'
        )
      );
      chunks.push(toolCallEndChunk(toolId));
    }
  }

  if (candidate?.finishReason) {
    // Close any open blocks
    if (state.inTextBlock) {
      chunks.push(textEnd());
      state.inTextBlock = false;
    }
    /* v8 ignore start - edge case when thought block open at finish */
    if (state.inThoughtBlock) {
      chunks.push(thoughtEnd());
      state.inThoughtBlock = false;
    }
    /* v8 ignore stop */

    const finishReason = decodeFinishReason(candidate.finishReason);
    if (finishReason) {
      chunks.push(finishReasonChunk(finishReason));
    }
  }

  const usage = response.usageMetadata;
  if (usage) {
    chunks.push(
      usageDeltaChunk({
        inputTokens: usage.promptTokenCount ?? /* v8 ignore next 1 */ 0,
        outputTokens:
          (usage.candidatesTokenCount ?? /* v8 ignore next 1 */ 0) +
          (usage.thoughtsTokenCount ?? /* v8 ignore next 1 */ 0),
        cacheReadTokens:
          usage.cachedContentTokenCount ?? /* v8 ignore next 1 */ 0,
        reasoningTokens: usage.thoughtsTokenCount ?? /* v8 ignore next 1 */ 0,
      })
    );
  }

  return chunks;
}

/**
 * Convert Google finish reason to Mirascope FinishReason.
 */
function decodeFinishReason(
  finishReason: GoogleFinishReasonType | undefined
): FinishReason | null {
  switch (finishReason) {
    case GoogleFinishReason.MAX_TOKENS:
      return FinishReason.MAX_TOKENS;
    /* v8 ignore start - refusal cases are rare and hard to trigger reliably */
    case GoogleFinishReason.SAFETY:
    case GoogleFinishReason.RECITATION:
    case GoogleFinishReason.BLOCKLIST:
    case GoogleFinishReason.PROHIBITED_CONTENT:
    case GoogleFinishReason.SPII:
      return FinishReason.REFUSAL;
    /* v8 ignore end */
    case GoogleFinishReason.STOP:
    case undefined:
      return null; // Normal completion
    /* v8 ignore start - exhaustive switch default */
    default:
      return null;
    /* v8 ignore end */
  }
}

/**
 * Create an async iterator that decodes Google stream responses to Mirascope chunks.
 *
 * @param stream - The Google content stream
 * @param includeThoughts - Whether to include thinking as thought chunks
 * @returns Async iterator of Mirascope chunks
 */
export async function* decodeStream(
  stream: AsyncIterable<GenerateContentResponse>,
  includeThoughts: boolean
): AsyncGenerator<StreamResponseChunk> {
  const state = createDecodeState(includeThoughts);

  for await (const response of stream) {
    const chunks = decodeStreamEvent(response, state);
    for (const chunk of chunks) {
      yield chunk;
    }
  }

  // Emit raw message chunk with properly structured Content (matching Python)
  yield rawMessageChunk({
    role: 'model',
    parts: state.accumulatedParts,
  } as unknown as Jsonable);
}
