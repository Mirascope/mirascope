/**
 * Tests for Format class and utilities.
 */

import { describe, it, expect } from "vitest";
import { z } from "zod";

import type { FormatSpec } from "./types";

import {
  FORMAT_TOOL_NAME,
  TOOL_MODE_INSTRUCTIONS,
  JSON_MODE_INSTRUCTIONS,
  FORMAT_TYPE,
  defineFormat,
  resolveFormat,
  isFormat,
} from "./format";
import { defineOutputParser } from "./output-parser";

// Mock Zod schema for testing
const BookSchema = z.object({
  title: z.string().describe("The title of the book"),
  author: z.string().describe("The author of the book"),
});

describe("FORMAT_TOOL_NAME", () => {
  it("is a string constant", () => {
    expect(typeof FORMAT_TOOL_NAME).toBe("string");
    expect(FORMAT_TOOL_NAME).toBe("__mirascope_formatted_output_tool__");
  });
});

describe("TOOL_MODE_INSTRUCTIONS", () => {
  it("contains the format tool name", () => {
    expect(TOOL_MODE_INSTRUCTIONS).toContain(FORMAT_TOOL_NAME);
  });
});

describe("JSON_MODE_INSTRUCTIONS", () => {
  it("contains placeholder for JSON schema", () => {
    expect(JSON_MODE_INSTRUCTIONS).toContain("{json_schema}");
  });
});

describe("isFormat", () => {
  it("returns true for Format objects", () => {
    const format = defineFormat<{ title: string }>({
      mode: "tool",
      validator: BookSchema,
    });
    expect(isFormat(format)).toBe(true);
  });

  it("returns false for non-Format objects", () => {
    expect(isFormat(null)).toBe(false);
    expect(isFormat(undefined)).toBe(false);
    expect(isFormat({})).toBe(false);
    expect(isFormat({ __formatType: "wrong" })).toBe(false);
    expect(isFormat("string")).toBe(false);
    expect(isFormat(123)).toBe(false);
  });
});

describe("defineFormat", () => {
  describe("with Zod schema validator", () => {
    it("creates a Format with tool mode", () => {
      const format = defineFormat<{ title: string; author: string }>({
        mode: "tool",
        validator: BookSchema,
      });

      expect(format.__formatType).toBe(FORMAT_TYPE);
      expect(format.mode).toBe("tool");
      expect(format.validator).toBe(BookSchema);
      expect(format.outputParser).toBeNull();
      expect(format.formattingInstructions).toBe(TOOL_MODE_INSTRUCTIONS);
    });

    it("creates a Format with json mode", () => {
      const format = defineFormat<{ title: string; author: string }>({
        mode: "json",
        validator: BookSchema,
      });

      expect(format.mode).toBe("json");
      expect(format.formattingInstructions).toContain(
        "Respond only with valid JSON",
      );
    });

    it("creates a Format with strict mode", () => {
      const format = defineFormat<{ title: string; author: string }>({
        mode: "strict",
        validator: BookSchema,
      });

      expect(format.mode).toBe("strict");
      expect(format.formattingInstructions).toBeNull();
    });

    it("creates a tool schema with format tool name", () => {
      const format = defineFormat<{ title: string; author: string }>({
        mode: "tool",
        validator: BookSchema,
      });

      const toolSchema = format.createToolSchema();
      expect(toolSchema.name).toContain(FORMAT_TOOL_NAME);
      expect(toolSchema.parameters).toBeDefined();
    });

    it("includes description in tool schema when set", () => {
      const DescribedSchema = z
        .object({
          title: z.string(),
        })
        .describe("A book with just a title");

      const format = defineFormat<{ title: string }>({
        mode: "tool",
        validator: DescribedSchema,
      });

      const toolSchema = format.createToolSchema();
      expect(toolSchema.description).toContain("A book with just a title");
    });
  });

  describe("createToolSchema with $defs", () => {
    it("includes $defs in parameters when present", () => {
      interface Data {
        value: string;
      }

      const format = defineFormat<Data>({
        mode: "tool",
        __schema: {
          type: "object",
          properties: {
            value: { $ref: "#/$defs/CustomType" },
          },
          required: ["value"],
          additionalProperties: false,
          $defs: {
            CustomType: { type: "string" },
          },
        },
      });
      const toolSchema = format.createToolSchema();

      expect(toolSchema.parameters.$defs).toEqual({
        CustomType: { type: "string" },
      });
    });
  });

  describe("error handling", () => {
    it("throws when options has no __schema and no validator", () => {
      // Build options dynamically to bypass the compile-time transformer
      const options = { mode: "tool" as const };
      expect(() => defineFormat<{ title: string }>(options)).toThrow(
        "Format specification is missing schema",
      );
    });
  });
});

