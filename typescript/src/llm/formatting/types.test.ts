/**
 * Tests for formatting types and type guards.
 */

import { describe, it, expect } from "vitest";
import { z } from "zod";

import type { FormatSpec } from "./types";

import { isZodSchema, isFormatSpec } from "./types";

describe("isZodSchema", () => {
  describe("valid Zod schemas", () => {
    it("returns true for z.object()", () => {
      const schema = z.object({ title: z.string() });
      expect(isZodSchema(schema)).toBe(true);
    });

    it("returns true for z.string()", () => {
      const schema = z.string();
      expect(isZodSchema(schema)).toBe(true);
    });

    it("returns true for z.number()", () => {
      const schema = z.number();
      expect(isZodSchema(schema)).toBe(true);
    });

    it("returns true for z.array()", () => {
      const schema = z.array(z.string());
      expect(isZodSchema(schema)).toBe(true);
    });

    it("returns true for z.union()", () => {
      const schema = z.union([z.string(), z.number()]);
      expect(isZodSchema(schema)).toBe(true);
    });

    it("returns true for complex nested schema", () => {
      const schema = z.object({
        book: z.object({
          title: z.string(),
          author: z.object({
            name: z.string(),
            age: z.number().optional(),
          }),
        }),
        tags: z.array(z.string()),
      });
      expect(isZodSchema(schema)).toBe(true);
    });
  });

  describe("non-Zod values", () => {
    it("returns false for null", () => {
      expect(isZodSchema(null)).toBe(false);
    });

    it("returns false for undefined", () => {
      expect(isZodSchema(undefined)).toBe(false);
    });

    it("returns false for plain objects", () => {
      expect(isZodSchema({})).toBe(false);
      expect(isZodSchema({ title: "string" })).toBe(false);
    });

    it("returns false for objects with _def but wrong structure", () => {
      expect(isZodSchema({ _def: {} })).toBe(false);
      expect(isZodSchema({ _def: "string" })).toBe(false);
    });

    it("returns false for primitive types", () => {
      expect(isZodSchema("string")).toBe(false);
      expect(isZodSchema(123)).toBe(false);
      expect(isZodSchema(true)).toBe(false);
    });

    it("returns false for arrays", () => {
      expect(isZodSchema([])).toBe(false);
      expect(isZodSchema(["a", "b"])).toBe(false);
    });

    it("returns false for functions", () => {
      expect(isZodSchema(() => {})).toBe(false);
      expect(isZodSchema(function test() {})).toBe(false);
    });
  });
});

describe("isFormatSpec", () => {
  describe("valid FormatSpec objects", () => {
    it("returns false for empty object (must have validator, __schema, or schema)", () => {
      // An empty object is not a valid FormatSpec
      // It must have at least one of validator, __schema, or schema
      const spec: FormatSpec<unknown> = {};
      expect(isFormatSpec(spec)).toBe(false);
    });

    it("returns true for object with validator", () => {
      const spec: FormatSpec<{ title: string }> = {
        validator: z.object({ title: z.string() }),
      };
      expect(isFormatSpec(spec)).toBe(true);
    });

    it("returns true for object with __schema", () => {
      const spec: FormatSpec<{ title: string }> = {
        __schema: {
          type: "object",
          properties: { title: { type: "string" } },
          required: ["title"],
          additionalProperties: false,
        },
      };
      expect(isFormatSpec(spec)).toBe(true);
    });

    it("returns true for object with both validator and __schema", () => {
      const spec: FormatSpec<{ title: string }> = {
        validator: z.object({ title: z.string() }),
        __schema: {
          type: "object",
          properties: { title: { type: "string" } },
          required: ["title"],
          additionalProperties: false,
        },
      };
      expect(isFormatSpec(spec)).toBe(true);
    });
  });

  describe("non-FormatSpec values", () => {
    it("returns false for null", () => {
      expect(isFormatSpec(null)).toBe(false);
    });

    it("returns false for undefined", () => {
      expect(isFormatSpec(undefined)).toBe(false);
    });

    it("returns false for Zod schemas", () => {
      const schema = z.object({ title: z.string() });
      expect(isFormatSpec(schema)).toBe(false);
    });

    it("returns false for primitive types", () => {
      expect(isFormatSpec("string")).toBe(false);
      expect(isFormatSpec(123)).toBe(false);
      expect(isFormatSpec(true)).toBe(false);
    });

    it("returns false for arrays", () => {
      expect(isFormatSpec([])).toBe(false);
      expect(isFormatSpec([{ title: "test" }])).toBe(false);
    });

    it("returns false for functions", () => {
      expect(isFormatSpec(() => {})).toBe(false);
    });
  });
});
