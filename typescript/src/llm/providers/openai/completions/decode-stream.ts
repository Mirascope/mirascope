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
 * State tracking for stream decoding.
 * Matches Python SDK's _OpenAIChunkProcessor state.
 */
interface DecodeState {
  /** Current content type being streamed */
  currentContentType: 'text' | 'tool_call' | null;
  /** Index of the current tool call being streamed */
  currentToolIndex: number | null;
  /** ID of the current tool call being streamed */
  currentToolId: string | null;
  /** Whether a refusal was encountered */
  refusalEncountered: boolean;
}

/**
 * Create a new decode state for a fresh stream.
 */
export function createDecodeState(): DecodeState {
  return {
    currentContentType: null,
    currentToolIndex: null,
    currentToolId: null,
    refusalEncountered: false,
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

  const choice = chunk.choices[0];
  if (!choice) {
    return chunks;
  }

  const delta = choice.delta;

  // Handle text content (including refusal as text)
  const content = delta?.content ?? delta?.refusal;
  /* v8 ignore start - refusal is a rare edge case */
  if (delta?.refusal) {
    state.refusalEncountered = true;
  }
  /* v8 ignore stop */
  if (content !== undefined && content !== null) {
    if (state.currentContentType === null) {
      chunks.push(textStart());
      state.currentContentType = 'text';
    }
    chunks.push(textChunk(content));
  }

  // Handle tool calls
  if (delta?.tool_calls) {
    /* v8 ignore start - rare to have text and tool calls in same chunk */
    if (state.currentContentType === 'text') {
      chunks.push(textEnd());
    }
    /* v8 ignore stop */
    state.currentContentType = 'tool_call';

    for (const toolCallDelta of delta.tool_calls) {
      const index = toolCallDelta.index;

      // Check for out-of-order tool call data
      /* v8 ignore start - defensive check for malformed streams */
      if (state.currentToolIndex !== null && state.currentToolIndex > index) {
        throw new Error(
          `Received tool data for already-finished tool at index ${index}`
        );
      }
      /* v8 ignore stop */

      // If we're moving to a new tool (higher index), close the previous one
      if (state.currentToolIndex !== null && state.currentToolIndex < index) {
        /* v8 ignore start - defensive check */
        if (state.currentToolId === null) {
          throw new Error('No current_tool_id for ToolCallEndChunk');
        }
        /* v8 ignore stop */
        chunks.push(toolCallEndChunk(state.currentToolId));
        state.currentToolIndex = null;
      }

      // Start a new tool call if we don't have one at this index
      if (state.currentToolIndex === null) {
        const name = toolCallDelta.function?.name;
        const toolId = toolCallDelta.id;
        /* v8 ignore start - defensive check for malformed streams */
        if (!name) {
          throw new Error(`Missing name for tool call at index ${index}`);
        }
        if (!toolId) {
          throw new Error(`Missing id for tool call at index ${index}`);
        }
        /* v8 ignore stop */

        state.currentToolIndex = index;
        state.currentToolId = toolId;
        chunks.push(toolCallStartChunk(toolId, name));
      }

      // Emit tool call argument chunk if present
      if (toolCallDelta.function?.arguments) {
        /* v8 ignore start - defensive check */
        if (state.currentToolId === null) {
          throw new Error('No current_tool_id for ToolCallChunk');
        }
        /* v8 ignore stop */
        chunks.push(
          toolCallChunk(state.currentToolId, toolCallDelta.function.arguments)
        );
      }
    }
  }

  // Handle finish reason
  if (choice.finish_reason) {
    if (state.currentContentType === 'text') {
      chunks.push(textEnd());
    } else if (state.currentContentType === 'tool_call') {
      /* v8 ignore start - defensive check */
      if (state.currentToolId === null) {
        throw new Error('No current_tool_id for ToolCallEndChunk');
      }
      /* v8 ignore stop */
      chunks.push(toolCallEndChunk(state.currentToolId));
      /* v8 ignore start - defensive check for unknown content types */
    } else if (state.currentContentType !== null) {
      throw new Error('Unexpected content type');
    }
    /* v8 ignore stop */

    // Emit finish reason if applicable
    /* v8 ignore next 2 - refusal is a rare edge case */
    const finishReason = state.refusalEncountered
      ? FinishReason.REFUSAL
      : decodeFinishReason(choice.finish_reason);
    if (finishReason !== null) {
      chunks.push(finishReasonChunk(finishReason));
    }
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
