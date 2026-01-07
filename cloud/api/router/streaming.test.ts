import { describe, it, expect, vi, beforeEach } from "vitest";
import { Effect, Stream, Chunk } from "effect";
import { parseStreamingResponse } from "@/api/router/streaming";

describe("Streaming", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  describe("parseStreamingResponse", () => {
    it("handles empty response body", async () => {
      const response = new Response(null, {
        status: 200,
        headers: { "content-type": "text/event-stream" },
      });

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", "openai"),
      );

      expect(result.response).toBeDefined();
      expect(result.usageStream).toBeDefined();

      // Collect from empty stream
      const usageChunk = await Effect.runPromise(
        Stream.runCollect(result.usageStream),
      );
      const usageData = Chunk.toReadonlyArray(usageChunk);
      expect(usageData.length).toBe(0);
    });

    it("parses SSE format and extracts OpenAI Completions usage", async () => {
      const sseData = `data: {"id":"1","choices":[{"text":"Hello"}]}\n\ndata: {"id":"2","usage":{"prompt_tokens":10,"completion_tokens":5}}\n\ndata: [DONE]\n\n`;
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode(sseData));
          controller.close();
        },
      });

      const response = new Response(stream, {
        status: 200,
        headers: { "content-type": "text/event-stream" },
      });

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", "openai"),
      );

      // Read the stream to trigger parsing
      await result.response.text();

      // Collect usage from stream
      const usageChunk = await Effect.runPromise(
        Stream.runCollect(result.usageStream),
      );
      const usageData = Chunk.toReadonlyArray(usageChunk);

      expect(usageData.length).toBe(1);
      const usage = usageData[0];
      expect(usage.inputTokens).toBe(10);
      expect(usage.outputTokens).toBe(5);
    });

    it("parses SSE format and extracts OpenAI Responses API usage", async () => {
      const sseData = `data: {"type":"response.created"}\n\ndata: {"type":"response.completed","response":{"usage":{"input_tokens":100,"output_tokens":50}}}\n\n`;
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode(sseData));
          controller.close();
        },
      });

      const response = new Response(stream, {
        status: 200,
        headers: { "content-type": "text/event-stream" },
      });

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", "openai"),
      );

      // Read the stream
      await result.response.text();

      // Collect usage from stream
      const usageChunk = await Effect.runPromise(
        Stream.runCollect(result.usageStream),
      );
      const usageData = Chunk.toReadonlyArray(usageChunk);

      expect(usageData.length).toBe(1);
      const usage = usageData[0];
      expect(usage.inputTokens).toBe(100);
      expect(usage.outputTokens).toBe(50);
    });

    it("parses SSE format and extracts Anthropic usage", async () => {
      const sseData = `data: {"type":"content_block_start"}\n\ndata: {"type":"message_delta","usage":{"output_tokens":5}}\n\ndata: {"type":"message_stop","usage":{"input_tokens":100,"output_tokens":50}}\n\n`;
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode(sseData));
          controller.close();
        },
      });

      const response = new Response(stream, {
        status: 200,
        headers: { "content-type": "text/event-stream" },
      });

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", "anthropic"),
      );

      await result.response.text();

      // Collect usage from stream - Anthropic may emit multiple usage chunks
      const usageChunk = await Effect.runPromise(
        Stream.runCollect(result.usageStream),
      );
      const usageData = Chunk.toReadonlyArray(usageChunk);

      expect(usageData.length).toBeGreaterThan(0);
      // Get the last usage chunk (message_stop)
      const finalUsage = usageData[usageData.length - 1];
      expect(finalUsage.inputTokens).toBe(100);
      expect(finalUsage.outputTokens).toBe(50);
    });

    it("parses SSE format and extracts Google usage", async () => {
      const sseData = `data: {"candidates":[]}\n\ndata: {"usageMetadata":{"promptTokenCount":100,"candidatesTokenCount":50}}\n\n`;
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode(sseData));
          controller.close();
        },
      });

      const response = new Response(stream, {
        status: 200,
        headers: { "content-type": "text/event-stream" },
      });

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", "google"),
      );

      await result.response.text();

      // Collect usage from stream
      const usageChunk = await Effect.runPromise(
        Stream.runCollect(result.usageStream),
      );
      const usageData = Chunk.toReadonlyArray(usageChunk);

      expect(usageData.length).toBe(1);
      const usage = usageData[0];
      expect(usage.inputTokens).toBe(100);
      expect(usage.outputTokens).toBe(50);
    });

    it("parses NDJSON format", async () => {
      const ndjsonData = `{"id":"1","text":"Hello"}\n{"id":"2","usage":{"prompt_tokens":10,"completion_tokens":5}}\n`;
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode(ndjsonData));
          controller.close();
        },
      });

      const response = new Response(stream, {
        status: 200,
        headers: { "content-type": "application/x-ndjson" },
      });

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "ndjson", "openai"),
      );

      await result.response.text();

      // Collect usage from stream
      const usageChunk = await Effect.runPromise(
        Stream.runCollect(result.usageStream),
      );
      const usageData = Chunk.toReadonlyArray(usageChunk);

      expect(usageData.length).toBe(1);
      const usage = usageData[0];
      expect(usage.inputTokens).toBe(10);
      expect(usage.outputTokens).toBe(5);
    });

    it("handles invalid JSON in SSE gracefully", async () => {
      const sseData = `data: invalid json\n\ndata: {"usage":{"prompt_tokens":10,"completion_tokens":5}}\n\n`;
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode(sseData));
          controller.close();
        },
      });

      const response = new Response(stream, {
        status: 200,
        headers: { "content-type": "text/event-stream" },
      });

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", "openai"),
      );

      await result.response.text();

      // Collect usage from stream - should still extract valid usage
      const usageChunk = await Effect.runPromise(
        Stream.runCollect(result.usageStream),
      );
      const usageData = Chunk.toReadonlyArray(usageChunk);

      expect(usageData.length).toBe(1);
      const usage = usageData[0];
      expect(usage.inputTokens).toBe(10);
      expect(usage.outputTokens).toBe(5);
    });

    it("handles invalid JSON in NDJSON gracefully", async () => {
      const ndjsonData = `invalid json\n{"usage":{"prompt_tokens":10,"completion_tokens":5}}\n`;
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode(ndjsonData));
          controller.close();
        },
      });

      const response = new Response(stream, {
        status: 200,
        headers: { "content-type": "application/x-ndjson" },
      });

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "ndjson", "openai"),
      );

      await result.response.text();

      // Collect usage from stream
      const usageChunk = await Effect.runPromise(
        Stream.runCollect(result.usageStream),
      );
      const usageData = Chunk.toReadonlyArray(usageChunk);

      expect(usageData.length).toBe(1);
      const usage = usageData[0];
      expect(usage.inputTokens).toBe(10);
      expect(usage.outputTokens).toBe(5);
    });

    it("handles SSE lines without data prefix", async () => {
      const sseData = `event: ping\n\ndata: {"usage":{"prompt_tokens":10,"completion_tokens":5}}\n\n`;
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode(sseData));
          controller.close();
        },
      });

      const response = new Response(stream, {
        status: 200,
        headers: { "content-type": "text/event-stream" },
      });

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", "openai"),
      );

      await result.response.text();

      // Collect usage from stream - should still extract valid usage from data lines
      const usageChunk = await Effect.runPromise(
        Stream.runCollect(result.usageStream),
      );
      const usageData = Chunk.toReadonlyArray(usageChunk);

      expect(usageData.length).toBe(1);
      const usage = usageData[0];
      expect(usage.inputTokens).toBe(10);
      expect(usage.outputTokens).toBe(5);
    });

    it("handles non-object chunks gracefully", async () => {
      const sseData = `data: "string value"\n\ndata: 123\n\ndata: {"usage":{"prompt_tokens":10,"completion_tokens":5}}\n\n`;
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode(sseData));
          controller.close();
        },
      });

      const response = new Response(stream, {
        status: 200,
        headers: { "content-type": "text/event-stream" },
      });

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", "openai"),
      );

      await result.response.text();

      // Collect usage from stream - should still extract usage from valid object chunk
      const usageChunk = await Effect.runPromise(
        Stream.runCollect(result.usageStream),
      );
      const usageData = Chunk.toReadonlyArray(usageChunk);

      expect(usageData.length).toBe(1);
      const usage = usageData[0];
      expect(usage.inputTokens).toBe(10);
      expect(usage.outputTokens).toBe(5);
    });

    it("handles OpenAI [DONE] sentinel value", async () => {
      const sseData = `data: {"usage":{"prompt_tokens":10,"completion_tokens":5}}\n\ndata: [DONE]\n\n`;
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode(sseData));
          controller.close();
        },
      });

      const response = new Response(stream, {
        status: 200,
        headers: { "content-type": "text/event-stream" },
      });

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", "openai"),
      );

      await result.response.text();

      // Collect usage from stream
      const usageChunk = await Effect.runPromise(
        Stream.runCollect(result.usageStream),
      );
      const usageData = Chunk.toReadonlyArray(usageChunk);

      expect(usageData.length).toBe(1);
      const usage = usageData[0];
      expect(usage.inputTokens).toBe(10);
      expect(usage.outputTokens).toBe(5);
    });

    it("processes incomplete chunks in buffer correctly", async () => {
      const sseData = `data: {"usage":{"prompt_tokens":10,"completion_tokens":5}}`;
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode(sseData));
          controller.close();
        },
      });

      const response = new Response(stream, {
        status: 200,
        headers: { "content-type": "text/event-stream" },
      });

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", "openai"),
      );

      await result.response.text();

      // Collect usage from stream - should process buffer in flush
      const usageChunk = await Effect.runPromise(
        Stream.runCollect(result.usageStream),
      );
      const usageData = Chunk.toReadonlyArray(usageChunk);

      expect(usageData.length).toBe(1);
      const usage = usageData[0];
      expect(usage.inputTokens).toBe(10);
      expect(usage.outputTokens).toBe(5);
    });

    it("collects usage data from stream", async () => {
      const sseData = `data: {"usage":{"prompt_tokens":10,"completion_tokens":5}}\n\n`;
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode(sseData));
          controller.close();
        },
      });

      const response = new Response(stream, {
        status: 200,
        headers: { "content-type": "text/event-stream" },
      });

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", "openai"),
      );

      await result.response.text();

      // Collect usage from stream
      const usageChunk = await Effect.runPromise(
        Stream.runCollect(result.usageStream),
      );
      const usageData = Chunk.toReadonlyArray(usageChunk);

      expect(usageData.length).toBe(1);
      expect(usageData[0].inputTokens).toBe(10);
      expect(usageData[0].outputTokens).toBe(5);
    });

    it("handles stream processing with multiple operations", async () => {
      const sseData = `data: {"usage":{"prompt_tokens":10,"completion_tokens":5}}\n\n`;
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode(sseData));
          controller.close();
        },
      });

      const response = new Response(stream, {
        status: 200,
        headers: { "content-type": "text/event-stream" },
      });

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", "openai"),
      );

      // Read the stream
      await result.response.text();

      // Can perform multiple operations on the usage stream
      const usageChunk = await Effect.runPromise(
        Stream.runCollect(result.usageStream),
      );
      const usageData = Chunk.toReadonlyArray(usageChunk);

      expect(usageData.length).toBe(1);
    });

    it("ignores non-usage chunks", async () => {
      const sseData = `data: {"id":"1","text":"Hello"}\n\ndata: {"choices":[]}\n\n`;
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode(sseData));
          controller.close();
        },
      });

      const response = new Response(stream, {
        status: 200,
        headers: { "content-type": "text/event-stream" },
      });

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", "openai"),
      );

      await result.response.text();

      // Collect usage from stream - should be empty
      const usageChunk = await Effect.runPromise(
        Stream.runCollect(result.usageStream),
      );
      const usageData = Chunk.toReadonlyArray(usageChunk);

      expect(usageData.length).toBe(0);
    });

    it("handles empty lines in stream", async () => {
      const sseData = `\n\ndata: {"usage":{"prompt_tokens":10,"completion_tokens":5}}\n\n\n\n`;
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode(sseData));
          controller.close();
        },
      });

      const response = new Response(stream, {
        status: 200,
        headers: { "content-type": "text/event-stream" },
      });

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", "openai"),
      );

      await result.response.text();

      // Collect usage from stream
      const usageChunk = await Effect.runPromise(
        Stream.runCollect(result.usageStream),
      );
      const usageData = Chunk.toReadonlyArray(usageChunk);

      expect(usageData.length).toBe(1);
      const usage = usageData[0];
      expect(usage.inputTokens).toBe(10);
      expect(usage.outputTokens).toBe(5);
    });

    it("handles chunked streaming", async () => {
      const sseData1 = `data: {"id":"1"}\n\n`;
      const sseData2 = `data: {"usage":{"prompt_tokens":10,"completion_tokens":5}}\n\n`;

      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode(sseData1));
          setTimeout(() => {
            controller.enqueue(new TextEncoder().encode(sseData2));
            controller.close();
          }, 10);
        },
      });

      const response = new Response(stream, {
        status: 200,
        headers: { "content-type": "text/event-stream" },
      });

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", "openai"),
      );

      await result.response.text();

      // Collect usage from stream
      const usageChunk = await Effect.runPromise(
        Stream.runCollect(result.usageStream),
      );
      const usageData = Chunk.toReadonlyArray(usageChunk);

      expect(usageData.length).toBe(1);
    });

    it("handles OpenAI Responses API without usage field", async () => {
      const sseData = `data: {"type":"response.completed","response":{"id":"resp_123"}}\n\n`;
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode(sseData));
          controller.close();
        },
      });

      const response = new Response(stream, {
        status: 200,
        headers: { "content-type": "text/event-stream" },
      });

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", "openai"),
      );

      await result.response.text();

      // Collect usage from stream - should be empty since no valid usage found
      const usageChunk = await Effect.runPromise(
        Stream.runCollect(result.usageStream),
      );
      const usageData = Chunk.toReadonlyArray(usageChunk);

      expect(usageData.length).toBe(0);
    });

    it("handles OpenAI Responses API with incomplete usage", async () => {
      const sseData = `data: {"type":"response.completed","response":{"usage":{"total_tokens":100}}}\n\n`;
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode(sseData));
          controller.close();
        },
      });

      const response = new Response(stream, {
        status: 200,
        headers: { "content-type": "text/event-stream" },
      });

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", "openai"),
      );

      await result.response.text();

      // Collect usage from stream - should be empty since input_tokens/output_tokens are missing
      const usageChunk = await Effect.runPromise(
        Stream.runCollect(result.usageStream),
      );
      const usageData = Chunk.toReadonlyArray(usageChunk);

      expect(usageData.length).toBe(0);
    });

    it("handles Google format with incomplete usageMetadata", async () => {
      const sseData = `data: {"usageMetadata":{"totalTokenCount":100}}\n\n`;
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode(sseData));
          controller.close();
        },
      });

      const response = new Response(stream, {
        status: 200,
        headers: { "content-type": "text/event-stream" },
      });

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", "openai"),
      );

      await result.response.text();

      // Collect usage from stream - should be empty since promptTokenCount/candidatesTokenCount are missing
      const usageChunk = await Effect.runPromise(
        Stream.runCollect(result.usageStream),
      );
      const usageData = Chunk.toReadonlyArray(usageChunk);

      expect(usageData.length).toBe(0);
    });

    it("processes NDJSON buffer in flush correctly", async () => {
      const ndjsonData = `{"usage":{"prompt_tokens":10,"completion_tokens":5}}`;
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode(ndjsonData));
          controller.close();
        },
      });

      const response = new Response(stream, {
        status: 200,
        headers: { "content-type": "application/x-ndjson" },
      });

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "ndjson", "openai"),
      );

      await result.response.text();

      // Collect usage from stream - should process buffer in flush for ndjson format
      const usageChunk = await Effect.runPromise(
        Stream.runCollect(result.usageStream),
      );
      const usageData = Chunk.toReadonlyArray(usageChunk);

      expect(usageData.length).toBe(1);
      expect(usageData[0].inputTokens).toBe(10);
      expect(usageData[0].outputTokens).toBe(5);
    });

    it("handles invalid JSON in flush buffer gracefully", async () => {
      const sseData = `data: invalid json without newline`;
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode(sseData));
          controller.close();
        },
      });

      const response = new Response(stream, {
        status: 200,
        headers: { "content-type": "text/event-stream" },
      });

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", "openai"),
      );

      await result.response.text();

      // Collect usage from stream - should be empty when buffer contains invalid JSON
      const usageChunk = await Effect.runPromise(
        Stream.runCollect(result.usageStream),
      );
      const usageData = Chunk.toReadonlyArray(usageChunk);

      expect(usageData.length).toBe(0);
    });

    it("handles non-usage data in flush buffer", async () => {
      const sseData = `data: {"id":"test","choices":[]}`;
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode(sseData));
          controller.close();
        },
      });

      const response = new Response(stream, {
        status: 200,
        headers: { "content-type": "text/event-stream" },
      });

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", "openai"),
      );

      await result.response.text();

      // Collect usage from stream - should be empty when buffer doesn't contain usage
      const usageChunk = await Effect.runPromise(
        Stream.runCollect(result.usageStream),
      );
      const usageData = Chunk.toReadonlyArray(usageChunk);

      expect(usageData.length).toBe(0);
    });
  });
});
