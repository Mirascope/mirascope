/**
 * OpenAI Responses stream decoding utilities.
 *
 * Converts OpenAI Responses API streaming events to Mirascope StreamResponseChunk.
 * The Responses API supports reasoning/thinking through summary text.
 */

import type {
  ResponseStreamEvent,
  ResponseTextDeltaEvent,
  ResponseCompletedEvent,
  ResponseIncompleteEvent,
} from "openai/resources/responses/responses";

import type { StreamResponseChunk } from "@/llm/responses/chunks";
import type { Jsonable } from "@/llm/types/jsonable";

import {
  textStart,
  textChunk,
  textEnd,
  thoughtStart,
  thoughtChunk,
  thoughtEnd,
  toolCallStart,
  toolCallChunk,
  toolCallEnd,
} from "@/llm/content";
import { serializeOutputItem } from "@/llm/providers/openai/responses/_utils";
import {
  finishReasonChunk,
  usageDeltaChunk,
  rawStreamEventChunk,
  rawMessageChunk,
} from "@/llm/responses/chunks";
import { FinishReason } from "@/llm/responses/finish-reason";

/**
 * State tracking for stream decoding.
 */
interface DecodeState {
  /** Whether we're in a text block */
  inTextBlock: boolean;
  /** Whether we're in a thought block */
  inThoughtBlock: boolean;
  /** ID of current tool call being streamed */
  currentToolCallId: string | null;
  /** Whether to include thoughts in output */
  includeThoughts: boolean;
}

/**
 * Create a new decode state for a fresh stream.
 */
export function createDecodeState(includeThoughts: boolean): DecodeState {
  return {
    inTextBlock: false,
    inThoughtBlock: false,
    currentToolCallId: null,
    includeThoughts,
  };
}

/**
 * Decode an OpenAI Responses API stream event to Mirascope chunks.
 *
 * @param event - The OpenAI Responses stream event
 * @param state - Mutable state tracking current block
 * @returns Array of Mirascope chunks (may be empty or multiple)
 */
export function decodeStreamEvent(
  event: ResponseStreamEvent,
  state: DecodeState,
): StreamResponseChunk[] {
  const chunks: StreamResponseChunk[] = [];

  // Always emit raw event chunk for debugging/passthrough
  chunks.push(rawStreamEventChunk(event));

  switch (event.type) {
    case "response.created":
      // Emit raw message chunk with initial response data
      chunks.push(rawMessageChunk(event.response as unknown as Jsonable));
      break;

    case "response.output_text.delta":
      handleTextDelta(event, state, chunks);
      break;

    case "response.output_text.done":
      if (state.inTextBlock) {
        chunks.push(textEnd());
        state.inTextBlock = false;
      }
      break;

    case "response.reasoning_summary_text.delta":
      if (state.includeThoughts) {
        handleThoughtDelta(event, state, chunks);
      }
      break;

    case "response.reasoning_summary_text.done":
      if (state.inThoughtBlock && state.includeThoughts) {
        chunks.push(thoughtEnd());
        state.inThoughtBlock = false;
      }
      break;

    /* v8 ignore start - OpenAI Responses API not in tools test providers */
    case "response.output_item.added":
      if (event.item.type === "function_call") {
        state.currentToolCallId = event.item.call_id;
        chunks.push(toolCallStart(event.item.call_id, event.item.name));
      }
      break;

    case "response.function_call_arguments.delta":
      if (state.currentToolCallId) {
        chunks.push(toolCallChunk(state.currentToolCallId, event.delta));
      }
      break;

    case "response.function_call_arguments.done":
      if (state.currentToolCallId) {
        chunks.push(toolCallEnd(state.currentToolCallId));
        state.currentToolCallId = null;
      }
      break;
    /* v8 ignore stop */

    case "response.completed":
    case "response.incomplete":
      // Close any open blocks
      /* v8 ignore start - blocks typically closed before completion event */
      if (state.inTextBlock) {
        chunks.push(textEnd());
        state.inTextBlock = false;
      }
      if (state.inThoughtBlock) {
        chunks.push(thoughtEnd());
        state.inThoughtBlock = false;
      }
      /* v8 ignore stop */

      handleCompleted(event, chunks);
      break;

    // Handle other events we might want to process
    /* v8 ignore start - refusal events are rare edge cases */
    case "response.refusal.delta":
      // Treat refusal as text
      handleRefusalDelta(event, state, chunks);
      break;

    case "response.refusal.done":
      // Close text block and emit refusal finish reason
      if (state.inTextBlock) {
        chunks.push(textEnd());
        state.inTextBlock = false;
      }
      chunks.push(finishReasonChunk(FinishReason.REFUSAL));
      break;
    /* v8 ignore stop */

    // Other events don't produce content chunks
    default:
      break;
  }

  return chunks;
}

