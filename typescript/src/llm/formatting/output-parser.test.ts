/**
 * Tests for OutputParser utilities.
 */

import { describe, it, expect } from "vitest";

import type { AnyResponse } from "./output-parser";

import {
  OUTPUT_PARSER_TYPE,
  defineOutputParser,
  isOutputParser,
} from "./output-parser";

// Mock response for testing
const createMockResponse = (text: string): AnyResponse =>
  ({
    text: () => text,
    texts: [{ type: "text", text }],
    content: [{ type: "text", text }],
  }) as unknown as AnyResponse;

describe("OUTPUT_PARSER_TYPE", () => {
  it("is a symbol", () => {
    expect(typeof OUTPUT_PARSER_TYPE).toBe("symbol");
  });
});

describe("defineOutputParser", () => {
  it("creates an OutputParser from args", () => {
    const parser = defineOutputParser<{ title: string }>({
      formattingInstructions: "Return JSON",
      parser: (response) => ({ title: response.text() }),
    });

    expect(parser.__outputParserType).toBe(OUTPUT_PARSER_TYPE);
    expect(parser.formattingInstructions).toBe("Return JSON");
    expect(typeof parser).toBe("function");
  });

  it("OutputParser is callable and returns parsed result", () => {
    const parser = defineOutputParser<{ title: string }>({
      formattingInstructions: "Return JSON",
      parser: (response) => ({ title: response.text() }),
    });

    const response = createMockResponse("Test Title");
    const result = parser(response);

    expect(result).toEqual({ title: "Test Title" });
  });

  it("uses parser function name as name", () => {
    const myCustomParser = function namedParser(response: AnyResponse) {
      return { title: response.text() };
    };

    const parser = defineOutputParser<{ title: string }>({
      formattingInstructions: "Return JSON",
      parser: myCustomParser,
    });

    expect(parser.name).toBe("namedParser");
  });

  it("uses default name for anonymous functions", () => {
    // Note: When an arrow function is assigned to an object property,
    // its name becomes the property name ('parser'), not empty string
    const parser = defineOutputParser<{ title: string }>({
      formattingInstructions: "Return JSON",
      parser: (response) => ({ title: response.text() }),
    });

    // The arrow function gets name 'parser' from the property assignment
    expect(parser.name).toBe("parser");
  });

  it("preserves formattingInstructions", () => {
    const instructions = `
      Return the data as XML format:
      <book>
        <title>Book Title</title>
        <author>Author Name</author>
      </book>
    `;

    const parser = defineOutputParser<{ title: string; author: string }>({
      formattingInstructions: instructions,
      parser: () => ({ title: "Test", author: "Test" }),
    });

    expect(parser.formattingInstructions).toBe(instructions);
  });

  it("allows complex parsing logic", () => {
    const xmlParser = defineOutputParser<{ title: string; author: string }>({
      formattingInstructions: "Return XML",
      parser: (response) => {
        const text = response.text();
        const titleMatch = text.match(/<title>([^<]+)<\/title>/);
        const authorMatch = text.match(/<author>([^<]+)<\/author>/);
        return {
          title: titleMatch?.[1] ?? "",
          author: authorMatch?.[1] ?? "",
        };
      },
    });

    const response = createMockResponse(
      "<book><title>1984</title><author>Orwell</author></book>",
    );
    const result = xmlParser(response);

    expect(result).toEqual({ title: "1984", author: "Orwell" });
  });
});

describe("isOutputParser", () => {
  it("returns true for OutputParser objects", () => {
    const parser = defineOutputParser<{ title: string }>({
      formattingInstructions: "Return JSON",
      parser: (response) => ({ title: response.text() }),
    });

    expect(isOutputParser(parser)).toBe(true);
  });

  it("returns false for null", () => {
    expect(isOutputParser(null)).toBe(false);
  });

  it("returns false for undefined", () => {
    expect(isOutputParser(undefined)).toBe(false);
  });

  it("returns false for plain objects", () => {
    expect(isOutputParser({})).toBe(false);
    expect(isOutputParser({ __outputParserType: OUTPUT_PARSER_TYPE })).toBe(
      false,
    );
  });

  it("returns false for regular functions", () => {
    expect(isOutputParser(() => {})).toBe(false);
    expect(
      isOutputParser(function regularFunc() {
        return {};
      }),
    ).toBe(false);
  });

  it("returns false for objects with wrong symbol", () => {
    const fake = Object.assign(() => {}, {
      __outputParserType: Symbol("fake"),
    });
    expect(isOutputParser(fake)).toBe(false);
  });

  it("returns false for primitive types", () => {
    expect(isOutputParser("string")).toBe(false);
    expect(isOutputParser(123)).toBe(false);
    expect(isOutputParser(true)).toBe(false);
  });

  it("narrows type correctly (type guard)", () => {
    const maybeParser: unknown = defineOutputParser<{ title: string }>({
      formattingInstructions: "Return JSON",
      parser: (response) => ({ title: response.text() }),
    });

    if (isOutputParser(maybeParser)) {
      // TypeScript should allow these accesses after type narrowing
      expect(maybeParser.formattingInstructions).toBe("Return JSON");
      expect(typeof maybeParser).toBe("function");
    } else {
      throw new Error("Should be an OutputParser");
    }
  });
});
