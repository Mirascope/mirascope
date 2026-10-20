/**
 * Anthropic Beta stream decoding utilities.
 *
 * Converts Anthropic Beta MessageStreamEvent to Mirascope StreamResponseChunk.
 * The Beta API supports thinking blocks which are decoded as thought chunks.
 *
 * Used for strict tools and structured outputs routed through the beta API.
 */

/* v8 ignore start - beta SSE paths require live recordings; tool decoding has a focused test */

import type {
  BetaRawMessageStreamEvent,
  BetaStopReason,
} from "@anthropic-ai/sdk/resources/beta/messages/messages";

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
import {
  finishReasonChunk,
  usageDeltaChunk,
  rawStreamEventChunk,
  rawMessageChunk,
} from "@/llm/responses/chunks";
import { FinishReason } from "@/llm/responses/finish-reason";

/**
 * Accumulated content block for raw message persistence.
 */
type AccumulatedBlock =
  | { type: "text"; text: string }
  | { type: "thinking"; thinking: string; signature: string }
  | { type: "redacted_thinking"; data: string }
  | {
      type: "tool_use";
      id: string;
      name: string;
      input: Record<string, unknown>;
    };

/**
 * State tracking for stream decoding.
 */
interface DecodeState {
  /** Index of current content block being streamed */
  currentBlockIndex: number;
  /** Type of current content block */
  currentBlockType:
    | "text"
    | "thinking"
    | "redacted_thinking"
    | "tool_use"
    | null;
  /** Whether to include thoughts in output */
  includeThoughts: boolean;
  /** Current block being accumulated */
  currentBlock: AccumulatedBlock | null;
  accumulatedToolJson: string;
  /** All accumulated blocks for raw message */
  accumulatedBlocks: AccumulatedBlock[];
  /** Usage reported by message_start, which message_delta's usage includes */
  startUsage: {
    inputTokens: number;
    outputTokens: number;
    cacheReadTokens: number;
    cacheWriteTokens: number;
  };
}

/**
 * Create a new decode state for a fresh stream.
 */
