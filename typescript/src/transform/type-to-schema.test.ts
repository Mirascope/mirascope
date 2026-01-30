/**
 * Tests for type-to-JSON-schema conversion.
 */

import ts from "typescript";
import { describe, it, expect } from "vitest";

import {
  typeToJsonSchema,
  typeToToolParameterSchema,
  createConversionContext,
} from "./type-to-schema";

/**
 * Minimal lib.d.ts definitions for testing.
 */
const LIB_DTS = `
interface Array<T> {
  length: number;
  [n: number]: T;
  push(...items: T[]): number;
}
interface ReadonlyArray<T> {
  readonly length: number;
  readonly [n: number]: T;
}
interface Boolean {}
interface String {}
interface Number {}
declare var Array: {
  new <T>(...items: T[]): T[];
  <T>(...items: T[]): T[];
};
`;

/**
 * Helper to create a TypeScript program from source code and get a type.
 */
function getTypeFromSource(
  source: string,
  typeName: string = "TestType",
  options: { noLib?: boolean } = {},
): { type: ts.Type; checker: ts.TypeChecker } {
  const fileName = "test.ts";
  const libFileName = "lib.d.ts";

  const sourceFile = ts.createSourceFile(
    fileName,
    source,
    ts.ScriptTarget.Latest,
    true,
  );

  const libFile = ts.createSourceFile(
    libFileName,
    LIB_DTS,
    ts.ScriptTarget.Latest,
    true,
  );

  const host: ts.CompilerHost = {
    getSourceFile: (name) => {
      if (name === fileName) return sourceFile;
      if (!options.noLib && (name === libFileName || name.includes("lib.")))
        return libFile;
      return undefined;
    },
    getDefaultLibFileName: () => libFileName,
    writeFile: () => {},
    getCurrentDirectory: () => "/",
    getCanonicalFileName: (f) => f,
    useCaseSensitiveFileNames: () => true,
    getNewLine: () => "\n",
    fileExists: (name) =>
      name === fileName || (!options.noLib && name === libFileName),
    readFile: () => undefined,
  };

  const program = ts.createProgram(
    [fileName],
    options.noLib ? { noLib: true } : { lib: ["lib.d.ts"], noLib: false },
    host,
  );
  const checker = program.getTypeChecker();

  // Find the type alias declaration
  let foundType: ts.Type | undefined;
  ts.forEachChild(sourceFile, (node) => {
    if (ts.isTypeAliasDeclaration(node) && node.name.text === typeName) {
      foundType = checker.getTypeAtLocation(node.name);
    }
  });

  if (!foundType) {
    throw new Error(`Type '${typeName}' not found in source`);
  }

  return { type: foundType, checker };
}

