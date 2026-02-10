/**
 * Tests for common instrumentation utilities.
 */

import { SpanStatusCode } from "@opentelemetry/api";
/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, it, expect, vi, beforeEach } from "vitest";

import {
  GenAIAttributes,
  recordException,
  attachResponse,
  recordDroppedParams,
  startModelSpan,
  withSpanContext,
} from "./common";

// Mock configuration
vi.mock("@/ops/_internal/configuration", () => ({
  getTracer: vi.fn(),
}));

import { getTracer } from "@/ops/_internal/configuration";

describe("GenAIAttributes", () => {
  it("has correct attribute names", () => {
    expect(GenAIAttributes.OPERATION_NAME).toBe("gen_ai.operation.name");
    expect(GenAIAttributes.PROVIDER_NAME).toBe("gen_ai.system");
    expect(GenAIAttributes.REQUEST_MODEL).toBe("gen_ai.request.model");
    expect(GenAIAttributes.RESPONSE_MODEL).toBe("gen_ai.response.model");
    expect(GenAIAttributes.USAGE_INPUT_TOKENS).toBe(
      "gen_ai.usage.input_tokens",
    );
    expect(GenAIAttributes.USAGE_OUTPUT_TOKENS).toBe(
      "gen_ai.usage.output_tokens",
    );
  });
});

describe("recordException", () => {
  it("records exception details on span", () => {
    const mockSpan = {
      recordException: vi.fn(),
      setAttribute: vi.fn(),
      setStatus: vi.fn(),
    };

    const error = new Error("Test error message");
    error.name = "TestError";

    recordException(mockSpan as any, error);

    expect(mockSpan.recordException).toHaveBeenCalledWith(error);
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      "error.type",
      "TestError",
    );
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      "error.message",
      "Test error message",
    );
    expect(mockSpan.setStatus).toHaveBeenCalledWith({
      code: SpanStatusCode.ERROR,
      message: "Test error message",
    });
  });

  it("handles empty error message", () => {
    const mockSpan = {
      recordException: vi.fn(),
      setAttribute: vi.fn(),
      setStatus: vi.fn(),
    };

    const error = new Error();
    error.name = "EmptyError";

    recordException(mockSpan as any, error);

    expect(mockSpan.recordException).toHaveBeenCalledWith(error);
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      "error.type",
      "EmptyError",
    );
    // Should not set error.message for empty message
    expect(mockSpan.setStatus).toHaveBeenCalled();
  });
});

