import {
  FinishReason as GoogleFinishReason,
  GenerateContentResponse,
} from "@google/genai";
import { describe, expect, it } from "vitest";

import {
  createDecodeState,
  decodeStreamEvent,
} from "@/llm/providers/google/decode-stream";
import type { UsageDeltaChunk } from "@/llm/responses/chunks";
import { FinishReason } from "@/llm/responses/finish-reason";

describe("Google stream metadata without content", () => {
  it("keeps finish reason and usage from a contentless candidate", () => {
    const chunks = decodeStreamEvent(
      Object.assign(new GenerateContentResponse(), {
        candidates: [{ finishReason: GoogleFinishReason.MAX_TOKENS }],
        usageMetadata: {
          promptTokenCount: 100,
          candidatesTokenCount: 0,
          thoughtsTokenCount: 50,
        },
      }),
      createDecodeState(true),
    );

    expect(chunks).toContainEqual({
      type: "finish_reason_chunk",
      finishReason: FinishReason.MAX_TOKENS,
    });
    expect(chunks).toContainEqual({
      type: "usage_delta_chunk",
      inputTokens: 100,
      outputTokens: 50,
      cacheReadTokens: 0,
      cacheWriteTokens: 0,
      reasoningTokens: 50,
    });
  });

  it("keeps usage from a chunk with no candidate", () => {
    const chunks = decodeStreamEvent(
      Object.assign(new GenerateContentResponse(), {
        candidates: [],
        usageMetadata: { promptTokenCount: 100, candidatesTokenCount: 25 },
      }),
      createDecodeState(false),
    );

    expect(chunks).toContainEqual({
      type: "usage_delta_chunk",
      inputTokens: 100,
      outputTokens: 25,
      cacheReadTokens: 0,
      cacheWriteTokens: 0,
      reasoningTokens: 0,
    });
  });
});

describe("Google stream cumulative usage", () => {
  const usageChunks = (
    usageMetadata: Record<string, number>,
    state: ReturnType<typeof createDecodeState>,
  ) =>
    decodeStreamEvent(
      Object.assign(new GenerateContentResponse(), {
        candidates: [],
        usageMetadata,
      }),
      state,
    ).filter(
      (chunk): chunk is UsageDeltaChunk => chunk.type === "usage_delta_chunk",
    );

  it("emits only the growth over the previous chunk's totals", () => {
    const state = createDecodeState(true);

    expect(
      usageChunks({ promptTokenCount: 10, candidatesTokenCount: 5 }, state),
    ).toEqual([
      {
        type: "usage_delta_chunk",
        inputTokens: 10,
        outputTokens: 5,
        cacheReadTokens: 0,
        cacheWriteTokens: 0,
        reasoningTokens: 0,
      },
    ]);
    expect(
      usageChunks(
        {
          promptTokenCount: 10,
          candidatesTokenCount: 12,
          thoughtsTokenCount: 4,
          cachedContentTokenCount: 6,
        },
        state,
      ),
    ).toEqual([
      {
        type: "usage_delta_chunk",
        inputTokens: 0,
        outputTokens: 11,
        cacheReadTokens: 6,
        cacheWriteTokens: 0,
        reasoningTokens: 4,
      },
    ]);
  });

  it("sums to the final totals over a whole stream", () => {
    const state = createDecodeState(false);
    const totals = [
      { promptTokenCount: 20, candidatesTokenCount: 3 },
      { promptTokenCount: 20, candidatesTokenCount: 9 },
      { promptTokenCount: 20, candidatesTokenCount: 15 },
    ];
    const deltas = totals.flatMap((metadata) => usageChunks(metadata, state));

    const sum = (key: "inputTokens" | "outputTokens") =>
      deltas.reduce((total, chunk) => total + chunk[key], 0);
    expect(sum("inputTokens")).toBe(20);
    expect(sum("outputTokens")).toBe(15);
  });
});
