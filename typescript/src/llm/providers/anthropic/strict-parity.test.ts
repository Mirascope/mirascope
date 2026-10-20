import type { BetaRawMessageStreamEvent } from "@anthropic-ai/sdk/resources/beta/messages/messages";

import { afterEach, describe, expect, it, vi } from "vitest";
import { z } from "zod";

import { FeatureNotSupportedError } from "@/llm/exceptions";
import { defineFormat } from "@/llm/formatting";
import { user } from "@/llm/messages";
import { defineTool, WebSearchTool } from "@/llm/tools";

import { buildRequestParams } from "./_utils";
import { decodeBetaStream } from "./beta-decode-stream";
import { buildBetaRequestParams } from "./beta-encode";
import { AnthropicProvider } from "./provider";

afterEach(() => vi.unstubAllGlobals());

function response(
  content: unknown[],
  stopReason = "end_turn",
): globalThis.Response {
  return new globalThis.Response(
    JSON.stringify({
      id: "msg_test",
      type: "message",
      role: "assistant",
      content,
      model: "claude-sonnet-4-5",
      stop_reason: stopReason,
      stop_sequence: null,
      usage: { input_tokens: 1, output_tokens: 1 },
    }),
    { headers: { "content-type": "application/json" } },
  );
}

describe("Anthropic strict parity", () => {
  it("streams beta tool arguments and preserves the completed call", async () => {
    const events = [
      {
        type: "content_block_start",
        index: 0,
        content_block: {
          type: "tool_use",
          id: "tool_1",
          name: "lookup",
          input: {},
        },
      },
      {
        type: "content_block_delta",
        index: 0,
        delta: { type: "input_json_delta", partial_json: '{"city":"Paris"}' },
      },
      { type: "content_block_stop", index: 0 },
    ] as unknown as BetaRawMessageStreamEvent[];
    const stream = (async function* () {
      yield* events;
    })();

    const chunks = [];
    for await (const chunk of decodeBetaStream(stream, false))
      chunks.push(chunk);

    expect(chunks.map((chunk) => chunk.type)).toContain(
      "tool_call_start_chunk",
    );
    expect(chunks.map((chunk) => chunk.type)).toContain("tool_call_chunk");
    expect(chunks.map((chunk) => chunk.type)).toContain("tool_call_end_chunk");
    expect(chunks.at(-1)).toMatchObject({
      type: "raw_message_chunk",
      rawMessage: {
        content: [{ type: "tool_use", id: "tool_1", input: { city: "Paris" } }],
      },
    });
  });
  it("preserves nonstrict and provider tools when adding a format tool", () => {
    const lookup = defineTool({
      name: "lookup",
      description: "Lookup",
      strict: false,
      validator: z.object({ city: z.string() }),
      tool: ({ city }) => city,
    });
    const format = defineFormat({
      mode: "tool",
      __schema: {
        type: "object",
        properties: { answer: { type: "string" } },
        required: ["answer"],
        additionalProperties: false,
      },
    });

    const request = buildBetaRequestParams(
      "anthropic/claude-sonnet-4-5",
      [user("lookup")],
      [lookup, new WebSearchTool()],
      format,
    );

    expect(request.tools?.[0]).toMatchObject({ name: "web_search" });
    expect(request.tools?.[1]).toMatchObject({ name: "lookup", strict: false });
    expect(request.tools?.[2]).toMatchObject({ strict: true });
  });
  it("rejects explicit strict tools on models without structured outputs", () => {
    const tool = defineTool({
      name: "lookup",
      description: "Lookup",
      strict: true,
      validator: z.object({ city: z.string() }),
      tool: ({ city }) => city,
    });
    expect(() =>
      buildRequestParams("anthropic/claude-sonnet-4", [user("lookup")], [tool]),
    ).toThrow(FeatureNotSupportedError);
  });
  it("routes strict format through beta with an output schema", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(response([{ type: "text", text: '{"answer":42}' }]));
    vi.stubGlobal("fetch", fetchMock);
    const format = defineFormat({
      mode: "strict",
      __schema: {
        type: "object",
        properties: { answer: { type: "number" } },
        required: ["answer"],
        additionalProperties: false,
      },
    });

    const result = await new AnthropicProvider({ apiKey: "test-key" }).call({
      modelId: "anthropic/claude-sonnet-4-5",
      messages: [user("answer")],
      format,
    });

    expect(result.parse()).toEqual({ answer: 42 });
    const [, init] = fetchMock.mock.calls[0] as [URL, RequestInit];
    const body = JSON.parse(String(init.body)) as {
      output_config: { format: { type: string; schema: object } };
    };
    expect(body.output_config.format).toEqual({
      type: "json_schema",
      schema: format.schema,
    });
    expect(new Headers(init.headers).get("anthropic-beta")).toContain(
      "structured-outputs-2025-11-13",
    );
  });

  it("routes default strict tools through beta and decodes tool calls", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      response(
        [
          {
            type: "tool_use",
            id: "tool_1",
            name: "lookup",
            input: { city: "Paris" },
          },
        ],
        "tool_use",
      ),
    );
    vi.stubGlobal("fetch", fetchMock);
    const lookup = defineTool({
      name: "lookup",
      description: "Look up a city",
      validator: z.object({ city: z.string(), unit: z.string().optional() }),
      tool: ({ city }) => city,
    });

    const result = await new AnthropicProvider({ apiKey: "test-key" }).call({
      modelId: "anthropic/claude-sonnet-4-5",
      messages: [user("lookup")],
      tools: [lookup],
    });

    expect(result.toolCalls[0]?.name).toBe("lookup");
    const [, init] = fetchMock.mock.calls[0] as [URL, RequestInit];
    const body = JSON.parse(String(init.body)) as {
      tools: { strict: boolean; input_schema: object }[];
    };
    expect(body.tools[0]?.strict).toBe(true);
    expect(body.tools[0]?.input_schema).toMatchObject({
      additionalProperties: false,
    });
  });
});
