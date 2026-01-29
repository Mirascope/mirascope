/**
 * OpenAI Completions stream decoding utilities.
 *
 * Converts OpenAI ChatCompletionChunk to Mirascope StreamResponseChunk.
 * The Chat Completions API does not support native reasoning/thinking.
 */

import type { ChatCompletionChunk } from 'openai/resources/chat/completions';

import type { StreamResponseChunk } from '@/llm/responses/chunks';
import {
  textStart,
  textChunk,
  textEnd,
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
  /** Whether we're in a text block */
  inTextBlock: boolean;
}

/**
 * Create a new decode state for a fresh stream.
 */
export function createDecodeState(): DecodeState {
  return {
    inTextBlock: false,
  };
}

/**
 * Decode an OpenAI ChatCompletionChunk to Mirascope chunks.
 *
 * @param chunk - The OpenAI stream chunk
 * @param state - Mutable state tracking current block
 * @returns Array of Mirascope chunks (may be empty or multiple)
 */
export function decodeStreamEvent(
  chunk: ChatCompletionChunk,
  state: DecodeState
): StreamResponseChunk[] {
  const chunks: StreamResponseChunk[] = [];

  // Always emit raw event chunk for debugging/passthrough
  chunks.push(rawStreamEventChunk(chunk));

  // Emit raw message chunk
  chunks.push(rawMessageChunk(chunk as unknown as Jsonable));

  const choice = chunk.choices[0];

  if (choice?.delta) {
    const delta = choice.delta;

    if (delta.content) {
      if (!state.inTextBlock) {
        chunks.push(textStart());
        state.inTextBlock = true;
      }
      chunks.push(textChunk(delta.content));
    }

    /* v8 ignore start - refusal is a rare edge case */
    if (delta.refusal) {
      if (!state.inTextBlock) {
        chunks.push(textStart());
        state.inTextBlock = true;
      }
      chunks.push(textChunk(delta.refusal));
    }
    /* v8 ignore stop */
  }

  if (choice?.finish_reason) {
    // Close any open text block
    if (state.inTextBlock) {
      chunks.push(textEnd());
      state.inTextBlock = false;
    }

    const finishReason = decodeFinishReason(choice.finish_reason);
    if (finishReason) {
      chunks.push(finishReasonChunk(finishReason));
    }
  }

  // Handle usage (typically in the last chunk when stream_options.include_usage is true)
  if (chunk.usage) {
    chunks.push(
      usageDeltaChunk({
        inputTokens: chunk.usage.prompt_tokens,
        outputTokens: chunk.usage.completion_tokens,
        /* v8 ignore start - optional details may not be present */
        cacheReadTokens: chunk.usage.prompt_tokens_details?.cached_tokens ?? 0,
        reasoningTokens:
          chunk.usage.completion_tokens_details?.reasoning_tokens ?? 0,
        /* v8 ignore stop */
      })
    );
  }

  return chunks;
}

/**
 * Convert OpenAI finish reason to Mirascope FinishReason.
 */
function decodeFinishReason(
  finishReason: ChatCompletionChunk.Choice['finish_reason']
): FinishReason | null {
  switch (finishReason) {
    case 'length':
      return FinishReason.MAX_TOKENS;
    /* v8 ignore start - content_filter is a rare edge case */
    case 'content_filter':
      return FinishReason.REFUSAL;
    /* v8 ignore stop */
    case 'stop':
    case 'tool_calls':
    case 'function_call':
      return null; // Normal completion
    /* v8 ignore start - exhaustive switch default */
    default:
      return null;
    /* v8 ignore stop */
  }
}

/**
 * Create an async iterator that decodes OpenAI stream chunks to Mirascope chunks.
 *
 * @param stream - The OpenAI completion stream
 * @returns Async iterator of Mirascope chunks
 */
export async function* decodeStream(
  stream: AsyncIterable<ChatCompletionChunk>
): AsyncGenerator<StreamResponseChunk> {
  const state = createDecodeState();

  for await (const chunk of stream) {
    const chunks = decodeStreamEvent(chunk, state);
    for (const c of chunks) {
      yield c;
    }
  }
}
