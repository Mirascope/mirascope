/**
 * Unit tests for Anthropic stream usage decoding.
 *
 * message_delta usage is cumulative, so the usage deltas emitted for a stream
 * must sum to its final counts.
 */

import type { BetaRawMessageStreamEvent } from "@anthropic-ai/sdk/resources/beta/messages/messages";
import type { MessageStreamEvent } from "@anthropic-ai/sdk/resources/messages";

import { describe, it, expect } from "vitest";

import type { StreamResponseChunk } from "@/llm/responses/chunks";

import { FinishReason } from "@/llm/responses/finish-reason";

import {
  createBetaDecodeState,
  decodeBetaStreamEvent,
} from "./beta-decode-stream";
import { createDecodeState, decodeStreamEvent } from "./decode-stream";

type Usage = Record<string, unknown>;

function messageStart(usage: Usage) {
  return {
    type: "message_start",
    message: {
      id: "msg_123",
      type: "message",
      role: "assistant",
      content: [],
      model: "claude-haiku-4-5",
      stop_reason: null,
      stop_sequence: null,
      usage,
    },
  };
}

function messageDelta(usage: Usage) {
  return {
    type: "message_delta",
    delta: { stop_reason: "end_turn", stop_sequence: null },
    usage,
  };
}

const decoders = [
  {
    name: "standard",
    decode: (events: unknown[]) => {
      const state = createDecodeState(false);
      return events.flatMap((event) =>
        decodeStreamEvent(event as MessageStreamEvent, state),
      );
    },
  },
  {
    name: "beta",
    decode: (events: unknown[]) => {
      const state = createBetaDecodeState(false);
      return events.flatMap((event) =>
        decodeBetaStreamEvent(event as BetaRawMessageStreamEvent, state),
      );
    },
  },
];

function sumUsage(chunks: StreamResponseChunk[]) {
  const total = {
    inputTokens: 0,
    outputTokens: 0,
    cacheReadTokens: 0,
    cacheWriteTokens: 0,
  };
  for (const chunk of chunks) {
    if (chunk.type === "usage_delta_chunk") {
      total.inputTokens += chunk.inputTokens;
      total.outputTokens += chunk.outputTokens;
      total.cacheReadTokens += chunk.cacheReadTokens;
      total.cacheWriteTokens += chunk.cacheWriteTokens;
    }
  }
  return total;
}

describe.each(decoders)("$name stream usage decoding", ({ decode }) => {
  it("sums to the cumulative message_delta usage", () => {
    // With server tools, message_delta's input and cache counts grow past
    // message_start's (values from a recorded web search stream).
    const chunks = decode([
      messageStart({
        input_tokens: 2285,
        output_tokens: 25,
        cache_creation_input_tokens: 0,
        cache_read_input_tokens: 0,
      }),
      messageDelta({
        input_tokens: 2292,
        output_tokens: 150,
        cache_creation_input_tokens: 12032,
        cache_read_input_tokens: 0,
        server_tool_use: { web_search_requests: 1 },
      }),
    ]);

    expect(sumUsage(chunks)).toEqual({
      inputTokens: 14324,
      outputTokens: 150,
      cacheReadTokens: 0,
      cacheWriteTokens: 12032,
    });
  });

  it("keeps message_start counts that message_delta omits", () => {
    const chunks = decode([
      messageStart({
        input_tokens: 10,
        output_tokens: 1,
        cache_creation_input_tokens: null,
        cache_read_input_tokens: 40,
      }),
      messageDelta({
        input_tokens: null,
        output_tokens: 12,
        cache_creation_input_tokens: null,
        cache_read_input_tokens: null,
      }),
    ]);

    expect(sumUsage(chunks)).toEqual({
      inputTokens: 50,
      outputTokens: 12,
      cacheReadTokens: 40,
      cacheWriteTokens: 0,
    });
  });

  it("counts missing cache counts as zero", () => {
    const chunks = decode([
      messageStart({
        input_tokens: 10,
        output_tokens: 1,
        cache_creation_input_tokens: null,
        cache_read_input_tokens: null,
      }),
      messageDelta({ input_tokens: 10, output_tokens: 12 }),
    ]);

    expect(sumUsage(chunks)).toEqual({
      inputTokens: 10,
      outputTokens: 12,
      cacheReadTokens: 0,
      cacheWriteTokens: 0,
    });
  });

  it("counts each cumulative usage update only once", () => {
    const chunks = decode([
      messageStart({
        input_tokens: 10,
        output_tokens: 1,
        cache_creation_input_tokens: 5,
        cache_read_input_tokens: 0,
      }),
      messageDelta({
        input_tokens: 12,
        output_tokens: 4,
        cache_creation_input_tokens: 9,
        cache_read_input_tokens: 3,
      }),
      messageDelta({
        input_tokens: 13,
        output_tokens: 8,
        cache_creation_input_tokens: 10,
        cache_read_input_tokens: 7,
      }),
    ]);

    expect(sumUsage(chunks)).toEqual({
      inputTokens: 30,
      outputTokens: 8,
      cacheReadTokens: 7,
      cacheWriteTokens: 10,
    });
  });
});

describe.each(decoders)("$name stream stop reason decoding", ({ decode }) => {
  const finishReasons = (stopReason: string) =>
    decode([
      messageStart({ input_tokens: 10, output_tokens: 1 }),
      {
        type: "message_delta",
        delta: { stop_reason: stopReason, stop_sequence: null },
        usage: { output_tokens: 5 },
      },
    ])
      .filter((chunk) => chunk.type === "finish_reason_chunk")
      .map((chunk) => chunk.finishReason);

  it.each([
    ["max_tokens", [FinishReason.MAX_TOKENS]],
    ["refusal", [FinishReason.REFUSAL]],
    ["model_context_window_exceeded", [FinishReason.CONTEXT_LENGTH_EXCEEDED]],
    ["end_turn", []],
  ])("maps stop_reason %s", (stopReason, expected) => {
    expect(finishReasons(stopReason)).toEqual(expected);
  });
});
