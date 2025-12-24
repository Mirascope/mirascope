import { describe, it, expect, vi, beforeEach } from "vitest";
import { Effect, Layer } from "effect";
import {
  parseStreamingResponse,
  performStreamMetering,
  settleMeteringForStream,
} from "@/api/router/streaming";
import { ProxyError } from "@/errors";
import { MockMeteringContext } from "@/tests/api";
import { Database } from "@/db";
import { Payments } from "@/payments";

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

      const meteringContext = MockMeteringContext.fromProvider(
        "openai",
        "gpt-4",
      );

      const result = await Effect.runPromise(
        parseStreamingResponse(response, "sse", meteringContext),
      );

      expect(result.responseEffect).toBeDefined();

      // Run the responseEffect to get the Response
      const finalResponse = await Effect.runPromise(result.responseEffect);

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
        parseStreamingResponse(response, "sse", meteringContext),
      );

      const finalResponse = await Effect.runPromise(result.responseEffect);

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
        parseStreamingResponse(response, "ndjson", meteringContext),
      );

      const finalResponse = await Effect.runPromise(result.responseEffect);

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
        parseStreamingResponse(response, "sse", meteringContext),
      );

      const finalResponse = await Effect.runPromise(result.responseEffect);

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
        parseStreamingResponse(response, "sse", meteringContext),
      );

      // Should fail when trying to read the stream
      await expect(
        Effect.runPromise(
          result.responseEffect.pipe(
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
        parseStreamingResponse(response, "sse", meteringContext),
      );

      const finalResponse = await Effect.runPromise(result.responseEffect);

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
        parseStreamingResponse(response, "ndjson", meteringContext),
      );

      const finalResponse = await Effect.runPromise(result.responseEffect);

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
        parseStreamingResponse(response, "sse", meteringContext),
      );

      const finalResponse = await Effect.runPromise(result.responseEffect);

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
        parseStreamingResponse(response, "sse", meteringContext),
      );

      const finalResponse = await Effect.runPromise(result.responseEffect);

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
        parseStreamingResponse(response, "ndjson", meteringContext),
      );

      const finalResponse = await Effect.runPromise(result.responseEffect);

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
        parseStreamingResponse(response, "sse", meteringContext),
      );

      const finalResponse = await Effect.runPromise(result.responseEffect);

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
        parseStreamingResponse(response, "sse", meteringContext),
      );

      const finalResponse = await Effect.runPromise(result.responseEffect);

      const text = await finalResponse.text();

      // Verify the stream was processed correctly, ignoring the unparsable buffer
      expect(text).toBe(sseData);

      // This exercises line 144: processRemainingBuffer returns null for unparsable content
    });
  });

  describe("performStreamMetering", () => {
    it("should update DB with failure and release funds when no usage data", async () => {
      // Mock update and releaseFunds calls
      const updateMock = vi.fn(() => Effect.succeed(undefined));
      const releaseFundsMock = vi.fn(() => Effect.succeed(undefined));

      const mockDbLayer = Layer.succeed(Database, {
        organizations: {
          projects: {
            environments: {
              apiKeys: {
                routerRequests: {
                  update: updateMock,
                },
              },
            },
          },
        },
      } as never);

      const mockPaymentsLayer = Layer.succeed(Payments, {
        products: {
          router: {
            releaseFunds: releaseFundsMock,
          },
        },
      } as never);

      const meteringContext = MockMeteringContext.fromProvider(
        "openai",
        "gpt-4",
      );

      await Effect.runPromise(
        performStreamMetering(null, meteringContext).pipe(
          Effect.provide(mockDbLayer),
          Effect.provide(mockPaymentsLayer),
        ),
      );

      // Verify update was called with failure status
      expect(updateMock).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            status: "failure",
            errorMessage: "No usage data from stream",
          }) as unknown,
        }),
      );

      // Verify releaseFunds was called
      expect(releaseFundsMock).toHaveBeenCalledWith(
        meteringContext.reservationId,
      );
    });

    it("should update DB with failure and release funds when cost calculation fails", async () => {
      // Mock update and releaseFunds calls
      const updateMock = vi.fn(() => Effect.succeed(undefined));
      const releaseFundsMock = vi.fn(() => Effect.succeed(undefined));

      const mockDbLayer = Layer.succeed(Database, {
        organizations: {
          projects: {
            environments: {
              apiKeys: {
                routerRequests: {
                  update: updateMock,
                },
              },
            },
          },
        },
      } as never);

      const mockPaymentsLayer = Layer.succeed(Payments, {
        products: {
          router: {
            releaseFunds: releaseFundsMock,
          },
        },
      } as never);

      const meteringContext = MockMeteringContext.fromProvider(
        "openai",
        "unknown-model", // Will cause cost calculation to fail
      );

      const usage = {
        inputTokens: 10,
        outputTokens: 5,
      };

      await Effect.runPromise(
        performStreamMetering(usage, meteringContext).pipe(
          Effect.provide(mockDbLayer),
          Effect.provide(mockPaymentsLayer),
        ),
      );

      // Verify update was called with failure status
      expect(updateMock).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            status: "failure",
            errorMessage: "Cost calculation failed",
          }) as unknown,
        }),
      );

      // Verify releaseFunds was called
      expect(releaseFundsMock).toHaveBeenCalledWith(
        meteringContext.reservationId,
      );
    });

    it("should update DB with success and settle funds when usage and cost are valid", async () => {
      // Mock update and settleFunds calls
      const updateMock = vi.fn(() => Effect.succeed(undefined));
      const settleFundsMock = vi.fn(() => Effect.succeed(undefined));

      const mockDbLayer = Layer.succeed(Database, {
        organizations: {
          projects: {
            environments: {
              apiKeys: {
                routerRequests: {
                  update: updateMock,
                },
              },
            },
          },
        },
      } as never);

      const mockPaymentsLayer = Layer.succeed(Payments, {
        products: {
          router: {
            settleFunds: settleFundsMock,
          },
        },
      } as never);

      const meteringContext = MockMeteringContext.fromProvider(
        "openai",
        "gpt-4",
      );

      const usage = {
        inputTokens: 100,
        outputTokens: 50,
      };

      await Effect.runPromise(
        performStreamMetering(usage, meteringContext).pipe(
          Effect.provide(mockDbLayer),
          Effect.provide(mockPaymentsLayer),
        ),
      );

      // Verify update was called with success status and usage data
      expect(updateMock).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            status: "success",
            inputTokens: 100n,
            outputTokens: 50n,
          }) as unknown,
        }),
      );

      // Verify settleFunds was called with the correct cost
      expect(settleFundsMock).toHaveBeenCalledWith(
        meteringContext.reservationId,
        expect.any(BigInt),
      );
    });

    it("should handle cache tokens correctly", async () => {
      // Mock update and settleFunds calls
      const updateMock = vi.fn(() => Effect.succeed(undefined));
      const settleFundsMock = vi.fn(() => Effect.succeed(undefined));

      const mockDbLayer = Layer.succeed(Database, {
        organizations: {
          projects: {
            environments: {
              apiKeys: {
                routerRequests: {
                  update: updateMock,
                },
              },
            },
          },
        },
      } as never);

      const mockPaymentsLayer = Layer.succeed(Payments, {
        products: {
          router: {
            settleFunds: settleFundsMock,
          },
        },
      } as never);

      const meteringContext = MockMeteringContext.fromProvider(
        "openai",
        "gpt-4",
      );

      const usage = {
        inputTokens: 100,
        outputTokens: 50,
        cacheReadTokens: 20,
        cacheWriteTokens: 10,
      };

      await Effect.runPromise(
        performStreamMetering(usage, meteringContext).pipe(
          Effect.provide(mockDbLayer),
          Effect.provide(mockPaymentsLayer),
        ),
      );

      // Verify update was called with cache token fields
      expect(updateMock).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            status: "success",
            inputTokens: 100n,
            outputTokens: 50n,
            cacheReadTokens: 20n,
            cacheWriteTokens: 10n,
          }) as unknown,
        }),
      );
    });

    it("should handle zero input tokens correctly", async () => {
      // Mock update and settleFunds calls
      const updateMock = vi.fn(() => Effect.succeed(undefined));
      const settleFundsMock = vi.fn(() => Effect.succeed(undefined));

      const mockDbLayer = Layer.succeed(Database, {
        organizations: {
          projects: {
            environments: {
              apiKeys: {
                routerRequests: {
                  update: updateMock,
                },
              },
            },
          },
        },
      } as never);

      const mockPaymentsLayer = Layer.succeed(Payments, {
        products: {
          router: {
            settleFunds: settleFundsMock,
          },
        },
      } as never);

      const meteringContext = MockMeteringContext.fromProvider(
        "openai",
        "gpt-4",
      );

      const usage = {
        inputTokens: 0,
        outputTokens: 10,
      };

      await Effect.runPromise(
        performStreamMetering(usage, meteringContext).pipe(
          Effect.provide(mockDbLayer),
          Effect.provide(mockPaymentsLayer),
        ),
      );

      // Verify update was called with null for zero inputTokens
      expect(updateMock).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            status: "success",
            inputTokens: null,
            outputTokens: 10n,
          }) as unknown,
        }),
      );
    });

    it("should handle zero output tokens correctly", async () => {
      // Mock update and settleFunds calls
      const updateMock = vi.fn(() => Effect.succeed(undefined));
      const settleFundsMock = vi.fn(() => Effect.succeed(undefined));

      const mockDbLayer = Layer.succeed(Database, {
        organizations: {
          projects: {
            environments: {
              apiKeys: {
                routerRequests: {
                  update: updateMock,
                },
              },
            },
          },
        },
      } as never);

      const mockPaymentsLayer = Layer.succeed(Payments, {
        products: {
          router: {
            settleFunds: settleFundsMock,
          },
        },
      } as never);

      const meteringContext = MockMeteringContext.fromProvider(
        "openai",
        "gpt-4",
      );

      const usage = {
        inputTokens: 10,
        outputTokens: 0,
      };

      await Effect.runPromise(
        performStreamMetering(usage, meteringContext).pipe(
          Effect.provide(mockDbLayer),
          Effect.provide(mockPaymentsLayer),
        ),
      );

      // Verify update was called with null for zero outputTokens
      expect(updateMock).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            status: "success",
            inputTokens: 10n,
            outputTokens: null,
          }) as unknown,
        }),
      );
    });
  });

  describe("settleMeteringForStream", () => {
    it("should handle layer construction errors gracefully", async () => {
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const meteringContext = MockMeteringContext.fromProvider(
        "openai",
        "gpt-4",
      );

      // Provide invalid database URL to trigger layer construction error
      const invalidContext = {
        ...meteringContext,
        databaseUrl: "invalid://not-a-real-database",
      };

      const usage = {
        inputTokens: 10,
        outputTokens: 5,
      };

      // Should succeed despite layer construction failure (catchAll handles it)
      await Effect.runPromise(settleMeteringForStream(usage, invalidContext));

      // Verify error was logged
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        "[Stream.ensuring] Failed to create Database layer for metering:",
        expect.anything(),
      );

      consoleErrorSpy.mockRestore();
    });
  });

  describe("parseStreamingResponse - remaining buffer", () => {
    it("processes remaining NDJSON buffer with usage data", async () => {
      // NDJSON stream that ends with incomplete usage data in buffer (no final newline)
      const ndjsonData = `{"id":"1","choices":[{"text":"Hello"}]}\n{"id":"2","usageMetadata":{"promptTokenCount":10,"candidatesTokenCount":5}}`;
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
        parseStreamingResponse(response, "ndjson", meteringContext),
      );

      const finalResponse = await Effect.runPromise(result.responseEffect);

      const text = await finalResponse.text();

      // Verify the stream was processed correctly
      expect(text).toBe(ndjsonData);

      // This exercises line 142: processRemainingBuffer with format === "ndjson"
    });
  });
});