describe("defineFormat with __schema (transformer-injected)", () => {
  it("creates Format with injected __schema", () => {
    interface Book {
      title: string;
      author: string;
    }

    const format = defineFormat<Book>({
      mode: "tool",
      __schema: {
        type: "object",
        title: "Book",
        properties: {
          title: { type: "string" },
          author: { type: "string" },
        },
        required: ["title", "author"],
        additionalProperties: false,
      },
    });

    expect(format.mode).toBe("tool");
    expect(format.name).toBe("Book");
    expect(format.schema.properties).toHaveProperty("title");
    expect(format.schema.properties).toHaveProperty("author");
  });

  it("uses default name when __schema has no title", () => {
    interface Data {
      value: number;
    }

    const format = defineFormat<Data>({
      mode: "tool",
      __schema: {
        type: "object",
        properties: {
          value: { type: "number" },
        },
        required: ["value"],
        additionalProperties: false,
      },
    });

    expect(format.name).toBe("FormattedOutput");
  });

  it("allows optional validator alongside __schema", () => {
    const ValidatorSchema = z.object({
      title: z.string(),
    });

    const schemaObj = {
      type: "object" as const,
      properties: {
        title: { type: "string" },
      },
      required: ["title"],
      additionalProperties: false as const,
    };

    const format = defineFormat<{ title: string }>({
      mode: "json",
      __schema: schemaObj,
      validator: ValidatorSchema,
    });

    expect(format.mode).toBe("json");
    expect(format.validator).toBe(ValidatorSchema);
    expect(format.schema).toEqual(schemaObj);
  });
});

describe("Zod schema with descriptions", () => {
  it("extracts description from Zod schema for name", () => {
    const SchemaWithDesc = z
      .object({
        title: z.string(),
      })
      .describe("A book");

    const format = defineFormat<{ title: string }>({
      mode: "tool",
      validator: SchemaWithDesc,
    });

    // Description affects the name extraction (first word)
    expect(format.name).toBe("A");
  });

  it("uses FormattedOutput when first word is too long", () => {
    const SchemaWithLongDesc = z
      .object({
        title: z.string(),
      })
      .describe(
        "ThisIsAReallyLongFirstWordThatExceeds30Characters and more words",
      );

    const format = defineFormat<{ title: string }>({
      mode: "tool",
      validator: SchemaWithLongDesc,
    });

    // Long first word gets skipped, falls back to FormattedOutput
    expect(format.name).toBe("FormattedOutput");
  });

  it("uses FormattedOutput when no description", () => {
    const SchemaNoDesc = z.object({
      title: z.string(),
    });

    const format = defineFormat<{ title: string }>({
      mode: "tool",
      validator: SchemaNoDesc,
    });

    expect(format.name).toBe("FormattedOutput");
  });

  it("extracts description from Zod 3 style _def.description", () => {
    // Create a mock Zod-like object with _def.description
    const mockZodSchema = {
      _def: {
        typeName: "ZodObject",
        description: "MyModel",
        shape: () => ({
          field: {
            _def: { typeName: "ZodString" },
          },
        }),
      },
      safeParse: () => ({ success: true, data: {} }),
    };

    // This tests the Zod 3 fallback path for description
    const format = defineFormat<{ field: string }>({
      mode: "tool",
      validator: mockZodSchema,
    });

    expect(format.name).toBe("MyModel");
  });

  it("handles wrapped types (optional) in Zod schema", () => {
    // Create a mock Zod-like object with an optional field (has innerType)
    const mockZodSchema = {
      _def: {
        typeName: "ZodObject",
        shape: () => ({
          optionalField: {
            _def: {
              typeName: "ZodOptional",
              description: "An optional field",
              innerType: {
                _def: { typeName: "ZodString" },
              },
            },
          },
        }),
      },
      safeParse: () => ({ success: true, data: {} }),
    };

    const format = defineFormat<{ optionalField?: string }>({
      mode: "tool",
      validator: mockZodSchema,
    });

    // The optional field should not be in required and should have the inner type's type
    expect(format.schema.required).not.toContain("optionalField");
    const props = format.schema.properties as Record<string, { type?: string }>;
    expect(props.optionalField?.type).toBe("string");
  });
});