describe("attachResponse", () => {
  it("attaches response attributes to span", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockResponse = {
      modelId: "anthropic/claude-sonnet-4-20250514",
      finishReason: null,
      raw: { id: "resp_123" },
      messages: [
        {
          role: "user",
          content: [{ type: "text", text: "Hello" }],
          name: null,
        },
        {
          role: "assistant",
          content: [{ type: "text", text: "Hi there!" }],
          name: null,
          providerId: "anthropic",
          modelId: "anthropic/claude-sonnet-4-20250514",
          providerModelName: "claude-sonnet-4-20250514",
          rawMessage: null,
        },
      ],
      usage: {
        inputTokens: 10,
        outputTokens: 20,
        cacheReadTokens: 0,
        cacheWriteTokens: 0,
        reasoningTokens: 0,
      },
      content: [{ type: "text", text: "Hi there!" }],
    };

    const requestMessages = [
      { role: "user", content: [{ type: "text", text: "Hello" }], name: null },
    ];

    attachResponse(
      mockSpan as any,
      mockResponse as any,
      requestMessages as any,
    );

    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.RESPONSE_MODEL,
      "anthropic/claude-sonnet-4-20250514",
    );
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.RESPONSE_FINISH_REASONS,
      ["stop"],
    );
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.RESPONSE_ID,
      "resp_123",
    );
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.USAGE_INPUT_TOKENS,
      10,
    );
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.USAGE_OUTPUT_TOKENS,
      20,
    );
  });

  it("handles response without usage", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockResponse = {
      modelId: "openai/gpt-4",
      finishReason: "max_tokens",
      raw: null,
      messages: [],
      usage: null,
      content: [],
    };

    attachResponse(mockSpan as any, mockResponse as any, []);

    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.RESPONSE_MODEL,
      "openai/gpt-4",
    );
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.RESPONSE_FINISH_REASONS,
      ["length"],
    );
    // Should not set usage attributes
    expect(mockSpan.setAttribute).not.toHaveBeenCalledWith(
      GenAIAttributes.USAGE_INPUT_TOKENS,
      expect.anything(),
    );
  });

  it("handles response with non-object raw", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockResponse = {
      modelId: "test/model",
      finishReason: null,
      raw: "not an object",
      messages: [],
      usage: null,
      content: [],
    };

    attachResponse(mockSpan as any, mockResponse as any, []);

    // Should not set response ID for non-object raw
    expect(mockSpan.setAttribute).not.toHaveBeenCalledWith(
      GenAIAttributes.RESPONSE_ID,
      expect.anything(),
    );
  });

  it("maps refusal finish reason to content_filter", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockResponse = {
      modelId: "test/model",
      finishReason: "refusal",
      raw: null,
      messages: [],
      usage: null,
      content: [],
    };

    attachResponse(mockSpan as any, mockResponse as any, []);

    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.RESPONSE_FINISH_REASONS,
      ["content_filter"],
    );
  });

  it("maps context_length_exceeded finish reason to length", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockResponse = {
      modelId: "test/model",
      finishReason: "context_length_exceeded",
      raw: null,
      messages: [],
      usage: null,
      content: [],
    };

    attachResponse(mockSpan as any, mockResponse as any, []);

    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.RESPONSE_FINISH_REASONS,
      ["length"],
    );
  });

  it("passes through unknown finish reasons", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockResponse = {
      modelId: "test/model",
      finishReason: "tool_calls",
      raw: null,
      messages: [],
      usage: null,
      content: [],
    };

    attachResponse(mockSpan as any, mockResponse as any, []);

    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.RESPONSE_FINISH_REASONS,
      ["tool_calls"],
    );
  });

  it("extracts response_id from raw response", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockResponse = {
      modelId: "test/model",
      finishReason: null,
      raw: { response_id: "resp_456" },
      messages: [],
      usage: null,
      content: [],
    };

    attachResponse(mockSpan as any, mockResponse as any, []);

    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.RESPONSE_ID,
      "resp_456",
    );
  });

  it("extracts responseId from raw response", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockResponse = {
      modelId: "test/model",
      finishReason: null,
      raw: { responseId: "resp_789" },
      messages: [],
      usage: null,
      content: [],
    };

    attachResponse(mockSpan as any, mockResponse as any, []);

    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.RESPONSE_ID,
      "resp_789",
    );
  });

  it("handles raw response object without string id fields", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockResponse = {
      modelId: "test/model",
      finishReason: null,
      raw: { id: 12345, someOtherField: "value" }, // id is not a string
      messages: [],
      usage: null,
      content: [],
    };

    attachResponse(mockSpan as any, mockResponse as any, []);

    // Should not set response ID when id is not a string
    expect(mockSpan.setAttribute).not.toHaveBeenCalledWith(
      GenAIAttributes.RESPONSE_ID,
      expect.anything(),
    );
  });
});

describe("recordDroppedParams", () => {
  it("does nothing for empty dropped params", () => {
    const mockSpan = {
      addEvent: vi.fn(),
    };

    recordDroppedParams(mockSpan as any, {});

    expect(mockSpan.addEvent).not.toHaveBeenCalled();
  });

  it("records dropped params as event", () => {
    const mockSpan = {
      addEvent: vi.fn(),
    };

    const droppedParams = {
      complexParam: { nested: "value" },
      anotherParam: [1, 2, 3],
    };

    recordDroppedParams(mockSpan as any, droppedParams);

    expect(mockSpan.addEvent).toHaveBeenCalledWith(
      "gen_ai.request.params.untracked",
      expect.objectContaining({
        "gen_ai.untracked_params.count": 2,
        "gen_ai.untracked_params.keys": ["complexParam", "anotherParam"],
      }),
    );
  });
});