describe("typeToJsonSchema", () => {
  describe("primitive types", () => {
    it("converts string type", () => {
      const { type, checker } = getTypeFromSource("type TestType = string;");
      const ctx = createConversionContext(checker);
      const schema = typeToJsonSchema(type, ctx);
      expect(schema).toEqual({ type: "string" });
    });

    it("converts number type", () => {
      const { type, checker } = getTypeFromSource("type TestType = number;");
      const ctx = createConversionContext(checker);
      const schema = typeToJsonSchema(type, ctx);
      expect(schema).toEqual({ type: "number" });
    });

    it("converts boolean type", () => {
      const { type, checker } = getTypeFromSource("type TestType = boolean;");
      const ctx = createConversionContext(checker);
      const schema = typeToJsonSchema(type, ctx);
      // Boolean is a union of true | false in TypeScript
      expect(schema.type).toBe("boolean");
    });
  });

  describe("literal types", () => {
    it("converts string literal type", () => {
      const { type, checker } = getTypeFromSource('type TestType = "hello";');
      const ctx = createConversionContext(checker);
      const schema = typeToJsonSchema(type, ctx);
      expect(schema).toEqual({ type: "string", enum: ["hello"] });
    });

    it("converts number literal type", () => {
      const { type, checker } = getTypeFromSource("type TestType = 42;");
      const ctx = createConversionContext(checker);
      const schema = typeToJsonSchema(type, ctx);
      expect(schema).toEqual({ type: "number", enum: [42] });
    });

    it("converts true literal type", () => {
      const { type, checker } = getTypeFromSource("type TestType = true;");
      const ctx = createConversionContext(checker);
      const schema = typeToJsonSchema(type, ctx);
      expect(schema).toEqual({ type: "boolean", enum: [true] });
    });

    it("converts false literal type", () => {
      const { type, checker } = getTypeFromSource("type TestType = false;");
      const ctx = createConversionContext(checker);
      const schema = typeToJsonSchema(type, ctx);
      expect(schema).toEqual({ type: "boolean", enum: [false] });
    });
  });

  describe("union types", () => {
    it("converts string literal union to enum", () => {
      const { type, checker } = getTypeFromSource(
        'type TestType = "a" | "b" | "c";',
      );
      const ctx = createConversionContext(checker);
      const schema = typeToJsonSchema(type, ctx);
      expect(schema.type).toBe("string");
      expect(schema.enum).toContain("a");
      expect(schema.enum).toContain("b");
      expect(schema.enum).toContain("c");
    });

    it("converts number literal union to enum", () => {
      const { type, checker } = getTypeFromSource("type TestType = 1 | 2 | 3;");
      const ctx = createConversionContext(checker);
      const schema = typeToJsonSchema(type, ctx);
      expect(schema.type).toBe("number");
      expect(schema.enum).toContain(1);
      expect(schema.enum).toContain(2);
      expect(schema.enum).toContain(3);
    });

    it("handles optional type (T | undefined)", () => {
      const { type, checker } = getTypeFromSource(
        "type TestType = string | undefined;",
      );
      const ctx = createConversionContext(checker);
      const schema = typeToJsonSchema(type, ctx);
      expect(schema).toEqual({ type: "string" });
    });

    it("handles object | undefined union", () => {
      const { type, checker } = getTypeFromSource(
        "type TestType = { name: string } | undefined;",
      );
      const ctx = createConversionContext(checker);
      const schema = typeToJsonSchema(type, ctx);
      expect(schema.type).toBe("object");
      expect(schema.properties).toHaveProperty("name");
    });

    it("handles mixed union with oneOf", () => {
      const { type, checker } = getTypeFromSource(
        "type TestType = string | number;",
      );
      const ctx = createConversionContext(checker);
      const schema = typeToJsonSchema(type, ctx);
      expect(schema.oneOf).toBeDefined();
      expect(schema.oneOf).toHaveLength(2);
    });
  });

  describe("array types", () => {
    it("converts string array", () => {
      const { type, checker } = getTypeFromSource("type TestType = string[];");
      const ctx = createConversionContext(checker);
      const schema = typeToJsonSchema(type, ctx);
      expect(schema).toEqual({
        type: "array",
        items: { type: "string" },
      });
    });

    it("converts number array", () => {
      const { type, checker } = getTypeFromSource("type TestType = number[];");
      const ctx = createConversionContext(checker);
      const schema = typeToJsonSchema(type, ctx);
      expect(schema).toEqual({
        type: "array",
        items: { type: "number" },
      });
    });

    it("converts Array<T> syntax", () => {
      const { type, checker } = getTypeFromSource(
        "type TestType = Array<string>;",
      );
      const ctx = createConversionContext(checker);
      const schema = typeToJsonSchema(type, ctx);
      expect(schema).toEqual({
        type: "array",
        items: { type: "string" },
      });
    });

    it("converts nested array in object", () => {
      const { type, checker } = getTypeFromSource(
        "type TestType = { items: string[] };",
      );
      const ctx = createConversionContext(checker);
      const schema = typeToJsonSchema(type, ctx);
      expect(schema.type).toBe("object");
      expect(schema.properties?.items).toEqual({
        type: "array",
        items: { type: "string" },
      });
    });
  });

  describe("object types", () => {
    it("converts simple object type", () => {
      const { type, checker } = getTypeFromSource(
        "type TestType = { name: string; age: number; };",
      );
      const ctx = createConversionContext(checker);
      const schema = typeToJsonSchema(type, ctx);
      expect(schema.type).toBe("object");
      expect(schema.properties).toEqual({
        name: { type: "string" },
        age: { type: "number" },
      });
      expect(schema.required).toContain("name");
      expect(schema.required).toContain("age");
    });

    it("handles optional properties", () => {
      const { type, checker } = getTypeFromSource(
        "type TestType = { name: string; age?: number; };",
      );
      const ctx = createConversionContext(checker);
      const schema = typeToJsonSchema(type, ctx);
      expect(schema.type).toBe("object");
      expect(schema.properties).toHaveProperty("name");
      expect(schema.properties).toHaveProperty("age");
      expect(schema.required).toContain("name");
      expect(schema.required).not.toContain("age");
    });

    it("handles nested objects", () => {
      const { type, checker } = getTypeFromSource(
        "type TestType = { user: { name: string; }; };",
      );
      const ctx = createConversionContext(checker);
      const schema = typeToJsonSchema(type, ctx);
      expect(schema.type).toBe("object");
      expect(schema.properties?.user).toEqual({
        type: "object",
        properties: { name: { type: "string" } },
        required: ["name"],
      });
    });
  });
});

