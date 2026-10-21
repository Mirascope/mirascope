import type { ResponseStreamEvent } from "openai/resources/responses/responses";

import { describe, expect, it } from "vitest";

import { APIError } from "@/llm/exceptions";

import { decodeStream } from "./decode-stream";

async function* events(list: unknown[]): AsyncGenerator<ResponseStreamEvent> {
  for (const event of list) {
    yield event as ResponseStreamEvent;
  }
}

async function collect(list: unknown[]) {
  const chunks = [];
  for await (const chunk of decodeStream(events(list), false)) {
    chunks.push(chunk);
  }
  return chunks;
}

describe("OpenAI Responses decodeStream", () => {
  it("raises when the stream reports response.failed", async () => {
    const stream = collect([
      { type: "response.created", response: { id: "resp_1", output: [] } },
      {
        type: "response.failed",
        response: {
          id: "resp_1",
          status: "failed",
          error: { code: "server_error", message: "The model crashed." },
          output: [],
        },
      },
    ]);

    await expect(stream).rejects.toThrow(APIError);
    await expect(stream).rejects.toThrow(/server_error.*The model crashed/);
  });

  it("raises with defaults when response.failed carries no error", async () => {
    const stream = collect([
      { type: "response.created", response: { id: "resp_1", output: [] } },
      {
        type: "response.failed",
        response: { id: "resp_1", status: "failed", output: [] },
      },
    ]);

    await expect(stream).rejects.toThrow(
      "OpenAI response failed: unknown_error: no error message",
    );
  });

  it("still completes a stream that ends with response.completed", async () => {
    const chunks = await collect([
      { type: "response.created", response: { id: "resp_1", output: [] } },
      {
        type: "response.completed",
        response: {
          id: "resp_1",
          status: "completed",
          output: [],
          usage: { input_tokens: 3, output_tokens: 2 },
        },
      },
    ]);

    expect(chunks.some((chunk) => chunk.type === "usage_delta_chunk")).toBe(
      true,
    );
  });
});