export function createBetaDecodeState(includeThoughts: boolean): DecodeState {
  return {
    currentBlockIndex: -1,
    currentBlockType: null,
    includeThoughts,
    currentBlock: null,
    accumulatedToolJson: "",
    accumulatedBlocks: [],
    startUsage: {
      inputTokens: 0,
      outputTokens: 0,
      cacheReadTokens: 0,
      cacheWriteTokens: 0,
    },
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
  state: DecodeState,
): StreamResponseChunk[] {
  const chunks: StreamResponseChunk[] = [];

  // Always emit raw event chunk for debugging/passthrough
  chunks.push(rawStreamEventChunk(event));

  switch (event.type) {
    case "message_start":
      // Emit initial usage if available
      if (event.message.usage) {
        state.startUsage = {
          inputTokens: event.message.usage.input_tokens,
          outputTokens: event.message.usage.output_tokens,
          cacheReadTokens: event.message.usage.cache_read_input_tokens ?? 0,
          cacheWriteTokens:
            event.message.usage.cache_creation_input_tokens ?? 0,
        };
        chunks.push(usageDeltaChunk(state.startUsage));
      }
      break;

    case "content_block_start":
      state.currentBlockIndex = event.index;
      if (event.content_block.type === "text") {
        state.currentBlockType = "text";
        state.currentBlock = { type: "text", text: event.content_block.text };
        chunks.push(textStart());
        // If there's initial text, emit it
        if (event.content_block.text) {
          chunks.push(textChunk(event.content_block.text));
        }
      } else if (event.content_block.type === "thinking") {
        state.currentBlockType = "thinking";
        state.currentBlock = { type: "thinking", thinking: "", signature: "" };
        // Only emit thought chunks if includeThoughts is true
        if (state.includeThoughts) {
          chunks.push(thoughtStart());
          // If there's initial thinking text, emit it
          if (event.content_block.thinking) {
            chunks.push(thoughtChunk(event.content_block.thinking));
          }
        }
      } else if (event.content_block.type === "redacted_thinking") {
        state.currentBlockType = "redacted_thinking";
        state.currentBlock = {
          type: "redacted_thinking",
          data: event.content_block.data,
        };
      } else if (event.content_block.type === "tool_use") {
        state.currentBlockType = "tool_use";
        state.currentBlock = {
          type: "tool_use",
          id: event.content_block.id,
          name: event.content_block.name,
          input: {},
        };
        state.accumulatedToolJson = "";
        chunks.push(
          toolCallStart(event.content_block.id, event.content_block.name),
        );
      }
      break;

    case "content_block_delta":
      if (event.delta.type === "text_delta") {
        if (state.currentBlock?.type === "text") {
          state.currentBlock.text += event.delta.text;
        }
        chunks.push(textChunk(event.delta.text));
      } else if (event.delta.type === "thinking_delta") {
        if (state.currentBlock?.type === "thinking") {
          state.currentBlock.thinking += event.delta.thinking;
        }
        // Only emit thought chunks if includeThoughts is true
        if (state.includeThoughts) {
          chunks.push(thoughtChunk(event.delta.thinking));
        }
      } else if (event.delta.type === "signature_delta") {
        // Accumulate signature for round-tripping
        if (state.currentBlock?.type === "thinking") {
          state.currentBlock.signature += event.delta.signature;
        }
      } else if (event.delta.type === "input_json_delta") {
        state.accumulatedToolJson += event.delta.partial_json;
        if (state.currentBlock?.type === "tool_use") {
          chunks.push(
            toolCallChunk(state.currentBlock.id, event.delta.partial_json),
          );
        }
      }
      break;

    case "content_block_stop":
      if (state.currentBlockType === "text") {
        chunks.push(textEnd());
      } else if (
        state.currentBlockType === "tool_use" &&
        state.currentBlock?.type === "tool_use"
      ) {
        try {
          state.currentBlock.input = state.accumulatedToolJson
            ? (JSON.parse(state.accumulatedToolJson) as Record<string, unknown>)
            : {};
        } catch {
          state.currentBlock.input = {};
        }
        chunks.push(toolCallEnd(state.currentBlock.id));
      } else if (
        state.currentBlockType === "thinking" &&
        state.includeThoughts
      ) {
        chunks.push(thoughtEnd());
      }
      // Save accumulated block for raw message
      if (state.currentBlock) {
        state.accumulatedBlocks.push(state.currentBlock);
      }
      state.currentBlockType = null;
      state.currentBlock = null;
      break;

    case "message_delta":
      // Handle finish reason
      if (event.delta.stop_reason) {
        const finishReason = decodeBetaStopReason(event.delta.stop_reason);
        if (finishReason) {
          chunks.push(finishReasonChunk(finishReason));
        }
      }
      // message_delta usage is cumulative and includes message_start's counts.
      // With server tools its input and cache counts grow past them, so emit
      // only the growth. Counts the delta omits stay at message_start's values.
      if (event.usage) {
        const start = state.startUsage;
        chunks.push(
          usageDeltaChunk({
            inputTokens:
              (event.usage.input_tokens ?? start.inputTokens) -
              start.inputTokens,
            outputTokens: event.usage.output_tokens - start.outputTokens,
            cacheReadTokens:
              (event.usage.cache_read_input_tokens ?? start.cacheReadTokens) -
              start.cacheReadTokens,
            cacheWriteTokens:
              (event.usage.cache_creation_input_tokens ??
                start.cacheWriteTokens) - start.cacheWriteTokens,
          }),
        );
      }
      break;

    case "message_stop":
      // Stream complete - no additional chunks needed
      break;
  }

  return chunks;
}

/**
 * Convert Anthropic Beta stop reason to Mirascope FinishReason.
 */
function decodeBetaStopReason(
  stopReason: BetaStopReason | null,
): FinishReason | null {
  switch (stopReason) {
    case "max_tokens":
      return FinishReason.MAX_TOKENS;
    case "model_context_window_exceeded":
      return FinishReason.CONTEXT_LENGTH_EXCEEDED;
    case "refusal":
      return FinishReason.REFUSAL;
    case "end_turn":
    case "stop_sequence":
    case "tool_use":
    case "pause_turn":
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
  includeThoughts: boolean,
): AsyncGenerator<StreamResponseChunk> {
  const state = createBetaDecodeState(includeThoughts);

  for await (const event of stream) {
    const chunks = decodeBetaStreamEvent(event, state);
    for (const chunk of chunks) {
      yield chunk;
    }
  }

  // Emit raw message chunk with accumulated blocks for round-tripping
  yield rawMessageChunk({
    role: "assistant",
    content: state.accumulatedBlocks,
  } as unknown as Jsonable);
}

/* v8 ignore stop */