describe("resolveFormat", () => {
  it("returns null for null input", () => {
    expect(resolveFormat(null, "tool")).toBeNull();
  });

  it("returns null for undefined input", () => {
    expect(resolveFormat(undefined, "tool")).toBeNull();
  });

  it("passes through Format objects", () => {
    const format = defineFormat<{ title: string; author: string }>({
      mode: "tool",
      validator: BookSchema,
    });

    const resolved = resolveFormat(format, "json");

    // Should pass through unchanged (keeps original mode)
    expect(resolved).toBe(format);
    expect(resolved?.mode).toBe("tool");
  });

  it("creates Format from Zod schema", () => {
    const resolved = resolveFormat(BookSchema, "json");

    expect(resolved).not.toBeNull();
    expect(resolved?.mode).toBe("json");
    expect(resolved?.validator).toBe(BookSchema);
  });

  it("creates Format from OutputParser", () => {
    const parser = defineOutputParser<{ title: string }>({
      formattingInstructions: "Return JSON",
      parser: (response) => ({ title: response.text() }),
    });

    const resolved = resolveFormat(parser, "tool");

    expect(resolved).not.toBeNull();
    expect(resolved?.mode).toBe("parser");
    expect(resolved?.outputParser).toBe(parser);
    expect(resolved?.formattingInstructions).toBe("Return JSON");
  });

  it("creates Format from FormatSpec with validator", () => {
    const spec: FormatSpec<{ title: string; author: string }> = {
      validator: BookSchema,
    };

    const resolved = resolveFormat(spec, "json");

    expect(resolved).not.toBeNull();
    expect(resolved?.mode).toBe("json");
    expect(resolved?.validator).toBe(BookSchema);
  });

  it("creates Format from FormatSpec with __schema", () => {
    const spec: FormatSpec<{ title: string }> = {
      __schema: {
        type: "object",
        properties: {
          title: { type: "string" },
        },
        required: ["title"],
        additionalProperties: false,
      },
    };

    const resolved = resolveFormat(spec, "json");

    expect(resolved).not.toBeNull();
    expect(resolved?.mode).toBe("json");
  });

  it("throws for empty object (not recognized as FormatSpec)", () => {
    // An empty object is not a valid FormatSpec (must have validator, __schema, or schema)
    // resolveFormat will not recognize it and throw "Unknown format type"
    const spec: FormatSpec<{ title: string }> = {};

    expect(() => resolveFormat(spec, "tool")).toThrow("Unknown format type");
  });

  it("throws for FormatSpec with schema but no __schema or validator", () => {
    // This tests the error path in resolveFormat where isFormatSpec returns true
    // but there's no __schema or validator
    const spec = { schema: {} }; // has schema but no __schema or validator

    expect(() => resolveFormat(spec, "tool")).toThrow(
      "Format specification is missing __schema",
    );
  });
});
