import { describe, expect, it, vi } from "vitest";

import type { ToolCall } from "@/llm/content/tool-call";
import type { UserMessage } from "@/llm/messages";
import type { StreamResponseChunk } from "@/llm/responses/chunks";
import type { ToolParameterSchema } from "@/llm/tools/tool-schema";

import {
  FORMAT_TOOL_NAME,
  defineFormat,
  defineOutputParser,
  resolveFormat,
} from "@/llm/formatting";
import { FinishReason } from "@/llm/responses/finish-reason";
import { StreamResponse } from "@/llm/responses/stream-response";
import { defineTool, Toolkit } from "@/llm/tools";

/**
 * Helper to create async iterator from array
 */
// eslint-disable-next-line @typescript-eslint/require-await
async function* arrayToAsyncIterator<T>(
  items: T[],
): AsyncGenerator<T, void, undefined> {
  for (const item of items) {
    yield item;
  }
}

/**
 * Helper to create a minimal StreamResponse for testing
 */
function createTestStreamResponse(
  chunks: StreamResponseChunk[],
): StreamResponse {
  const iterator = arrayToAsyncIterator(chunks);
  return new StreamResponse({
    providerId: "anthropic",
    modelId: "anthropic/claude-sonnet-4-20250514",
    providerModelName: "claude-sonnet-4-20250514",
    params: {},
    inputMessages: [],
    chunkIterator: iterator,
  });
}

