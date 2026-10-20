import type { ChatCompletionChunk } from "openai/resources/chat/completions";

import { describe, expect, it } from "vitest";

import { createDecodeState, decodeStreamEvent } from "./decode-stream";

function chunk(
  toolCalls: Record<string, unknown>[],
  finishReason: string | null = null,
) {
  return {
    id: "chatcmpl-test",
    created: 1,
    model: "gemini-3.5-flash",
    object: "chat.completion.chunk",
    choices: [
      {
        index: 0,
        delta: { tool_calls: toolCalls },
        finish_reason: finishReason,
      },
    ],
  } as unknown as ChatCompletionChunk;
}

function call(
  id: string | undefined,
  args: string,
  name?: string,
  index?: number,
) {
  return {
    ...(index === undefined ? {} : { index }),
    ...(id === undefined ? {} : { id }),
    type: "function",
    function: { ...(name === undefined ? {} : { name }), arguments: args },
  };
}

function toolChunks(events: ChatCompletionChunk[]) {
  const state = createDecodeState();
  return events
    .flatMap((event) => decodeStreamEvent(event, state))
    .filter((part) => part.type.startsWith("tool_call_"));
}

describe("OpenAI-compatible streamed tool calls", () => {
  it("keeps whole unindexed calls separate", () => {
    expect(
      toolChunks([
        chunk([call("call_paris", '{"city":"Paris"}', "get_weather")]),
        chunk([call("call_london", '{"city":"London"}', "get_weather")]),
        chunk([], "tool_calls"),
      ]),
    ).toEqual([
      {
        type: "tool_call_start_chunk",
        contentType: "tool_call",
        id: "call_paris",
        name: "get_weather",
      },
      {
        type: "tool_call_chunk",
        contentType: "tool_call",
        id: "call_paris",
        delta: '{"city":"Paris"}',
      },
      {
        type: "tool_call_end_chunk",
        contentType: "tool_call",
        id: "call_paris",
      },
      {
        type: "tool_call_start_chunk",
        contentType: "tool_call",
        id: "call_london",
        name: "get_weather",
      },
      {
        type: "tool_call_chunk",
        contentType: "tool_call",
        id: "call_london",
        delta: '{"city":"London"}',
      },
      {
        type: "tool_call_end_chunk",
        contentType: "tool_call",
        id: "call_london",
      },
    ]);
  });

  it("continues unindexed fragments with the same or missing id", () => {
    expect(
      toolChunks([
        chunk([call("call_paris", '{"city":', "get_weather")]),
        chunk([call("call_paris", '"Paris"}')]),
        chunk([call("call_london", '{"city":', "get_weather")]),
        chunk([call(undefined, '"London"}')]),
        chunk([], "tool_calls"),
      ]).filter((part) => part.type === "tool_call_chunk"),
    ).toEqual([
      {
        type: "tool_call_chunk",
        contentType: "tool_call",
        id: "call_paris",
        delta: '{"city":',
      },
      {
        type: "tool_call_chunk",
        contentType: "tool_call",
        id: "call_paris",
        delta: '"Paris"}',
      },
      {
        type: "tool_call_chunk",
        contentType: "tool_call",
        id: "call_london",
        delta: '{"city":',
      },
      {
        type: "tool_call_chunk",
        contentType: "tool_call",
        id: "call_london",
        delta: '"London"}',
      },
    ]);
  });

  it("keeps explicit indexes authoritative", () => {
    expect(
      toolChunks([
        chunk([call("call_a", "{}", "get_weather", 0)]),
        chunk([call("call_b", "{}", "get_weather", 1)]),
        chunk([], "tool_calls"),
      ]).filter((part) => part.type === "tool_call_start_chunk"),
    ).toEqual([
      {
        type: "tool_call_start_chunk",
        contentType: "tool_call",
        id: "call_a",
        name: "get_weather",
      },
      {
        type: "tool_call_start_chunk",
        contentType: "tool_call",
        id: "call_b",
        name: "get_weather",
      },
    ]);
  });
});
