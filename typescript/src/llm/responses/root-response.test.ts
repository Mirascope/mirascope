/**
 * Tests for RootResponse.
 */

import { describe, it, expect } from "vitest";
import { z } from "zod";

import type {
  AssistantContentPart,
  Text,
  Thought,
  ToolCall,
} from "@/llm/content";
import type { Format, FormattingMode } from "@/llm/formatting";
import type { Message } from "@/llm/messages";
import type { Params } from "@/llm/models";
import type { ModelId, ProviderId } from "@/llm/providers";
import type { FinishReason } from "@/llm/responses/finish-reason";
import type { Usage } from "@/llm/responses/usage";

import { ParseError } from "@/llm/exceptions";
import { FORMAT_TYPE, defineOutputParser } from "@/llm/formatting";
import { RootResponse } from "@/llm/responses/root-response";

/** Helper to create mock Format objects for testing */
function createMockFormat(
  options: {
    mode?: FormattingMode;
    validator?: z.ZodType | null;
    outputParser?: ((resp: RootResponse) => unknown) | null;
  } = {},
): Format {
  const { mode = "json", validator = null, outputParser = null } = options;

  // If outputParser is provided, wrap it in a proper OutputParser
  const wrappedOutputParser = outputParser
    ? defineOutputParser({
        formattingInstructions: "test",
        parser: outputParser,
      })
    : null;

  return {
    __formatType: FORMAT_TYPE,
    name: "TestFormat",
    description: null,
    schema: {
      type: "object",
      properties: {},
      required: [],
      additionalProperties: false,
    },
    mode,
    validator,
    toolSchemaUnwrapKey: null,
    outputParser: wrappedOutputParser,
    formattingInstructions: null,
    createToolSchema: () => ({
      name: "test",
      description: "test",
      parameters: {
        type: "object",
        properties: {},
        required: [],
        additionalProperties: false,
      },
    }),
  };
}

// Concrete implementation for testing
class TestResponse extends RootResponse {
  readonly raw: unknown;
  readonly providerId: ProviderId;
  readonly modelId: ModelId;
  readonly providerModelName: string;
  readonly params: Params;
  readonly messages: readonly Message[];
  readonly content: readonly AssistantContentPart[];
  readonly texts: readonly Text[];
  readonly toolCalls: readonly ToolCall[];
  readonly thoughts: readonly Thought[];
  readonly finishReason: FinishReason | null;
  readonly usage: Usage | null;
  readonly format: Format | null;

  constructor(
    content: readonly AssistantContentPart[],
    format: Format | null = null,
  ) {
    super();
    this.raw = {};
    this.providerId = "anthropic";
    this.modelId = "anthropic/claude-sonnet-4-20250514";
    this.providerModelName = "claude-sonnet-4-20250514";
    this.params = {};
    this.messages = [];
    this.content = content;
    this.texts = content.filter((c): c is Text => c.type === "text");
    this.toolCalls = content.filter(
      (c): c is ToolCall => c.type === "tool_call",
    );
    this.thoughts = content.filter((c): c is Thought => c.type === "thought");
    this.finishReason = null;
    this.usage = null;
    this.format = format;
  }
}

