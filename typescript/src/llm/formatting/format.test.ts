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
  extractSchemaFromZod,
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

  it("handles array types with items in Zod 3 schema", () => {
    // Create a mock Zod-like object with an array field (Zod 3 style)
    const mockZodSchema = {
      _def: {
        typeName: "ZodObject",
        shape: () => ({
          numbers: {
            _def: {
              typeName: "ZodArray",
              description: "A list of numbers",
              type: {
                _def: { typeName: "ZodNumber" },
              },
            },
          },
        }),
      },
      safeParse: () => ({ success: true, data: {} }),
    };

    const format = defineFormat<{ numbers: number[] }>({
      mode: "tool",
      validator: mockZodSchema,
    });

    // The array field should have type "array" and items with type "number"
    const props = format.schema.properties as Record<
      string,
      { type?: string; items?: { type?: string } }
    >;
    expect(props.numbers?.type).toBe("array");
    expect(props.numbers?.items?.type).toBe("number");
  });

  it("handles array types with real Zod schema", () => {
    // Use a real Zod schema to test the actual behavior
    const SchemaWithArray = z.object({
      numbers: z.array(z.number()).describe("A list of numbers"),
    });

    const format = defineFormat<{ numbers: number[] }>({
      mode: "tool",
      validator: SchemaWithArray,
    });

    // The array field should have type "array" and items
    const props = format.schema.properties as Record<
      string,
      { type?: string; items?: { type?: string } }
    >;
    expect(props.numbers?.type).toBe("array");
    expect(props.numbers?.items).toBeDefined();
    expect(props.numbers?.items?.type).toBe("number");
  });
});

describe("non-object schema wrapping", () => {
  it("wraps z.array() in object with output key", () => {
    const ArraySchema = z.array(z.string());
    const { schema, unwrapKey } = extractSchemaFromZod(ArraySchema);

    expect(unwrapKey).toBe("output");
    expect(schema.type).toBe("object");
    expect(schema.properties).toHaveProperty("output");
    expect(schema.required).toEqual(["output"]);

    const outputProp = (schema.properties as Record<string, { type?: string }>)
      .output;
    expect(outputProp?.type).toBe("array");
  });

  it("does NOT wrap z.object() — unwrapKey is null", () => {
    const { schema, unwrapKey } = extractSchemaFromZod(BookSchema);

    expect(unwrapKey).toBeNull();
    expect(schema.type).toBe("object");
    expect(schema.properties).toHaveProperty("title");
    expect(schema.properties).toHaveProperty("author");
  });

  it("resolveFormat sets toolSchemaUnwrapKey for array schemas", () => {
    const ArraySchema = z.array(z.string());
    const format = resolveFormat(ArraySchema, "tool");

    expect(format).not.toBeNull();
    expect(format!.toolSchemaUnwrapKey).toBe("output");
  });

  it("resolveFormat sets toolSchemaUnwrapKey to null for object schemas", () => {
    const format = resolveFormat(BookSchema, "tool");

    expect(format).not.toBeNull();
    expect(format!.toolSchemaUnwrapKey).toBeNull();
  });

  it("createToolSchema wraps non-object schema in tool parameters", () => {
    const ArraySchema = z.array(z.string());
    const format = resolveFormat(ArraySchema, "tool");

    const toolSchema = format!.createToolSchema();
    expect(toolSchema.parameters.properties).toHaveProperty("output");
    expect(toolSchema.parameters.required).toEqual(["output"]);
  });

  it("wraps Zod 3 mock non-object schema", () => {
    // Mock a Zod 3-style array schema (no toJSONSchema)
    const mockArraySchema = {
      _def: {
        typeName: "ZodArray",
        type: {
          _def: { typeName: "ZodString" },
        },
      },
      safeParse: () => ({ success: true, data: [] }),
    };

    const { schema, unwrapKey } = extractSchemaFromZod(mockArraySchema);

    expect(unwrapKey).toBe("output");
    expect(schema.type).toBe("object");
    expect(schema.properties).toHaveProperty("output");
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