describe("startModelSpan", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("returns null span when tracer is not configured", () => {
    vi.mocked(getTracer).mockReturnValue(null);

    const result = startModelSpan({
      modelId: "anthropic/claude-sonnet-4-20250514",
      providerId: "anthropic",
      messages: [],
      params: {},
    });

    expect(result.span).toBeNull();
    expect(result.droppedParams).toEqual({});
  });

  it("creates span with GenAI attributes when tracer is configured", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockTracer = {
      startSpan: vi.fn().mockReturnValue(mockSpan),
    };

    vi.mocked(getTracer).mockReturnValue(mockTracer as any);

    const result = startModelSpan({
      modelId: "anthropic/claude-sonnet-4-20250514",
      providerId: "anthropic",
      messages: [
        {
          role: "user",
          content: [{ type: "text", text: "Hello" }],
          name: null,
        },
      ],
      params: {
        temperature: 0.7,
        maxTokens: 1000,
      },
    });

    expect(result.span).toBe(mockSpan);
    expect(mockTracer.startSpan).toHaveBeenCalledWith(
      "chat anthropic/claude-sonnet-4-20250514",
      expect.objectContaining({ kind: 2 }), // SpanKind.CLIENT = 2
      expect.anything(),
    );

    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.OPERATION_NAME,
      "chat",
    );
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.PROVIDER_NAME,
      "anthropic",
    );
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.REQUEST_MODEL,
      "anthropic/claude-sonnet-4-20250514",
    );
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.REQUEST_TEMPERATURE,
      0.7,
    );
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.REQUEST_MAX_TOKENS,
      1000,
    );
  });

  it("separates supported and dropped params", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockTracer = {
      startSpan: vi.fn().mockReturnValue(mockSpan),
    };

    vi.mocked(getTracer).mockReturnValue(mockTracer as any);

    const result = startModelSpan({
      modelId: "test/model",
      providerId: "test",
      messages: [],
      params: {
        temperature: 0.5, // supported
        customObject: { complex: "value" }, // dropped (object)
      } as any,
    });

    expect(result.droppedParams).toEqual({
      customObject: { complex: "value" },
    });
  });

  it("normalizes Symbol values in dropped params", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockTracer = {
      startSpan: vi.fn().mockReturnValue(mockSpan),
    };

    vi.mocked(getTracer).mockReturnValue(mockTracer as any);

    const testSymbol = Symbol("test");
    const result = startModelSpan({
      modelId: "test/model",
      providerId: "test",
      messages: [],
      params: {
        customSymbol: testSymbol,
      } as any,
    });

    // Symbol should be converted to string representation
    expect(result.droppedParams).toHaveProperty("customSymbol");
    expect(result.droppedParams.customSymbol).toBe("Symbol(test)");
  });

  it("supports string array params (stopSequences)", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockTracer = {
      startSpan: vi.fn().mockReturnValue(mockSpan),
    };

    vi.mocked(getTracer).mockReturnValue(mockTracer as any);

    const result = startModelSpan({
      modelId: "test/model",
      providerId: "test",
      messages: [],
      params: {
        stopSequences: ["END", "STOP"],
      } as any,
    });

    // Should set stop sequences as array
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.REQUEST_STOP_SEQUENCES,
      ["END", "STOP"],
    );
    // String arrays should be supported, not dropped
    expect(result.droppedParams).toEqual({});
  });

  it("drops array with non-string items", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockTracer = {
      startSpan: vi.fn().mockReturnValue(mockSpan),
    };

    vi.mocked(getTracer).mockReturnValue(mockTracer as any);

    const result = startModelSpan({
      modelId: "test/model",
      providerId: "test",
      messages: [],
      params: {
        mixedArray: ["string", 123, true],
      } as any,
    });

    // Mixed arrays should be dropped and normalized
    expect(result.droppedParams).toHaveProperty("mixedArray");
    expect(result.droppedParams.mixedArray).toEqual(["string", 123, true]);
  });

  it("sets output type to json when format is provided", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockTracer = {
      startSpan: vi.fn().mockReturnValue(mockSpan),
    };

    vi.mocked(getTracer).mockReturnValue(mockTracer as any);

    startModelSpan({
      modelId: "test/model",
      providerId: "test",
      messages: [],
      format: { type: "json", schema: {} } as any,
      params: {},
    });

    // Should set output type to json
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.OUTPUT_TYPE,
      "json",
    );
  });

  it("includes system instructions when present", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockTracer = {
      startSpan: vi.fn().mockReturnValue(mockSpan),
    };

    vi.mocked(getTracer).mockReturnValue(mockTracer as any);

    startModelSpan({
      modelId: "test/model",
      providerId: "test",
      messages: [
        {
          role: "system",
          content: { type: "text", text: "You are helpful" },
        },
        {
          role: "user",
          content: [{ type: "text", text: "Hello" }],
          name: null,
        },
      ],
      params: {},
    });

    // Should set system instructions
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.SYSTEM_INSTRUCTIONS,
      expect.any(String),
    );
  });

  it("includes tool definitions when tools provided", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockTracer = {
      startSpan: vi.fn().mockReturnValue(mockSpan),
    };

    vi.mocked(getTracer).mockReturnValue(mockTracer as any);

    const mockTools = [
      {
        name: "testTool",
        description: "A test tool",
        __schema: { name: "testTool", description: "A test tool" },
      },
    ];

    startModelSpan({
      modelId: "test/model",
      providerId: "test",
      messages: [],
      tools: mockTools as any,
      params: {},
    });

    // Should set tool definitions
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.TOOL_DEFINITIONS,
      expect.any(String),
    );
  });

  it("handles tools without __schema using name and description", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockTracer = {
      startSpan: vi.fn().mockReturnValue(mockSpan),
    };

    vi.mocked(getTracer).mockReturnValue(mockTracer as any);

    // Tools without __schema but with name
    const mockTools = [
      {
        name: "simpleTool",
        description: "A simple tool",
      },
    ];

    startModelSpan({
      modelId: "test/model",
      providerId: "test",
      messages: [],
      tools: mockTools as any,
      params: {},
    });

    // Should set tool definitions using name/description fallback
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.TOOL_DEFINITIONS,
      expect.stringContaining("simpleTool"),
    );
  });

  it("handles tools without __schema or name", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockTracer = {
      startSpan: vi.fn().mockReturnValue(mockSpan),
    };

    vi.mocked(getTracer).mockReturnValue(mockTracer as any);

    // Tools without __schema or name (raw provider tool)
    const mockTools = [
      {
        type: "function",
        function: { name: "rawTool", parameters: {} },
      },
    ];

    startModelSpan({
      modelId: "test/model",
      providerId: "test",
      messages: [],
      tools: mockTools as any,
      params: {},
    });

    // Should set tool definitions with the raw tool object
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.TOOL_DEFINITIONS,
      expect.any(String),
    );
  });

  it("handles toolkit with tools array", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockTracer = {
      startSpan: vi.fn().mockReturnValue(mockSpan),
    };

    vi.mocked(getTracer).mockReturnValue(mockTracer as any);

    // Toolkit object with tools array
    const mockToolkit = {
      tools: [
        {
          name: "toolkitTool",
          description: "A toolkit tool",
          __schema: { name: "toolkitTool" },
        },
      ],
    };

    startModelSpan({
      modelId: "test/model",
      providerId: "test",
      messages: [],
      tools: mockToolkit as any,
      params: {},
    });

    // Should set tool definitions from toolkit
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.TOOL_DEFINITIONS,
      expect.stringContaining("toolkitTool"),
    );
  });

  it("handles empty tools array", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockTracer = {
      startSpan: vi.fn().mockReturnValue(mockSpan),
    };

    vi.mocked(getTracer).mockReturnValue(mockTracer as any);

    startModelSpan({
      modelId: "test/model",
      providerId: "test",
      messages: [],
      tools: [] as any,
      params: {},
    });

    // Should not set tool definitions for empty array
    expect(mockSpan.setAttribute).not.toHaveBeenCalledWith(
      GenAIAttributes.TOOL_DEFINITIONS,
      expect.anything(),
    );
  });

  it("includes choice count when n param is provided", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockTracer = {
      startSpan: vi.fn().mockReturnValue(mockSpan),
    };

    vi.mocked(getTracer).mockReturnValue(mockTracer as any);

    startModelSpan({
      modelId: "test/model",
      providerId: "test",
      messages: [],
      params: {
        n: 3,
      } as any,
    });

    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.REQUEST_CHOICE_COUNT,
      3,
    );
  });

  it("handles messages with image content", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockTracer = {
      startSpan: vi.fn().mockReturnValue(mockSpan),
    };

    vi.mocked(getTracer).mockReturnValue(mockTracer as any);

    startModelSpan({
      modelId: "test/model",
      providerId: "test",
      messages: [
        {
          role: "user",
          content: [
            { type: "text", text: "What is this?" },
            { type: "image", data: "base64data", mediaType: "image/png" },
          ] as any,
          name: null,
        },
      ],
      params: {},
    });

    // Should have set input messages with image content omitted
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.INPUT_MESSAGES,
      expect.stringContaining("...(omitted)"),
    );
  });

  it("handles messages with document content", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockTracer = {
      startSpan: vi.fn().mockReturnValue(mockSpan),
    };

    vi.mocked(getTracer).mockReturnValue(mockTracer as any);

    startModelSpan({
      modelId: "test/model",
      providerId: "test",
      messages: [
        {
          role: "user",
          content: [
            { type: "text", text: "Summarize this document" },
            {
              type: "document",
              source: {
                type: "base64_document_source",
                data: "JVBERi0xLjcK...",
                mediaType: "application/pdf",
              },
            },
          ] as any,
          name: null,
        },
      ],
      params: {},
    });

    // Should have set input messages with document content omitted
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.INPUT_MESSAGES,
      expect.stringContaining("...(omitted)"),
    );
    // Should contain the document type
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.INPUT_MESSAGES,
      expect.stringContaining('"type":"document"'),
    );
  });

  it("handles messages with tool_call content", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockTracer = {
      startSpan: vi.fn().mockReturnValue(mockSpan),
    };

    vi.mocked(getTracer).mockReturnValue(mockTracer as any);

    startModelSpan({
      modelId: "test/model",
      providerId: "test",
      messages: [
        {
          role: "assistant",
          content: [
            {
              type: "tool_call",
              id: "call_123",
              name: "get_weather",
              args: { location: "NYC" },
            },
          ],
          name: null,
        } as any,
      ],
      params: {},
    });

    // Should have serialized tool call content
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.INPUT_MESSAGES,
      expect.stringContaining("tool_use"),
    );
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.INPUT_MESSAGES,
      expect.stringContaining("get_weather"),
    );
  });

  it("handles messages with tool_result content", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockTracer = {
      startSpan: vi.fn().mockReturnValue(mockSpan),
    };

    vi.mocked(getTracer).mockReturnValue(mockTracer as any);

    startModelSpan({
      modelId: "test/model",
      providerId: "test",
      messages: [
        {
          role: "user",
          content: [
            {
              type: "tool_result",
              id: "call_123",
              result: "Sunny, 72F",
            },
          ] as any,
          name: null,
        },
      ],
      params: {},
    });

    // Should have serialized tool result content
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.INPUT_MESSAGES,
      expect.stringContaining("tool_result"),
    );
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.INPUT_MESSAGES,
      expect.stringContaining("Sunny"),
    );
  });

  it("handles messages with unknown content types", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockTracer = {
      startSpan: vi.fn().mockReturnValue(mockSpan),
    };

    vi.mocked(getTracer).mockReturnValue(mockTracer as any);

    startModelSpan({
      modelId: "test/model",
      providerId: "test",
      messages: [
        {
          role: "user",
          content: [
            {
              type: "custom_type",
              data: "custom data",
            } as any,
          ],
          name: null,
        },
      ],
      params: {},
    });

    // Should pass through unknown content types as-is
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.INPUT_MESSAGES,
      expect.stringContaining("custom_type"),
    );
  });

  it("handles messages with plain string content", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockTracer = {
      startSpan: vi.fn().mockReturnValue(mockSpan),
    };

    vi.mocked(getTracer).mockReturnValue(mockTracer as any);

    startModelSpan({
      modelId: "test/model",
      providerId: "test",
      messages: [
        {
          role: "user",
          content: "Hello, this is a plain string message" as any,
          name: null,
        },
      ],
      params: {},
    });

    // Should serialize plain string content directly
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.INPUT_MESSAGES,
      expect.stringContaining("Hello, this is a plain string message"),
    );
  });

  it("handles messages with array content containing plain strings", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockTracer = {
      startSpan: vi.fn().mockReturnValue(mockSpan),
    };

    vi.mocked(getTracer).mockReturnValue(mockTracer as any);

    startModelSpan({
      modelId: "test/model",
      providerId: "test",
      messages: [
        {
          role: "user",
          content: ["Hello", "World"] as any,
          name: null,
        },
      ],
      params: {},
    });

    // Should convert plain strings to text parts
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.INPUT_MESSAGES,
      expect.stringContaining("Hello"),
    );
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.INPUT_MESSAGES,
      expect.stringContaining("World"),
    );
  });

  it("handles stop param as string (normalizes to array)", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockTracer = {
      startSpan: vi.fn().mockReturnValue(mockSpan),
    };

    vi.mocked(getTracer).mockReturnValue(mockTracer as any);

    startModelSpan({
      modelId: "test/model",
      providerId: "test",
      messages: [],
      params: {
        stop: "END",
      } as any,
    });

    // Should normalize string stop to array
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.REQUEST_STOP_SEQUENCES,
      ["END"],
    );
  });

  it("skips params with undefined value", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockTracer = {
      startSpan: vi.fn().mockReturnValue(mockSpan),
    };

    vi.mocked(getTracer).mockReturnValue(mockTracer as any);

    startModelSpan({
      modelId: "test/model",
      providerId: "test",
      messages: [],
      params: {
        temperature: undefined,
        maxTokens: 100,
      } as any,
    });

    // Should set maxTokens but not temperature
    expect(mockSpan.setAttribute).toHaveBeenCalledWith(
      GenAIAttributes.REQUEST_MAX_TOKENS,
      100,
    );
    // Temperature should not be set since it's undefined
    expect(mockSpan.setAttribute).not.toHaveBeenCalledWith(
      GenAIAttributes.REQUEST_TEMPERATURE,
      expect.anything(),
    );
  });

  it("normalizes null values in dropped object params", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockTracer = {
      startSpan: vi.fn().mockReturnValue(mockSpan),
    };

    vi.mocked(getTracer).mockReturnValue(mockTracer as any);

    const result = startModelSpan({
      modelId: "test/model",
      providerId: "test",
      messages: [],
      params: {
        complexObj: { key: null, nested: { value: undefined } },
      } as any,
    });

    // Null and undefined should be normalized to null
    expect(result.droppedParams).toHaveProperty("complexObj");
    expect((result.droppedParams.complexObj as any).key).toBe(null);
    expect((result.droppedParams.complexObj as any).nested.value).toBe(null);
  });

  it("creates span without context when activate is false", () => {
    const mockSpan = {
      setAttribute: vi.fn(),
    };

    const mockTracer = {
      startSpan: vi.fn().mockReturnValue(mockSpan),
    };

    vi.mocked(getTracer).mockReturnValue(mockTracer as any);

    startModelSpan({
      modelId: "test/model",
      providerId: "test",
      messages: [],
      params: {},
      activate: false,
    });

    // Should call startSpan with undefined context
    expect(mockTracer.startSpan).toHaveBeenCalledWith(
      "chat test/model",
      expect.objectContaining({ kind: 2 }),
      undefined,
    );
  });
});

describe("withSpanContext", () => {
  it("executes function when span is null", async () => {
    const fn = vi.fn().mockResolvedValue("result");

    const result = await withSpanContext(null, fn);

    expect(result).toBe("result");
    expect(fn).toHaveBeenCalled();
  });

  it("executes function within span context when span exists", async () => {
    const mockSpan = {};
    const fn = vi.fn().mockResolvedValue("result");

    const result = await withSpanContext(mockSpan as any, fn);

    expect(result).toBe("result");
    expect(fn).toHaveBeenCalled();
  });
});
