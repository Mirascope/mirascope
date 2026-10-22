/**
 * OpenAI Completions stream decoding utilities.
 *
 * Converts OpenAI ChatCompletionChunk to Mirascope StreamResponseChunk.
 * The Chat Completions API does not support native reasoning/thinking.
 */

import type { ChatCompletionChunk } from "openai/resources/chat/completions";

import type { StreamResponseChunk } from "@/llm/responses/chunks";
import type { Jsonable } from "@/llm/types/jsonable";

import {
  textStart,
  textChunk,
  textEnd,
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
 * State tracking for stream decoding.
 * Matches Python SDK's _OpenAIChunkProcessor state.
 */
interface DecodeState {
  /** Current content type being streamed */
  currentContentType: "text" | "tool_call" | null;
  /** Open tool calls by slot (id of each call that has started) */
  currentTools: Map<number, string>;
  /** Maps the provider's tool call index to its slot in `currentTools` */
  indexSlots: Map<number, number>;
  /** Whether a refusal was encountered */
  refusalEncountered: boolean;
}

/**
 * Create a new decode state for a fresh stream.
 */
export function createDecodeState(): DecodeState {
  return {
    currentContentType: null,
    currentTools: new Map(),
    indexSlots: new Map(),
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
  state: DecodeState,
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
      }),
    );
  }

  const choice = chunk.choices[0];
  if (!choice) {
    return chunks;
  }

  const delta = choice.delta;

  // Handle text content (including refusal as text). Some servers open the
  // stream with an empty content string, which must not start a text block.
  const content = delta?.content || delta?.refusal;
  /* v8 ignore start - refusal is a rare edge case */
  if (delta?.refusal) {
    state.refusalEncountered = true;
  }
  /* v8 ignore stop */
  if (content) {
    if (state.currentContentType === null) {
      chunks.push(textStart());
      state.currentContentType = "text";
    }
    chunks.push(textChunk(content));
  }

  // Handle tool calls
  if (delta?.tool_calls) {
    /* v8 ignore start - rare to have text and tool calls in same chunk */
    if (state.currentContentType === "text") {
      chunks.push(textEnd());
    }
    /* v8 ignore stop */
    state.currentContentType = "tool_call";

    for (const toolCallDelta of delta.tool_calls) {
      const latest = Math.max(-1, ...state.currentTools.keys());
      const knownId = (slot: number) => state.currentTools.get(slot);
      let slot: number;
      if (toolCallDelta.index !== undefined) {
        // Some servers reuse one index for several calls; a different id on a
        // known index starts a new call. Calls may also interleave by index.
        const mapped = state.indexSlots.get(toolCallDelta.index);
        if (mapped === undefined) {
          slot = state.currentTools.has(toolCallDelta.index)
            ? latest + 1
            : toolCallDelta.index;
        } else if (
          toolCallDelta.id &&
          knownId(mapped) !== undefined &&
          toolCallDelta.id !== knownId(mapped)
        ) {
          slot = latest + 1;
        } else {
          slot = mapped;
        }
        state.indexSlots.set(toolCallDelta.index, slot);
      } else if (latest < 0) {
        // Gemini's OpenAI-compatible stream omits index. A new id starts the
        // next call; fragments without an id continue the latest call.
        slot = 0;
      } else if (toolCallDelta.id && toolCallDelta.id !== knownId(latest)) {
        slot = latest + 1;
      } else {
        slot = latest;
      }

      let currentToolId = state.currentTools.get(slot);
      if (currentToolId === undefined) {
        const name = toolCallDelta.function?.name;
        const toolId = toolCallDelta.id;
        /* v8 ignore start - defensive check for malformed streams */
        if (!name) {
          throw new Error(`Missing name for tool call at index ${slot}`);
        }
        if (!toolId) {
          throw new Error(`Missing id for tool call at index ${slot}`);
        }
        /* v8 ignore stop */

        // Without an index nothing can interleave, so the previous call is done
        if (toolCallDelta.index === undefined) {
          for (const openId of state.currentTools.values()) {
            chunks.push(toolCallEnd(openId));
          }
          state.currentTools.clear();
          state.indexSlots.clear();
        }
        state.currentTools.set(slot, toolId);
        currentToolId = toolId;
        chunks.push(toolCallStart(toolId, name));
      }

      // Emit tool call argument chunk if present
      if (toolCallDelta.function?.arguments) {
        chunks.push(
          toolCallChunk(currentToolId, toolCallDelta.function.arguments),
        );
      }
    }
  }

  // Handle finish reason
  if (choice.finish_reason) {
    if (state.currentContentType === "text") {
      chunks.push(textEnd());
    } else if (state.currentContentType === "tool_call") {
      for (const openId of state.currentTools.values()) {
        chunks.push(toolCallEnd(openId));
      }
      state.currentTools.clear();
      state.indexSlots.clear();
      /* v8 ignore start - defensive check for unknown content types */
    } else if (state.currentContentType !== null) {
      throw new Error("Unexpected content type");
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
  finishReason: ChatCompletionChunk.Choice["finish_reason"],
): FinishReason | null {
  switch (finishReason) {
    case "length":
      return FinishReason.MAX_TOKENS;
    /* v8 ignore start - content_filter is a rare edge case */
    case "content_filter":
      return FinishReason.REFUSAL;
    /* v8 ignore stop */
    case "stop":
    case "tool_calls":
    case "function_call":
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
  stream: AsyncIterable<ChatCompletionChunk>,
): AsyncGenerator<StreamResponseChunk> {
  const state = createDecodeState();

  for await (const chunk of stream) {
    const chunks = decodeStreamEvent(chunk, state);
    for (const c of chunks) {
      yield c;
    }
  }
}