describe("StreamResponse", () => {
  describe("wrapChunkIterator", () => {
    it("wraps the chunk iterator with a custom wrapper", async () => {
      const chunks: StreamResponseChunk[] = [
        { type: "text_start_chunk", contentType: "text" },
        { type: "text_chunk", contentType: "text", delta: "hello" },
        { type: "text_end_chunk", contentType: "text" },
      ];

      const response = createTestStreamResponse(chunks);

      // Wrap with a pass-through wrapper that tracks calls
      const wrappedChunks: StreamResponseChunk[] = [];
      response.wrapChunkIterator((iterator) => {
        return (async function* () {
          let result = await iterator.next();
          while (!result.done) {
            wrappedChunks.push(result.value);
            yield result.value;
            result = await iterator.next();
          }
        })();
      });

      // Consume the stream
      await response.consume();

      // Verify the wrapper was called
      expect(wrappedChunks).toHaveLength(3);
      expect(wrappedChunks[0]?.type).toBe("text_start_chunk");
    });

    it("allows error wrapping during iteration", async () => {
      const chunks: StreamResponseChunk[] = [
        { type: "text_start_chunk", contentType: "text" },
        { type: "text_chunk", contentType: "text", delta: "hello" },
      ];

      const response = createTestStreamResponse(chunks);

      // Wrap with an error-throwing wrapper
      response.wrapChunkIterator((iterator) => {
        return (async function* () {
          let result = await iterator.next();
          while (!result.done) {
            if (result.value.type === "text_chunk") {
              throw new Error("Simulated streaming error");
            }
            yield result.value;
            result = await iterator.next();
          }
        })();
      });

      // Consuming should throw
      await expect(response.consume()).rejects.toThrow(
        "Simulated streaming error",
      );
    });
  });

  describe("textStream", () => {
    it("streams only text deltas", async () => {
      const chunks: StreamResponseChunk[] = [
        { type: "text_start_chunk", contentType: "text" },
        { type: "text_chunk", contentType: "text", delta: "hello " },
        { type: "text_chunk", contentType: "text", delta: "world" },
        { type: "text_end_chunk", contentType: "text" },
      ];

      const response = createTestStreamResponse(chunks);

      const texts: string[] = [];
      for await (const text of response.textStream()) {
        texts.push(text);
      }

      expect(texts).toEqual(["hello ", "world"]);
    });
  });

  describe("thoughtStream", () => {
    it("streams only thought deltas", async () => {
      const chunks: StreamResponseChunk[] = [
        { type: "thought_start_chunk", contentType: "thought" },
        { type: "thought_chunk", contentType: "thought", delta: "thinking " },
        { type: "thought_chunk", contentType: "thought", delta: "deeply" },
        { type: "thought_end_chunk", contentType: "thought" },
      ];

      const response = createTestStreamResponse(chunks);

      const thoughts: string[] = [];
      for await (const thought of response.thoughtStream()) {
        thoughts.push(thought);
      }

      expect(thoughts).toEqual(["thinking ", "deeply"]);
    });
  });

  describe("consume", () => {
    it("consumes the entire stream", async () => {
      const chunks: StreamResponseChunk[] = [
        { type: "text_start_chunk", contentType: "text" },
        { type: "text_chunk", contentType: "text", delta: "hello" },
        { type: "text_end_chunk", contentType: "text" },
      ];

      const response = createTestStreamResponse(chunks);

      expect(response.consumed).toBe(false);
      await response.consume();
      expect(response.consumed).toBe(true);
    });
  });

  describe("chunkStream replay", () => {
    it("replays cached chunks on second iteration", async () => {
      const chunks: StreamResponseChunk[] = [
        { type: "text_start_chunk", contentType: "text" },
        { type: "text_chunk", contentType: "text", delta: "hello" },
        { type: "text_end_chunk", contentType: "text" },
      ];

      const response = createTestStreamResponse(chunks);

      // First iteration - consumes from iterator
      const firstPass: string[] = [];
      for await (const chunk of response.chunkStream()) {
        if (chunk.type === "text_chunk") {
          firstPass.push(chunk.delta);
        }
      }
      expect(firstPass).toEqual(["hello"]);
      expect(response.consumed).toBe(true);

      // Second iteration - replays from cache
      const secondPass: string[] = [];
      for await (const chunk of response.chunkStream()) {
        if (chunk.type === "text_chunk") {
          secondPass.push(chunk.delta);
        }
      }
      expect(secondPass).toEqual(["hello"]);
    });

    it("returns early when stream is already consumed", async () => {
      const chunks: StreamResponseChunk[] = [
        { type: "text_start_chunk", contentType: "text" },
        { type: "text_chunk", contentType: "text", delta: "hello" },
        { type: "text_end_chunk", contentType: "text" },
      ];

      const response = createTestStreamResponse(chunks);

      // Consume the stream
      await response.consume();
      expect(response.consumed).toBe(true);

      // Calling chunkStream again should replay cached chunks and return
      const replayedChunks: string[] = [];
      for await (const chunk of response.chunkStream()) {
        if (chunk.type === "text_chunk") {
          replayedChunks.push(chunk.delta);
        }
      }
      expect(replayedChunks).toEqual(["hello"]);
    });
  });

  describe("metadata chunk processing", () => {
    it("processes raw_stream_event_chunk", async () => {
      const rawEvent = { type: "some_event", data: "test" };
      const chunks: StreamResponseChunk[] = [
        { type: "raw_stream_event_chunk", rawStreamEvent: rawEvent },
        { type: "text_start_chunk", contentType: "text" },
        { type: "text_chunk", contentType: "text", delta: "hello" },
        { type: "text_end_chunk", contentType: "text" },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.raw).toContainEqual(rawEvent);
    });

    it("processes raw_message_chunk", async () => {
      const rawMessage = { id: "msg_123", model: "test-model" };
      const chunks: StreamResponseChunk[] = [
        { type: "raw_message_chunk", rawMessage },
        { type: "text_start_chunk", contentType: "text" },
        { type: "text_end_chunk", contentType: "text" },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.assistantMessage.rawMessage).toEqual(rawMessage);
    });

    it("processes finish_reason_chunk", async () => {
      const chunks: StreamResponseChunk[] = [
        { type: "text_start_chunk", contentType: "text" },
        { type: "text_chunk", contentType: "text", delta: "partial" },
        { type: "text_end_chunk", contentType: "text" },
        { type: "finish_reason_chunk", finishReason: FinishReason.MAX_TOKENS },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.finishReason).toBe(FinishReason.MAX_TOKENS);
    });

    it("accumulates usage_delta_chunk", async () => {
      const chunks: StreamResponseChunk[] = [
        {
          type: "usage_delta_chunk",
          inputTokens: 10,
          outputTokens: 0,
          cacheReadTokens: 5,
          cacheWriteTokens: 0,
          reasoningTokens: 0,
        },
        { type: "text_start_chunk", contentType: "text" },
        { type: "text_chunk", contentType: "text", delta: "hello" },
        { type: "text_end_chunk", contentType: "text" },
        {
          type: "usage_delta_chunk",
          inputTokens: 0,
          outputTokens: 20,
          cacheReadTokens: 0,
          cacheWriteTokens: 3,
          reasoningTokens: 15,
        },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.usage).not.toBeNull();
      expect(response.usage?.inputTokens).toBe(10);
      expect(response.usage?.outputTokens).toBe(20);
      expect(response.usage?.cacheReadTokens).toBe(5);
      expect(response.usage?.cacheWriteTokens).toBe(3);
      expect(response.usage?.reasoningTokens).toBe(15);
    });
  });

  describe("property getters", () => {
    it("returns toolCalls via getter (empty when no tool calls)", async () => {
      const chunks: StreamResponseChunk[] = [
        { type: "text_start_chunk", contentType: "text" },
        { type: "text_chunk", contentType: "text", delta: "hello" },
        { type: "text_end_chunk", contentType: "text" },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.toolCalls).toEqual([]);
    });

    it("returns thoughts via getter", async () => {
      const chunks: StreamResponseChunk[] = [
        { type: "thought_start_chunk", contentType: "thought" },
        { type: "thought_chunk", contentType: "thought", delta: "thinking " },
        { type: "thought_chunk", contentType: "thought", delta: "about it" },
        { type: "thought_end_chunk", contentType: "thought" },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.thoughts).toHaveLength(1);
      expect(response.thoughts[0]?.thought).toBe("thinking about it");
    });

    it("returns chunks via getter", async () => {
      const chunks: StreamResponseChunk[] = [
        { type: "text_start_chunk", contentType: "text" },
        { type: "text_chunk", contentType: "text", delta: "hi" },
        { type: "text_end_chunk", contentType: "text" },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.chunks).toHaveLength(3);
      expect(response.chunks[0]?.type).toBe("text_start_chunk");
      expect(response.chunks[1]?.type).toBe("text_chunk");
      expect(response.chunks[2]?.type).toBe("text_end_chunk");
    });

    it("returns texts via getter", async () => {
      const chunks: StreamResponseChunk[] = [
        { type: "text_start_chunk", contentType: "text" },
        { type: "text_chunk", contentType: "text", delta: "hello " },
        { type: "text_chunk", contentType: "text", delta: "world" },
        { type: "text_end_chunk", contentType: "text" },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.texts).toHaveLength(1);
      expect(response.texts[0]?.text).toBe("hello world");
    });

    it("thought() joins with default separator", async () => {
      const chunks: StreamResponseChunk[] = [
        { type: "thought_start_chunk", contentType: "thought" },
        { type: "thought_chunk", contentType: "thought", delta: "first" },
        { type: "thought_end_chunk", contentType: "thought" },
        { type: "thought_start_chunk", contentType: "thought" },
        { type: "thought_chunk", contentType: "thought", delta: "second" },
        { type: "thought_end_chunk", contentType: "thought" },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.thought()).toBe("first\nsecond");
    });

    it("thought() joins with custom separator", async () => {
      const chunks: StreamResponseChunk[] = [
        { type: "thought_start_chunk", contentType: "thought" },
        { type: "thought_chunk", contentType: "thought", delta: "first" },
        { type: "thought_end_chunk", contentType: "thought" },
        { type: "thought_start_chunk", contentType: "thought" },
        { type: "thought_chunk", contentType: "thought", delta: "second" },
        { type: "thought_end_chunk", contentType: "thought" },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.thought(" | ")).toBe("first | second");
    });

    it("builds messages array with input and assistant", async () => {
      const inputMessage: UserMessage = {
        role: "user",
        content: [{ type: "text", text: "hello" }],
        name: null,
      };

      const textChunks: StreamResponseChunk[] = [
        { type: "text_start_chunk", contentType: "text" },
        { type: "text_chunk", contentType: "text", delta: "hi there" },
        { type: "text_end_chunk", contentType: "text" },
      ];

      const iterator = arrayToAsyncIterator(textChunks);
      const response = new StreamResponse({
        providerId: "anthropic",
        modelId: "anthropic/claude-sonnet-4-20250514",
        providerModelName: "claude-sonnet-4-20250514",
        params: {},
        inputMessages: [inputMessage],
        chunkIterator: iterator,
      });

      await response.consume();

      expect(response.messages).toHaveLength(2);
      expect(response.messages[0]?.role).toBe("user");
      expect(response.messages[1]?.role).toBe("assistant");
    });

    it("builds assistantMessage with correct properties", async () => {
      const rawMessage = { id: "msg_123" };
      const chunks: StreamResponseChunk[] = [
        { type: "raw_message_chunk", rawMessage },
        { type: "text_start_chunk", contentType: "text" },
        { type: "text_chunk", contentType: "text", delta: "response" },
        { type: "text_end_chunk", contentType: "text" },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      const msg = response.assistantMessage;
      expect(msg.role).toBe("assistant");
      expect(msg.content).toHaveLength(1);
      expect(msg.content[0]?.type).toBe("text");
      expect(msg.providerId).toBe("anthropic");
      expect(msg.modelId).toBe("anthropic/claude-sonnet-4-20250514");
      expect(msg.providerModelName).toBe("claude-sonnet-4-20250514");
      expect(msg.rawMessage).toEqual(rawMessage);
    });
  });

  describe("content accumulation", () => {
    it("accumulates text content correctly", async () => {
      const chunks: StreamResponseChunk[] = [
        { type: "text_start_chunk", contentType: "text" },
        { type: "text_chunk", contentType: "text", delta: "Hello " },
        { type: "text_chunk", contentType: "text", delta: "World!" },
        { type: "text_end_chunk", contentType: "text" },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.content).toHaveLength(1);
      expect(response.content[0]?.type).toBe("text");
      expect(response.text()).toBe("Hello World!");
    });

    it("accumulates thought content correctly", async () => {
      const chunks: StreamResponseChunk[] = [
        { type: "thought_start_chunk", contentType: "thought" },
        { type: "thought_chunk", contentType: "thought", delta: "Let me " },
        { type: "thought_chunk", contentType: "thought", delta: "think..." },
        { type: "thought_end_chunk", contentType: "thought" },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.content).toHaveLength(1);
      expect(response.content[0]?.type).toBe("thought");
      expect(response.thought()).toBe("Let me think...");
    });

    it("accumulates mixed content correctly", async () => {
      const chunks: StreamResponseChunk[] = [
        { type: "thought_start_chunk", contentType: "thought" },
        { type: "thought_chunk", contentType: "thought", delta: "thinking" },
        { type: "thought_end_chunk", contentType: "thought" },
        { type: "text_start_chunk", contentType: "text" },
        { type: "text_chunk", contentType: "text", delta: "answer" },
        { type: "text_end_chunk", contentType: "text" },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      expect(response.content).toHaveLength(2);
      expect(response.content[0]?.type).toBe("thought");
      expect(response.content[1]?.type).toBe("text");
      expect(response.thought()).toBe("thinking");
      expect(response.text()).toBe("answer");
    });
  });

  describe("toolkit and tools", () => {
    // Helper to create a mock schema
    function createMockSchema(
      properties: Record<string, { type: string }>,
      required: string[] = [],
    ): ToolParameterSchema {
      return {
        type: "object",
        properties,
        required,
        additionalProperties: false,
      };
    }

    it("accepts Toolkit directly", () => {
      const schema = createMockSchema({ value: { type: "string" } }, ["value"]);
      const tool = defineTool<{ value: string }>({
        name: "test_tool",
        description: "Test tool",
        tool: ({ value }) => `result: ${value}`,
        __schema: schema,
      });
      const toolkit = new Toolkit([tool]);

      const chunks: StreamResponseChunk[] = [
        { type: "text_start_chunk", contentType: "text" },
        { type: "text_chunk", contentType: "text", delta: "Hello!" },
        { type: "text_end_chunk", contentType: "text" },
      ];

      const iterator = arrayToAsyncIterator(chunks);
      const response = new StreamResponse({
        providerId: "anthropic",
        modelId: "anthropic/claude-sonnet-4-20250514",
        providerModelName: "claude-sonnet-4-20250514",
        params: {},
        inputMessages: [],
        chunkIterator: iterator,
        tools: toolkit,
      });

      // The toolkit should be the same instance
      expect(response.toolkit).toBe(toolkit);
    });

    it("executeTools executes tool calls after stream is consumed", async () => {
      const toolFn = vi.fn(
        ({ query }: { query: string }) => `searched: ${query}`,
      );
      const searchTool = defineTool<{ query: string }>({
        name: "search",
        description: "Search",
        tool: toolFn,
        __schema: createMockSchema({ query: { type: "string" } }, ["query"]),
      });

      const toolCall: ToolCall = {
        type: "tool_call",
        id: "call-1",
        name: "search",
        args: JSON.stringify({ query: "test" }),
      };

      const chunks: StreamResponseChunk[] = [
        { type: "text_start_chunk", contentType: "text" },
        { type: "text_chunk", contentType: "text", delta: "Let me search." },
        { type: "text_end_chunk", contentType: "text" },
        {
          type: "tool_call_start_chunk",
          contentType: "tool_call",
          id: toolCall.id,
          name: toolCall.name,
        },
        {
          type: "tool_call_chunk",
          contentType: "tool_call",
          id: toolCall.id,
          delta: toolCall.args,
        },
        {
          type: "tool_call_end_chunk",
          contentType: "tool_call",
          id: toolCall.id,
        },
      ];

      const iterator = arrayToAsyncIterator(chunks);
      const response = new StreamResponse({
        providerId: "anthropic",
        modelId: "anthropic/claude-sonnet-4-20250514",
        providerModelName: "claude-sonnet-4-20250514",
        params: {},
        inputMessages: [],
        chunkIterator: iterator,
        tools: [searchTool],
      });

      // Consume stream first
      await response.consume();

      // Then execute tools
      const outputs = await response.executeTools();

      expect(outputs).toHaveLength(1);
      expect(outputs[0]?.result).toBe("searched: test");
      expect(outputs[0]?.error).toBeNull();
      expect(toolFn).toHaveBeenCalledWith({ query: "test" });
    });

    it("executeTools handles multiple tool calls", async () => {
      const addFn = vi.fn(({ a, b }: { a: number; b: number }) => a + b);
      const multiplyFn = vi.fn(({ a, b }: { a: number; b: number }) => a * b);

      const addTool = defineTool<{ a: number; b: number }>({
        name: "add",
        description: "Add",
        tool: addFn,
        __schema: createMockSchema(
          { a: { type: "number" }, b: { type: "number" } },
          ["a", "b"],
        ),
      });

      const multiplyTool = defineTool<{ a: number; b: number }>({
        name: "multiply",
        description: "Multiply",
        tool: multiplyFn,
        __schema: createMockSchema(
          { a: { type: "number" }, b: { type: "number" } },
          ["a", "b"],
        ),
      });

      const chunks: StreamResponseChunk[] = [
        {
          type: "tool_call_start_chunk",
          contentType: "tool_call",
          id: "call-1",
          name: "add",
        },
        {
          type: "tool_call_chunk",
          contentType: "tool_call",
          id: "call-1",
          delta: JSON.stringify({ a: 5, b: 3 }),
        },
        { type: "tool_call_end_chunk", contentType: "tool_call", id: "call-1" },
        {
          type: "tool_call_start_chunk",
          contentType: "tool_call",
          id: "call-2",
          name: "multiply",
        },
        {
          type: "tool_call_chunk",
          contentType: "tool_call",
          id: "call-2",
          delta: JSON.stringify({ a: 4, b: 6 }),
        },
        { type: "tool_call_end_chunk", contentType: "tool_call", id: "call-2" },
      ];

      const iterator = arrayToAsyncIterator(chunks);
      const response = new StreamResponse({
        providerId: "anthropic",
        modelId: "anthropic/claude-sonnet-4-20250514",
        providerModelName: "claude-sonnet-4-20250514",
        params: {},
        inputMessages: [],
        chunkIterator: iterator,
        tools: [addTool, multiplyTool],
      });

      await response.consume();
      const outputs = await response.executeTools();

      expect(outputs).toHaveLength(2);
      expect(outputs[0]?.result).toBe(8); // 5 + 3
      expect(outputs[1]?.result).toBe(24); // 4 * 6
    });

    it("defaults args to {} when no tool_call_chunk provided", async () => {
      const noArgsFn = vi.fn(() => "no args result");
      const noArgsTool = defineTool({
        name: "no_args",
        description: "Tool with no args",
        tool: noArgsFn,
        __schema: {
          type: "object",
          properties: {},
          required: [],
          additionalProperties: false,
        },
      });

      const chunks: StreamResponseChunk[] = [
        {
          type: "tool_call_start_chunk",
          contentType: "tool_call",
          id: "call-1",
          name: "no_args",
        },
        // No tool_call_chunk - args should default to {}
        { type: "tool_call_end_chunk", contentType: "tool_call", id: "call-1" },
      ];

      const iterator = arrayToAsyncIterator(chunks);
      const response = new StreamResponse({
        providerId: "anthropic",
        modelId: "anthropic/claude-sonnet-4-20250514",
        providerModelName: "claude-sonnet-4-20250514",
        params: {},
        inputMessages: [],
        chunkIterator: iterator,
        tools: [noArgsTool],
      });

      await response.consume();
      expect(response.toolCalls[0]?.args).toBe("{}");

      const outputs = await response.executeTools();
      expect(outputs).toHaveLength(1);
      expect(outputs[0]?.result).toBe("no args result");
    });

    it("throws error for tool_call_end_chunk with unknown id", async () => {
      const chunks: StreamResponseChunk[] = [
        {
          type: "tool_call_end_chunk",
          contentType: "tool_call",
          id: "unknown-id",
        },
      ];

      const iterator = arrayToAsyncIterator(chunks);
      const response = new StreamResponse({
        providerId: "anthropic",
        modelId: "anthropic/claude-sonnet-4-20250514",
        providerModelName: "claude-sonnet-4-20250514",
        params: {},
        inputMessages: [],
        chunkIterator: iterator,
        tools: [],
      });

      await expect(response.consume()).rejects.toThrow(
        "Received tool_call_end_chunk for unknown tool call ID: unknown-id",
      );
    });

    it("throws error for tool_call_chunk with unknown id", async () => {
      const chunks: StreamResponseChunk[] = [
        {
          type: "tool_call_chunk",
          contentType: "tool_call",
          id: "unknown-id",
          delta: "{}",
        },
      ];

      const iterator = arrayToAsyncIterator(chunks);
      const response = new StreamResponse({
        providerId: "anthropic",
        modelId: "anthropic/claude-sonnet-4-20250514",
        providerModelName: "claude-sonnet-4-20250514",
        params: {},
        inputMessages: [],
        chunkIterator: iterator,
        tools: [],
      });

      await expect(response.consume()).rejects.toThrow(
        "Received tool_call_chunk for unknown tool call ID: unknown-id",
      );
    });

    it("throws error for duplicate tool_call_start_chunk id", async () => {
      const chunks: StreamResponseChunk[] = [
        {
          type: "tool_call_start_chunk",
          contentType: "tool_call",
          id: "call-1",
          name: "test",
        },
        {
          type: "tool_call_start_chunk",
          contentType: "tool_call",
          id: "call-1",
          name: "test",
        },
      ];

      const iterator = arrayToAsyncIterator(chunks);
      const response = new StreamResponse({
        providerId: "anthropic",
        modelId: "anthropic/claude-sonnet-4-20250514",
        providerModelName: "claude-sonnet-4-20250514",
        params: {},
        inputMessages: [],
        chunkIterator: iterator,
        tools: [],
      });

      await expect(response.consume()).rejects.toThrow(
        "Received tool_call_start_chunk with duplicate id: call-1",
      );
    });
  });

  describe("structuredStream", () => {
    it("throws error when format is not set", async () => {
      const chunks: StreamResponseChunk[] = [
        { type: "text_start_chunk", contentType: "text" },
        { type: "text_chunk", contentType: "text", delta: "hello" },
        { type: "text_end_chunk", contentType: "text" },
      ];

      const response = createTestStreamResponse(chunks);

      await expect(async () => {
        for await (const _ of response.structuredStream()) {
          // Should throw before yielding
        }
      }).rejects.toThrow("structuredStream() requires format parameter");
    });

    it("throws error when format uses OutputParser", async () => {
      const outputParser = defineOutputParser({
        formattingInstructions: "Return XML",
        parser: () => ({ value: "test" }),
      });

      // Resolve OutputParser to a Format (this is what providers do internally)
      const format = resolveFormat(outputParser, "tool");

      const chunks: StreamResponseChunk[] = [
        { type: "text_start_chunk", contentType: "text" },
        { type: "text_chunk", contentType: "text", delta: "hello" },
        { type: "text_end_chunk", contentType: "text" },
      ];

      const iterator = arrayToAsyncIterator(chunks);
      const response = new StreamResponse({
        providerId: "anthropic",
        modelId: "anthropic/claude-sonnet-4-20250514",
        providerModelName: "claude-sonnet-4-20250514",
        params: {},
        inputMessages: [],
        chunkIterator: iterator,
        format,
      });

      await expect(async () => {
        for await (const _ of response.structuredStream()) {
          // Should throw before yielding
        }
      }).rejects.toThrow(
        "structuredStream() is not supported for OutputParser",
      );
    });

    it("yields partial parsed objects as stream progresses", async () => {
      interface Book {
        title: string;
        author: string;
      }

      const bookSchema: ToolParameterSchema = {
        type: "object",
        properties: {
          title: { type: "string" },
          author: { type: "string" },
        },
        required: ["title", "author"],
        additionalProperties: false,
      };

      const bookFormat = defineFormat<Book>({
        mode: "tool",
        __schema: bookSchema,
      });

      const chunks: StreamResponseChunk[] = [
        { type: "text_start_chunk", contentType: "text" },
        { type: "text_chunk", contentType: "text", delta: '{"title": "Dune"' },
        {
          type: "text_chunk",
          contentType: "text",
          delta: ', "author": "Frank Herbert"}',
        },
        { type: "text_end_chunk", contentType: "text" },
      ];

      const iterator = arrayToAsyncIterator(chunks);
      const response = new StreamResponse({
        providerId: "anthropic",
        modelId: "anthropic/claude-sonnet-4-20250514",
        providerModelName: "claude-sonnet-4-20250514",
        params: {},
        inputMessages: [],
        chunkIterator: iterator,
        format: bookFormat,
      });

      const partials: unknown[] = [];
      for await (const partial of response.structuredStream()) {
        partials.push(partial);
      }

      // Should have yielded at least one partial
      expect(partials.length).toBeGreaterThan(0);
      // Final partial should have both fields
      const finalPartial = partials[partials.length - 1] as Book;
      expect(finalPartial.title).toBe("Dune");
      expect(finalPartial.author).toBe("Frank Herbert");
    });

    it("handles chunks that do not produce valid partial JSON", async () => {
      interface Data {
        value: number;
      }

      const dataSchema: ToolParameterSchema = {
        type: "object",
        properties: {
          value: { type: "number" },
        },
        required: ["value"],
        additionalProperties: false,
      };

      const dataFormat = defineFormat<Data>({
        mode: "tool",
        __schema: dataSchema,
      });

      const chunks: StreamResponseChunk[] = [
        { type: "text_start_chunk", contentType: "text" },
        // Invalid JSON that can't be parsed
        { type: "text_chunk", contentType: "text", delta: "not json at all" },
        { type: "text_end_chunk", contentType: "text" },
      ];

      const iterator = arrayToAsyncIterator(chunks);
      const response = new StreamResponse({
        providerId: "anthropic",
        modelId: "anthropic/claude-sonnet-4-20250514",
        providerModelName: "claude-sonnet-4-20250514",
        params: {},
        inputMessages: [],
        chunkIterator: iterator,
        format: dataFormat,
      });

      const partials: unknown[] = [];
      for await (const partial of response.structuredStream()) {
        partials.push(partial);
      }

      // Should yield nothing since JSON couldn't be parsed
      expect(partials.length).toBe(0);
    });
  });

  describe("FORMAT_TOOL transformation", () => {
    it("transforms FORMAT_TOOL tool_call chunks to text chunks", async () => {
      const chunks: StreamResponseChunk[] = [
        {
          type: "tool_call_start_chunk",
          contentType: "tool_call",
          id: "call-format",
          name: FORMAT_TOOL_NAME,
        },
        {
          type: "tool_call_chunk",
          contentType: "tool_call",
          id: "call-format",
          delta: '{"title": "Test Book",',
        },
        {
          type: "tool_call_chunk",
          contentType: "tool_call",
          id: "call-format",
          delta: ' "author": "Test Author"}',
        },
        {
          type: "tool_call_end_chunk",
          contentType: "tool_call",
          id: "call-format",
        },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      // The FORMAT_TOOL chunks should be transformed to text
      // so text() should return the JSON content
      expect(response.text()).toBe(
        '{"title": "Test Book", "author": "Test Author"}',
      );
      // And no tool calls should be accumulated
      expect(response.toolCalls).toHaveLength(0);
    });

    it("handles FORMAT_TOOL mixed with regular text", async () => {
      const chunks: StreamResponseChunk[] = [
        // Regular text before
        { type: "text_start_chunk", contentType: "text" },
        {
          type: "text_chunk",
          contentType: "text",
          delta: "Here is your data: ",
        },
        { type: "text_end_chunk", contentType: "text" },
        // FORMAT_TOOL
        {
          type: "tool_call_start_chunk",
          contentType: "tool_call",
          id: "call-format",
          name: FORMAT_TOOL_NAME,
        },
        {
          type: "tool_call_chunk",
          contentType: "tool_call",
          id: "call-format",
          delta: '{"value": 42}',
        },
        {
          type: "tool_call_end_chunk",
          contentType: "tool_call",
          id: "call-format",
        },
      ];

      const response = createTestStreamResponse(chunks);
      await response.consume();

      // Both text segments should be captured
      expect(response.texts).toHaveLength(2);
      expect(response.texts[0]?.text).toBe("Here is your data: ");
      expect(response.texts[1]?.text).toBe('{"value": 42}');
    });
  });
});