describe("typeToJsonSchema - additional types", () => {
  it("converts null type", () => {
    const { type, checker } = getTypeFromSource("type TestType = null;");
    const ctx = createConversionContext(checker);
    const schema = typeToJsonSchema(type, ctx);
    expect(schema).toEqual({ type: "null" });
  });

  it("converts undefined type", () => {
    const { type, checker } = getTypeFromSource("type TestType = undefined;");
    const ctx = createConversionContext(checker);
    const schema = typeToJsonSchema(type, ctx);
    expect(schema).toEqual({});
  });

  it("handles intersection of object types", () => {
    const { type, checker } = getTypeFromSource(
      "type A = { name: string }; type B = { age: number }; type TestType = A & B;",
    );
    const ctx = createConversionContext(checker);
    const schema = typeToJsonSchema(type, ctx);
    expect(schema.type).toBe("object");
    expect(schema.properties).toHaveProperty("name");
    expect(schema.properties).toHaveProperty("age");
    expect(schema.required).toContain("name");
    expect(schema.required).toContain("age");
  });

  it("handles intersection of non-object types", () => {
    const { type, checker } = getTypeFromSource(
      "type TestType = { name: string } & { age: number } & string;",
    );
    const ctx = createConversionContext(checker);
    const schema = typeToJsonSchema(type, ctx);
    // When mixed types in intersection, returns allOf
    expect(schema.allOf).toBeDefined();
  });

  it("handles object with no required properties", () => {
    const { type, checker } = getTypeFromSource(
      "type TestType = { name?: string; age?: number };",
    );
    const ctx = createConversionContext(checker);
    const schema = typeToJsonSchema(type, ctx);
    expect(schema.type).toBe("object");
    expect(schema.properties).toHaveProperty("name");
    expect(schema.properties).toHaveProperty("age");
    expect(schema.required).toBeUndefined();
  });

  it("handles ReadonlyArray<T>", () => {
    const { type, checker } = getTypeFromSource(
      "type TestType = ReadonlyArray<number>;",
    );
    const ctx = createConversionContext(checker);
    const schema = typeToJsonSchema(type, ctx);
    expect(schema).toEqual({
      type: "array",
      items: { type: "number" },
    });
  });
});

describe("typeToToolParameterSchema", () => {
  it("converts object type to ToolParameterSchema", () => {
    const { type, checker } = getTypeFromSource(
      'type TestType = { city: string; units?: "celsius" | "fahrenheit"; };',
    );
    const schema = typeToToolParameterSchema(type, checker);

    expect(schema.type).toBe("object");
    expect(schema.additionalProperties).toBe(false);
    expect(schema.properties.city).toEqual({ type: "string" });
    expect(schema.properties.units?.type).toBe("string");
    expect(schema.properties.units?.enum).toContain("celsius");
    expect(schema.properties.units?.enum).toContain("fahrenheit");
    expect(schema.required).toContain("city");
    expect(schema.required).not.toContain("units");
  });

  it("throws error for non-object types", () => {
    const { type, checker } = getTypeFromSource("type TestType = string;");
    expect(() => typeToToolParameterSchema(type, checker)).toThrow(
      "Tool parameter type must be an object type",
    );
  });
});

describe("JSDoc extraction", () => {
  it("extracts JSDoc comments as property descriptions", () => {
    const { type, checker } = getTypeFromSource(`
      type TestType = {
        /** The city to get weather for */
        city: string;
        /** Temperature units */
        units: string;
      };
    `);
    const ctx = createConversionContext(checker);
    const schema = typeToJsonSchema(type, ctx);

    expect(schema.properties?.city?.description).toBe(
      "The city to get weather for",
    );
    expect(schema.properties?.units?.description).toBe("Temperature units");
  });

  it("extracts multi-line JSDoc comments", () => {
    const { type, checker } = getTypeFromSource(`
      type TestType = {
        /**
         * The search query to execute.
         * Supports full-text search syntax.
         */
        query: string;
      };
    `);
    const ctx = createConversionContext(checker);
    const schema = typeToJsonSchema(type, ctx);

    // Multi-line JSDoc gets combined
    expect(schema.properties?.query?.description).toContain("search query");
  });

  it("handles properties without JSDoc comments", () => {
    const { type, checker } = getTypeFromSource(`
      type TestType = {
        /** Has a description */
        documented: string;
        noDoc: number;
      };
    `);
    const ctx = createConversionContext(checker);
    const schema = typeToJsonSchema(type, ctx);

    expect(schema.properties?.documented?.description).toBe(
      "Has a description",
    );
    expect(schema.properties?.noDoc?.description).toBeUndefined();
  });

  it("extracts JSDoc from nested objects", () => {
    const { type, checker } = getTypeFromSource(`
      type TestType = {
        /** The user object */
        user: {
          /** The user's name */
          name: string;
        };
      };
    `);
    const ctx = createConversionContext(checker);
    const schema = typeToJsonSchema(type, ctx);

    expect(schema.properties?.user?.description).toBe("The user object");
    // Nested properties also get descriptions
    const userProps = schema.properties?.user?.properties;
    expect(userProps?.name?.description).toBe("The user's name");
  });

  it("extracts JSDoc descriptions in ToolParameterSchema", () => {
    const { type, checker } = getTypeFromSource(`
      type TestType = {
        /** The city name */
        city: string;
        /** Optional count */
        count?: number;
      };
    `);
    const schema = typeToToolParameterSchema(type, checker);

    expect(schema.properties.city?.description).toBe("The city name");
    expect(schema.properties.count?.description).toBe("Optional count");
  });
});