/**
 * Handle text delta event.
 */
function handleTextDelta(
  event: ResponseTextDeltaEvent,
  state: DecodeState,
  chunks: StreamResponseChunk[],
): void {
  if (!state.inTextBlock) {
    // Close thought block if transitioning from thoughts to text
    /* v8 ignore start - edge case when thoughts precede text */
    if (state.inThoughtBlock) {
      chunks.push(thoughtEnd());
      state.inThoughtBlock = false;
    }
    /* v8 ignore stop */
    chunks.push(textStart());
    state.inTextBlock = true;
  }
  chunks.push(textChunk(event.delta));
}

/**
 * Handle reasoning summary delta event (thoughts).
 */
function handleThoughtDelta(
  event: { type: "response.reasoning_summary_text.delta"; delta: string },
  state: DecodeState,
  chunks: StreamResponseChunk[],
): void {
  if (!state.inThoughtBlock) {
    // Close text block if transitioning from text to thoughts
    /* v8 ignore start - edge case when text precedes thoughts */
    if (state.inTextBlock) {
      chunks.push(textEnd());
      state.inTextBlock = false;
    }
    /* v8 ignore stop */
    chunks.push(thoughtStart());
    state.inThoughtBlock = true;
  }
  chunks.push(thoughtChunk(event.delta));
}

/**
 * Handle refusal delta event.
 */
/* v8 ignore start - refusal events are rare edge cases */
function handleRefusalDelta(
  event: { type: "response.refusal.delta"; delta: string },
  state: DecodeState,
  chunks: StreamResponseChunk[],
): void {
  // Treat refusal as text content
  if (!state.inTextBlock) {
    chunks.push(textStart());
    state.inTextBlock = true;
  }
  chunks.push(textChunk(event.delta));
}
/* v8 ignore stop */

/**
 * Handle response.completed or response.incomplete event for finish reason and usage.
 */
function handleCompleted(
  event: ResponseCompletedEvent | ResponseIncompleteEvent,
  chunks: StreamResponseChunk[],
): void {
  const response = event.response;

  // Emit the completed output items as rawMessage for round-tripping.
  // This overrides the initial rawMessage from response.created and enables
  // encodeMessages to reuse the original output items (with correct IDs)
  // when resuming a conversation after tool execution.
  if (response.output) {
    chunks.push(
      rawMessageChunk(
        response.output.map(serializeOutputItem) as unknown as Jsonable,
      ),
    );
  }

  // Check for finish reason from incomplete_details
  /* v8 ignore start - incomplete_details only present when stream is incomplete */
  if (response.incomplete_details) {
    const reason = response.incomplete_details.reason;
    if (reason === "max_output_tokens") {
      chunks.push(finishReasonChunk(FinishReason.MAX_TOKENS));
    } else if (reason === "content_filter") {
      chunks.push(finishReasonChunk(FinishReason.REFUSAL));
    }
  }
  /* v8 ignore stop */

  // Emit usage if available
  if (response.usage) {
    chunks.push(
      usageDeltaChunk({
        inputTokens: response.usage.input_tokens,
        outputTokens: response.usage.output_tokens,
        cacheReadTokens:
          /* v8 ignore next 1 */
          response.usage.input_tokens_details?.cached_tokens ?? 0,
        reasoningTokens:
          /* v8 ignore next 1 */
          response.usage.output_tokens_details?.reasoning_tokens ?? 0,
      }),
    );
  }
}

/**
 * Create an async iterator that decodes OpenAI Responses stream events to Mirascope chunks.
 *
 * @param stream - The OpenAI Responses stream
 * @param includeThoughts - Whether to include reasoning blocks as thought chunks
 * @returns Async iterator of Mirascope chunks
 */
export async function* decodeStream(
  stream: AsyncIterable<ResponseStreamEvent>,
  includeThoughts: boolean,
): AsyncGenerator<StreamResponseChunk> {
  const state = createDecodeState(includeThoughts);

  for await (const event of stream) {
    const chunks = decodeStreamEvent(event, state);
    for (const chunk of chunks) {
      yield chunk;
    }
  }
}
