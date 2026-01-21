import { describe, it, expect, vi, beforeEach } from "vitest";
import { Effect, Layer } from "effect";
import { parseStreamingResponse } from "@/api/router/streaming";
import { ProxyError } from "@/errors";
import { MockMeteringContext } from "@/tests/api";
import { RouterMeteringQueueService } from "@/workers/routerMeteringQueue";

describe("Streaming", () => {
  // Mock queue service for all tests
  const mockQueueLayer = Layer.succeed(RouterMeteringQueueService, {
    send: () => Effect.succeed(undefined),
  });

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  describe("parseStreamingResponse", () => {
    it("handles empty response body", async () => {
      const response = new Response(null, {
        status: 200,
        headers: { "content-type": "text/event-stream" },
      });

      const meteringContext = MockMeteringContext.fromProvider(
        "openai",
        "gpt-4",
      );

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", meteringContext).pipe(
          Effect.provide(mockQueueLayer),
        ),
      );

      expect(result.responseEffect).toBeDefined();

      // Run the responseEffect to get the Response
      const finalResponse = await Effect.runPromise(
        result.responseEffect.pipe(Effect.provide(mockQueueLayer)),
      );

      expect(finalResponse).toBeInstanceOf(Response);
      expect(finalResponse.status).toBe(200);
    });

    it("passes through SSE data while extracting usage", async () => {
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

      const meteringContext = MockMeteringContext.fromProvider(
        "openai",
        "gpt-4",
      );

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", meteringContext).pipe(
          Effect.provide(mockQueueLayer),
        ),
      );

      const finalResponse = await Effect.runPromise(
        result.responseEffect.pipe(Effect.provide(mockQueueLayer)),
      );

      // Read the stream to trigger metering
      const text = await finalResponse.text();

      // Verify data passed through
      expect(text).toBe(sseData);

      // Note: Metering happens in stream finalizer with fresh DB/Payments instances,
      // so we can't assert on mocks here. Metering logic is tested separately.
    });

    it("handles NDJSON format", async () => {
      const ndjsonData = `{"id":"1","choices":[{"text":"Hello"}]}\n{"id":"2","usage":{"prompt_tokens":10,"completion_tokens":5}}\n`;
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

      const meteringContext = MockMeteringContext.fromProvider(
        "openai",
        "gpt-4",
      );

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "ndjson", meteringContext).pipe(
          Effect.provide(mockQueueLayer),
        ),
      );

      const finalResponse = await Effect.runPromise(
        result.responseEffect.pipe(Effect.provide(mockQueueLayer)),
      );

      const text = await finalResponse.text();
      expect(text).toBe(ndjsonData);
    });

    it("preserves response metadata", async () => {
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode("data: {}\n\n"));
          controller.close();
        },
      });

      const response = new Response(stream, {
        status: 201,
        headers: { "content-type": "text/event-stream" },
      });

      const meteringContext = MockMeteringContext.fromProvider(
        "openai",
        "gpt-4",
        {
          response: {
            status: 201,
            statusText: "Created",
            headers: new Headers({
              "content-type": "text/event-stream",
              "x-custom": "value",
            }),
          },
        },
      );

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", meteringContext).pipe(
          Effect.provide(mockQueueLayer),
        ),
      );

      const finalResponse = await Effect.runPromise(
        result.responseEffect.pipe(Effect.provide(mockQueueLayer)),
      );

      expect(finalResponse.status).toBe(201);
      expect(finalResponse.statusText).toBe("Created");
      expect(finalResponse.headers.get("x-custom")).toBe("value");
    });

    it("handles stream read errors", async () => {
      // Create a stream that throws an error
      const stream = new ReadableStream({
        start(controller) {
          controller.error(new Error("Stream read error"));
        },
      });

      const response = new Response(stream, {
        status: 200,
        headers: { "content-type": "text/event-stream" },
      });

      const meteringContext = MockMeteringContext.fromProvider(
        "openai",
        "gpt-4",
      );

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", meteringContext).pipe(
          Effect.provide(mockQueueLayer),
        ),
      );

      // Should fail when trying to read the stream
      await expect(
        Effect.runPromise(
          result.responseEffect.pipe(
            Effect.provide(mockQueueLayer),
            Effect.flatMap((response) =>
              Effect.tryPromise({
                try: () => response.text(),
                catch: (error) =>
                  new ProxyError({
                    message: "Failed to read stream",
                    cause: error,
                  }),
              }),
            ),
          ),
        ),
      ).rejects.toThrow();
    });

    it("handles anthropic streaming format", async () => {
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

      const meteringContext = MockMeteringContext.fromProvider(
        "anthropic",
        "claude-3-opus",
      );

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", meteringContext).pipe(
          Effect.provide(mockQueueLayer),
        ),
      );

      const finalResponse = await Effect.runPromise(
        result.responseEffect.pipe(Effect.provide(mockQueueLayer)),
      );

      const text = await finalResponse.text();
      expect(text).toBe(sseData);

      // Note: Metering happens in stream finalizer with fresh DB/Payments instances,
      // so we can't assert on mocks here. Metering logic is tested separately.
    });

    it("handles google streaming format", async () => {
      const ndjsonData = `{"candidates":[{"content":{"parts":[{"text":"Hello"}]}}]}\n{"candidates":[{"content":{"parts":[{"text":" world"}]}}],"usageMetadata":{"promptTokenCount":10,"candidatesTokenCount":5}}\n`;
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

      const meteringContext = MockMeteringContext.fromProvider(
        "google",
        "gemini-pro",
      );

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "ndjson", meteringContext).pipe(
          Effect.provide(mockQueueLayer),
        ),
      );

      const finalResponse = await Effect.runPromise(
        result.responseEffect.pipe(Effect.provide(mockQueueLayer)),
      );

      const text = await finalResponse.text();
      expect(text).toBe(ndjsonData);
    });

    it("releases funds when no usage found", async () => {
      // Stream with no usage data
      const sseData = `data: {"id":"1","choices":[{"text":"Hello"}]}\n\ndata: [DONE]\n\n`;
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

      const meteringContext = MockMeteringContext.fromProvider(
        "openai",
        "gpt-4",
      );

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", meteringContext).pipe(
          Effect.provide(mockQueueLayer),
        ),
      );

      const finalResponse = await Effect.runPromise(
        result.responseEffect.pipe(Effect.provide(mockQueueLayer)),
      );

      await finalResponse.text();

      // Note: Metering happens in stream finalizer with fresh DB/Payments instances,
      // so we can't assert on mocks here. The logic to release funds when no usage
      // is found is tested in router.ts tests.
    });

    it("handles invalid JSON in SSE stream", async () => {
      // Stream with invalid JSON that should be ignored
      const sseData = `data: {"id":"1","choices":[{"text":"Hello"}]}\n\ndata: {invalid json\n\ndata: [DONE]\n\n`;
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

      const meteringContext = MockMeteringContext.fromProvider(
        "openai",
        "gpt-4",
      );

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", meteringContext).pipe(
          Effect.provide(mockQueueLayer),
        ),
      );

      const finalResponse = await Effect.runPromise(
        result.responseEffect.pipe(Effect.provide(mockQueueLayer)),
      );

      const text = await finalResponse.text();
      expect(text).toBe(sseData);
    });

    it("handles invalid JSON in NDJSON stream", async () => {
      // Stream with invalid NDJSON that should be ignored
      const ndjsonData = `{"id":"1","choices":[{"text":"Hello"}]}\n{invalid json}\n{"id":"2","usage":{"prompt_tokens":10,"completion_tokens":5}}\n`;
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

      const meteringContext = MockMeteringContext.fromProvider(
        "google",
        "gemini-pro",
      );

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "ndjson", meteringContext).pipe(
          Effect.provide(mockQueueLayer),
        ),
      );

      const finalResponse = await Effect.runPromise(
        result.responseEffect.pipe(Effect.provide(mockQueueLayer)),
      );

      const text = await finalResponse.text();
      expect(text).toBe(ndjsonData);
    });

    it("processes remaining buffer with usage data", async () => {
      // Stream that ends with incomplete usage data in buffer
      const sseData = `data: {"id":"1","choices":[{"text":"Hello"}]}\n\ndata: {"id":"2","usage":{"prompt_tokens":10,"completion_tokens":5}}`;
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

      const meteringContext = MockMeteringContext.fromProvider(
        "openai",
        "gpt-4",
      );

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", meteringContext).pipe(
          Effect.provide(mockQueueLayer),
        ),
      );

      const finalResponse = await Effect.runPromise(
        result.responseEffect.pipe(Effect.provide(mockQueueLayer)),
      );

      const text = await finalResponse.text();

      // Verify the stream was processed correctly
      expect(text).toBe(sseData);

      // This exercises line 371: the remaining buffer contains usage data
      // that gets processed and set in the usageRef
    });

    it("handles unparsable remaining buffer", async () => {
      // Stream that ends with unparsable content in buffer
      const sseData = `data: {"id":"1","choices":[{"text":"Hello"}]}\n\ndata: incomplete`;
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

      const meteringContext = MockMeteringContext.fromProvider(
        "openai",
        "gpt-4",
      );

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", meteringContext).pipe(
          Effect.provide(mockQueueLayer),
        ),
      );

      const finalResponse = await Effect.runPromise(
        result.responseEffect.pipe(Effect.provide(mockQueueLayer)),
      );

      const text = await finalResponse.text();

      // Verify the stream was processed correctly, ignoring the unparsable buffer
      expect(text).toBe(sseData);

      // This exercises line 144: processRemainingBuffer returns null for unparsable content
    });

    it("processes remaining buffer with NDJSON format", async () => {
      // Stream that ends with incomplete NDJSON usage data in buffer
      const ndjsonData = `{"candidates":[{"content":{"parts":[{"text":"Hello"}]}}]}\n{"usageMetadata":{"promptTokenCount":10,"candidatesTokenCount":5}}`;
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

      const meteringContext = MockMeteringContext.fromProvider(
        "google",
        "gemini-pro",
      );

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "ndjson", meteringContext).pipe(
          Effect.provide(mockQueueLayer),
        ),
      );

      const finalResponse = await Effect.runPromise(
        result.responseEffect.pipe(Effect.provide(mockQueueLayer)),
      );

      const text = await finalResponse.text();

      // Verify the stream was processed correctly
      expect(text).toBe(ndjsonData);

      // This exercises line 119: processRemainingBuffer with ndjson format
    });

    it("handles queue enqueue failure gracefully", async () => {
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const sseData = `data: {"id":"1","usage":{"prompt_tokens":10,"completion_tokens":5}}\n\n`;
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

      const meteringContext = MockMeteringContext.fromProvider(
        "openai",
        "gpt-4",
      );

      // Create a failing queue layer
      const failingQueueLayer = Layer.succeed(RouterMeteringQueueService, {
        send: () => Effect.fail(new Error("Queue is down")),
      });

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", meteringContext).pipe(
          Effect.provide(failingQueueLayer),
        ),
      );

      const finalResponse = await Effect.runPromise(
        result.responseEffect.pipe(Effect.provide(failingQueueLayer)),
      );

      await finalResponse.text();

      // Verify error was logged but stream still completed
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        expect.stringContaining(
          "[settleMeteringForStream] Failed to enqueue metering",
        ),
        expect.anything(),
      );

      consoleErrorSpy.mockRestore();
    });
  });
});
