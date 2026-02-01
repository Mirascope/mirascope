/**
 * Anthropic stream decoding utilities.
 *
 * Converts Anthropic MessageStreamEvent to Mirascope StreamResponseChunk.
 * The standard Anthropic API supports thinking blocks when extended thinking is enabled.
 */

import type { MessageStreamEvent } from "@anthropic-ai/sdk/resources/messages";

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
  | {
      type: "tool_use";
      id: string;
      name: string;
      input: Record<string, unknown>;
    }
  | { type: "thinking"; thinking: string; signature: string }
  | { type: "redacted_thinking"; data: string };

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
    | "tool_use"
    | "redacted_thinking"
    | null;
  /** Whether to include thoughts in output */
  includeThoughts: boolean;
  /** Current block being accumulated */
  currentBlock: AccumulatedBlock | null;
  /** Accumulated tool JSON for current tool_use block */
  accumulatedToolJson: string;
  /** All accumulated blocks for raw message */
  accumulatedBlocks: AccumulatedBlock[];
}

/**
 * Create a new decode state for a fresh stream.
 */
export function createDecodeState(includeThoughts: boolean): DecodeState {
  return {
    currentBlockIndex: -1,
    currentBlockType: null,
    includeThoughts,
    currentBlock: null,
    accumulatedToolJson: "",
    accumulatedBlocks: [],
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
  state: DecodeState,
): StreamResponseChunk[] {
  const chunks: StreamResponseChunk[] = [];

  // Always emit raw event chunk for debugging/passthrough
  chunks.push(rawStreamEventChunk(event));

  switch (event.type) {
    case "message_start":
      // Emit initial usage if available
      if (event.message.usage) {
        chunks.push(
          usageDeltaChunk({
            inputTokens: event.message.usage.input_tokens,
            outputTokens: event.message.usage.output_tokens,
          }),
        );
      }
      break;

    case "content_block_start":
      state.currentBlockIndex = event.index;
      if (event.content_block.type === "text") {
        state.currentBlockType = "text";
        state.currentBlock = { type: "text", text: event.content_block.text };
        chunks.push(textStart());
        // If there's initial text, emit it
        /* v8 ignore start - initial text in start event is rare */
        if (event.content_block.text) {
          chunks.push(textChunk(event.content_block.text));
        }
        /* v8 ignore stop */
      } else if (event.content_block.type === "thinking") {
        state.currentBlockType = "thinking";
        state.currentBlock = { type: "thinking", thinking: "", signature: "" };
        if (state.includeThoughts) {
          chunks.push(thoughtStart());
          // If there's initial thinking text, emit it
          /* v8 ignore start - initial thinking in start event is rare */
          if (event.content_block.thinking) {
            chunks.push(thoughtChunk(event.content_block.thinking));
          }
          /* v8 ignore stop */
        }
        /* v8 ignore start - tool streaming will be tested via e2e */
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
      } else if (event.content_block.type === "redacted_thinking") {
        state.currentBlockType = "redacted_thinking";
        state.currentBlock = {
          type: "redacted_thinking",
          data: event.content_block.data,
        };
      } else if (
        event.content_block.type === "server_tool_use" ||
        event.content_block.type === "web_search_tool_result"
      ) {
        // Skip server-side tool content - preserved in raw_message via rawStreamEventChunk
        state.currentBlockType = null;
        state.currentBlock = null;
      }
      /* v8 ignore stop */
      break;

    case "content_block_delta":
      /* v8 ignore start - server tool skip will be tested via e2e */
      // Skip deltas for server-side tool content
      if (state.currentBlock === null) {
        break;
      }
      /* v8 ignore stop */

      if (event.delta.type === "text_delta") {
        if (state.currentBlock?.type === "text") {
          state.currentBlock.text += event.delta.text;
        }
        chunks.push(textChunk(event.delta.text));
      } else if (event.delta.type === "thinking_delta") {
        if (state.currentBlock?.type === "thinking") {
          state.currentBlock.thinking += event.delta.thinking;
        }
        if (state.includeThoughts) {
          chunks.push(thoughtChunk(event.delta.thinking));
        }
      } else if (event.delta.type === "signature_delta") {
        // Accumulate signature for round-tripping
        if (state.currentBlock?.type === "thinking") {
          state.currentBlock.signature += event.delta.signature;
        }
        /* v8 ignore start - tool streaming will be tested via e2e */
      } else if (event.delta.type === "input_json_delta") {
        state.accumulatedToolJson += event.delta.partial_json;
        if (state.currentBlock?.type === "tool_use") {
          chunks.push(
            toolCallChunk(state.currentBlock.id, event.delta.partial_json),
          );
        }
      } else if (event.delta.type === "citations_delta") {
        // Skip citations delta - preserved in raw_message via rawStreamEventChunk
      }
      /* v8 ignore stop */
      break;

    case "content_block_stop":
      /* v8 ignore start - server tool skip will be tested via e2e */
      // Skip stop for server-side tool content
      if (state.currentBlock === null) {
        break;
      }
      /* v8 ignore stop */

      if (state.currentBlockType === "text") {
        chunks.push(textEnd());
        /* v8 ignore start - tool streaming will be tested via e2e */
      } else if (state.currentBlockType === "tool_use") {
        // Parse accumulated JSON and store in block
        if (state.currentBlock?.type === "tool_use") {
          try {
            state.currentBlock.input = state.accumulatedToolJson
              ? (JSON.parse(state.accumulatedToolJson) as Record<
                  string,
                  unknown
                >)
              : {};
          } catch {
            state.currentBlock.input = {};
          }
          chunks.push(toolCallEnd(state.currentBlock.id));
        }
      } else if (
        /* v8 ignore stop */
        state.currentBlockType === "thinking" &&
        state.includeThoughts
      ) {
        chunks.push(thoughtEnd());
      }
      // Save accumulated block for raw message
      state.accumulatedBlocks.push(state.currentBlock);
      state.currentBlockType = null;
      state.currentBlock = null;
      break;

    case "message_delta":
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
 * Convert Anthropic stop reason to Mirascope FinishReason.
 */
function decodeStopReason(
  stopReason:
    | "end_turn"
    | "max_tokens"
    | "stop_sequence"
    | "tool_use"
    | "refusal"
    | "pause_turn"
    | null,
): FinishReason | null {
  switch (stopReason) {
    case "max_tokens":
      return FinishReason.MAX_TOKENS;
    /* v8 ignore next 2 - refusal is rare and hard to trigger reliably */
    case "refusal":
      return FinishReason.REFUSAL;
    case "end_turn":
    case "stop_sequence":
    case "tool_use":
    case "pause_turn":
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
  includeThoughts: boolean,
): AsyncGenerator<StreamResponseChunk> {
  const state = createDecodeState(includeThoughts);

  for await (const event of stream) {
    const chunks = decodeStreamEvent(event, state);
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
