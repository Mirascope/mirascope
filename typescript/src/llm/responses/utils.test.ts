/**
 * Tests for response parsing utilities.
 */

import { describe, it, expect } from "vitest";
import { z } from "zod";

import { extractSerializedJson, parsePartial } from "./utils";

describe("extractSerializedJson", () => {
  describe("valid JSON extraction", () => {
    it("extracts plain JSON object", () => {
      const text = '{"title": "1984", "author": "Orwell"}';
      expect(extractSerializedJson(text)).toBe(text);
    });

    it("extracts JSON with preamble text", () => {
      const text =
        'Here is the book:\n{"title": "1984", "author": "Orwell"}\nHope this helps!';
      expect(extractSerializedJson(text)).toBe(
        '{"title": "1984", "author": "Orwell"}',
      );
    });

    it("extracts JSON from markdown code block", () => {
      const text = '```json\n{"title": "1984"}\n```';
      expect(extractSerializedJson(text)).toBe('{"title": "1984"}');
    });

    it("extracts JSON from code block with preamble", () => {
      const text =
        'Here is the JSON:\n```json\n{"title": "1984"}\n```\nAll done!';
      expect(extractSerializedJson(text)).toBe('{"title": "1984"}');
    });

    it("handles nested objects", () => {
      const json = '{"book": {"title": "1984", "author": {"name": "Orwell"}}}';
      const text = `Some preamble\n${json}\nTrailing text`;
      expect(extractSerializedJson(text)).toBe(json);
    });

    it("handles arrays in objects", () => {
      const json = '{"titles": ["1984", "Animal Farm"]}';
      expect(extractSerializedJson(json)).toBe(json);
    });

    it("handles strings with braces inside", () => {
      const json = '{"text": "Hello {world}!"}';
      expect(extractSerializedJson(json)).toBe(json);
    });

    it("handles escaped quotes in strings", () => {
      const json = '{"text": "He said \\"Hello\\""}';
      expect(extractSerializedJson(json)).toBe(json);
    });

    it("handles unicode escapes", () => {
      const json = '{"emoji": "\\u2764"}';
      expect(extractSerializedJson(json)).toBe(json);
    });

    it("handles newlines in strings", () => {
      const json = '{"text": "line1\\nline2"}';
      expect(extractSerializedJson(json)).toBe(json);
    });
  });

  describe("error cases", () => {
    it("throws for missing opening brace", () => {
      expect(() => extractSerializedJson("No JSON here")).toThrow(
        "No JSON object found in response: missing '{'",
      );
    });

    it("throws for empty string", () => {
      expect(() => extractSerializedJson("")).toThrow(
        "No JSON object found in response: missing '{'",
      );
    });

    it("throws for unclosed object", () => {
      expect(() => extractSerializedJson('{"title": "1984"')).toThrow(
        "No JSON object found in response: missing '}'",
      );
    });

    it("throws for mismatched braces", () => {
      expect(() => extractSerializedJson('{"title": "1984"}}')).not.toThrow(); // Only extracts first complete object
    });
  });
});

describe("parsePartial", () => {
  describe("complete JSON", () => {
    it("parses complete JSON object", () => {
      const result = parsePartial<{ title: string }>('{"title": "1984"}');
      expect(result).toEqual({ title: "1984" });
    });

    it("parses complete JSON with preamble", () => {
      const result = parsePartial<{ title: string }>(
        'Here is the JSON:\n{"title": "1984"}',
      );
      expect(result).toEqual({ title: "1984" });
    });
  });

  describe("incomplete JSON (streaming)", () => {
    it("parses incomplete object with partial string", () => {
      const result = parsePartial<{ title: string }>('{"title": "19');
      expect(result).toEqual({ title: "19" });
    });

    it("parses incomplete object with complete field", () => {
      const result = parsePartial<{ title: string; author: string }>(
        '{"title": "1984", "au',
      );
      expect(result).toEqual({ title: "1984" });
    });

    it("parses incomplete nested object", () => {
      const result = parsePartial<{ book: { title: string } }>(
        '{"book": {"title": "19',
      );
      expect(result).toEqual({ book: { title: "19" } });
    });

    it("returns null for no opening brace", () => {
      expect(parsePartial("Some text without JSON")).toBeNull();
    });

    it("returns null for empty string", () => {
      expect(parsePartial("")).toBeNull();
    });
  });

  describe("with Zod validator", () => {
    const BookSchema = z.object({
      title: z.string(),
      author: z.string(),
    });

    it("validates complete JSON against schema", () => {
      const result = parsePartial<{ title: string; author: string }>(
        '{"title": "1984", "author": "Orwell"}',
        BookSchema,
      );
      expect(result).toEqual({ title: "1984", author: "Orwell" });
    });

    it("still returns partial data even if validation fails", () => {
      // Partial data won't have all required fields, but we still return it
      const result = parsePartial<{ title: string; author: string }>(
        '{"title": "1984"}',
        BookSchema,
      );
      expect(result).toEqual({ title: "1984" });
    });

    it("returns parsed data without validation when no validator", () => {
      const result = parsePartial<{ title: string }>(
        '{"title": "1984", "extra": "field"}',
      );
      expect(result).toEqual({ title: "1984", extra: "field" });
    });
  });

  describe("edge cases", () => {
    it("handles markdown code blocks", () => {
      const result = parsePartial<{ title: string }>(
        '```json\n{"title": "1984"}\n```',
      );
      expect(result).toEqual({ title: "1984" });
    });

    it("handles deeply nested structures", () => {
      const result = parsePartial<{
        level1: { level2: { level3: { value: string } } };
      }>('{"level1": {"level2": {"level3": {"value": "deep"}}}}');
      expect(result).toEqual({
        level1: { level2: { level3: { value: "deep" } } },
      });
    });

    it("handles arrays", () => {
      const result = parsePartial<{ items: string[] }>(
        '{"items": ["a", "b", "c"]}',
      );
      expect(result).toEqual({ items: ["a", "b", "c"] });
    });

    it("handles incomplete arrays", () => {
      const result = parsePartial<{ items: string[] }>('{"items": ["a", "b');
      expect(result).toEqual({ items: ["a", "b"] });
    });
  });
});
