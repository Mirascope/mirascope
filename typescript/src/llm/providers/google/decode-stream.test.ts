import {
  FinishReason as GoogleFinishReason,
  GenerateContentResponse,
} from "@google/genai";
import { describe, expect, it } from "vitest";

import {
  createDecodeState,
  decodeStreamEvent,
} from "@/llm/providers/google/decode-stream";
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

describe("Google stream image refusal finish reasons", () => {
  it.each([
    GoogleFinishReason.IMAGE_SAFETY,
    GoogleFinishReason.IMAGE_PROHIBITED_CONTENT,
    GoogleFinishReason.IMAGE_RECITATION,
  ])("maps %s to REFUSAL", (finishReason) => {
    const chunks = decodeStreamEvent(
      Object.assign(new GenerateContentResponse(), {
        candidates: [{ finishReason }],
      }),
      createDecodeState(true),
    );

    expect(chunks).toContainEqual({
      type: "finish_reason_chunk",
      finishReason: FinishReason.REFUSAL,
    });
  });
});