describe("RootResponse", () => {
  describe("text()", () => {
    it("returns empty string when no text content", () => {
      const response = new TestResponse([]);
      expect(response.text()).toBe("");
    });

    it("returns single text content", () => {
      const response = new TestResponse([{ type: "text", text: "Hello!" }]);
      expect(response.text()).toBe("Hello!");
    });

    it("joins multiple text parts with newline by default", () => {
      const response = new TestResponse([
        { type: "text", text: "Hello" },
        { type: "text", text: "World" },
      ]);
      expect(response.text()).toBe("Hello\nWorld");
    });

    it("joins with custom separator", () => {
      const response = new TestResponse([
        { type: "text", text: "Hello" },
        { type: "text", text: "World" },
      ]);
      expect(response.text(" ")).toBe("Hello World");
      expect(response.text("")).toBe("HelloWorld");
    });
  });

  describe("pretty()", () => {
    it("returns empty string for empty content", () => {
      const response = new TestResponse([]);
      expect(response.pretty()).toBe("");
    });

    it("formats text content", () => {
      const response = new TestResponse([{ type: "text", text: "Hello!" }]);
      expect(response.pretty()).toBe("Hello!");
    });

    it("formats tool call content", () => {
      const response = new TestResponse([
        {
          type: "tool_call",
          id: "call_1",
          name: "calculator",
          args: '{"a": 1, "b": 2}',
        },
      ]);
      expect(response.pretty()).toBe(
        '**ToolCall (calculator):** {"a": 1, "b": 2}',
      );
    });

    it("formats thought content with indentation", () => {
      const response = new TestResponse([
        {
          type: "thought",
          thought: "Let me think about this.\nIt seems complex.",
        },
      ]);
      expect(response.pretty()).toBe(
        "**Thinking:**\n  Let me think about this.\n  It seems complex.",
      );
    });

    it("formats mixed content with double newlines", () => {
      const response = new TestResponse([
        { type: "thought", thought: "Thinking first" },
        {
          type: "tool_call",
          id: "call_1",
          name: "calc",
          args: '{"op": "add"}',
        },
        { type: "text", text: "Here is my answer!" },
      ]);

      const expected = [
        "**Thinking:**\n  Thinking first",
        '**ToolCall (calc):** {"op": "add"}',
        "Here is my answer!",
      ].join("\n\n");

      expect(response.pretty()).toBe(expected);
    });
  });

  describe("parse()", () => {
    it("returns null when no format is specified", () => {
      const response = new TestResponse([{ type: "text", text: "Hello!" }]);
      expect(response.parse()).toBeNull();
    });

    it("parses JSON response with format", () => {
      const format = createMockFormat();
      const response = new TestResponse(
        [{ type: "text", text: '{"title": "Test Book"}' }],
        format,
      );
      expect(response.parse()).toEqual({ title: "Test Book" });
    });

    it("parses JSON with surrounding text", () => {
      const format = createMockFormat();
      const response = new TestResponse(
        [{ type: "text", text: 'Here is the data: {"name": "Alice"}' }],
        format,
      );
      expect(response.parse()).toEqual({ name: "Alice" });
    });

    it("validates with Zod when validator is provided", () => {
      const BookSchema = z.object({
        title: z.string(),
        author: z.string(),
      });
      const format = createMockFormat({ validator: BookSchema });
      const response = new TestResponse(
        [
          {
            type: "text",
            text: '{"title": "1984", "author": "George Orwell"}',
          },
        ],
        format,
      );
      expect(response.parse()).toEqual({
        title: "1984",
        author: "George Orwell",
      });
    });

    it("throws ParseError when validation fails", () => {
      const BookSchema = z.object({
        title: z.string(),
        author: z.string(),
      });
      const format = createMockFormat({ validator: BookSchema });
      const response = new TestResponse(
        [{ type: "text", text: '{"title": "1984"}' }], // missing author
        format,
      );
      expect(() => response.parse()).toThrow(ParseError);
      expect(() => response.parse()).toThrow("Validation failed");
    });

    it("throws ParseError when JSON is invalid", () => {
      const format = createMockFormat();
      const response = new TestResponse(
        [{ type: "text", text: "not valid json" }],
        format,
      );
      expect(() => response.parse()).toThrow(ParseError);
    });

    it("uses OutputParser when provided", () => {
      const format = createMockFormat({
        mode: "parser",
        outputParser: (resp: RootResponse) => ({
          custom: resp.text().toUpperCase(),
        }),
      });
      const response = new TestResponse(
        [{ type: "text", text: "hello world" }],
        format,
      );
      expect(response.parse()).toEqual({ custom: "HELLO WORLD" });
    });

    it("throws when OutputParser fails", () => {
      const format = createMockFormat({
        mode: "parser",
        outputParser: () => {
          throw new Error("Parser error");
        },
      });
      const response = new TestResponse(
        [{ type: "text", text: "hello" }],
        format,
      );
      expect(() => response.parse()).toThrow(ParseError);
      expect(() => response.parse()).toThrow("OutputParser failed");
    });

    it("throws when OutputParser fails with non-Error", () => {
      const format = createMockFormat({
        mode: "parser",
        outputParser: () => {
          throw "string error"; // eslint-disable-line @typescript-eslint/only-throw-error
        },
      });
      const response = new TestResponse(
        [{ type: "text", text: "hello" }],
        format,
      );
      expect(() => response.parse()).toThrow(ParseError);
    });

    it("throws when partial parsing with OutputParser", () => {
      const format = createMockFormat({
        mode: "parser",
        outputParser: () => ({}),
      });
      const response = new TestResponse(
        [{ type: "text", text: "hello" }],
        format,
      );
      expect(() => response.parse({ partial: true })).toThrow(
        "parse({ partial: true }) is not supported with OutputParser",
      );
    });

    it("returns partial object when partial: true", () => {
      const format = createMockFormat();
      // Incomplete JSON
      const response = new TestResponse(
        [{ type: "text", text: '{"title": "Test' }],
        format,
      );
      const partial = response.parse({ partial: true });
      expect(partial).toEqual({ title: "Test" });
    });

    it("handles non-Error exceptions during JSON parsing", () => {
      const format = createMockFormat();
      const response = new TestResponse(
        [{ type: "text", text: "no json here at all" }],
        format,
      );
      expect(() => response.parse()).toThrow(ParseError);
    });

    it("unwraps non-object schema with toolSchemaUnwrapKey", () => {
      const ArraySchema = z.array(z.string());
      const format = createMockFormat({ validator: ArraySchema });
      // Override toolSchemaUnwrapKey to simulate a wrapped array
      (format as { toolSchemaUnwrapKey: string | null }).toolSchemaUnwrapKey =
        "output";

      const response = new TestResponse(
        [
          {
            type: "text",
            text: '{"output": ["apple", "banana", "cherry"]}',
          },
        ],
        format,
      );

      const result = response.parse();
      expect(result).toEqual(["apple", "banana", "cherry"]);
    });

    it("partial parse unwraps non-object schema with toolSchemaUnwrapKey", () => {
      const format = createMockFormat();
      (format as { toolSchemaUnwrapKey: string | null }).toolSchemaUnwrapKey =
        "output";

      const response = new TestResponse(
        [{ type: "text", text: '{"output": ["apple", "ban' }],
        format,
      );

      const partial = response.parse({ partial: true });
      expect(partial).toEqual(["apple", "ban"]);
    });

    it("partial parse returns null when unwrap key not yet present", () => {
      const format = createMockFormat();
      (format as { toolSchemaUnwrapKey: string | null }).toolSchemaUnwrapKey =
        "output";

      const response = new TestResponse([{ type: "text", text: "{" }], format);

      const partial = response.parse({ partial: true });
      expect(partial).toBeNull();
    });
  });
});
