/**
 * Tests for the TypeScript transformer.
 */

import ts from "typescript";
import { describe, it, expect } from "vitest";

import { createToolSchemaTransformer } from "./transformer";
import transformer from "./transformer";

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
 * Helper to transform source code and get the result.
 */
function transformSource(source: string): string {
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
      if (name === libFileName || name.includes("lib.")) return libFile;
      return undefined;
    },
    getDefaultLibFileName: () => libFileName,
    writeFile: () => {},
    getCurrentDirectory: () => "/",
    getCanonicalFileName: (f) => f,
    useCaseSensitiveFileNames: () => true,
    getNewLine: () => "\n",
    fileExists: (name) => name === fileName || name === libFileName,
    readFile: () => undefined,
  };

  const program = ts.createProgram(
    [fileName],
    { lib: ["lib.d.ts"], noLib: false },
    host,
  );
  const transformer = createToolSchemaTransformer(program);

  const result = ts.transform(sourceFile, [transformer]);
  const transformedSourceFile = result.transformed[0]!;

  const printer = ts.createPrinter();
  return printer.printFile(transformedSourceFile);
}

describe("createToolSchemaTransformer", () => {
  it("injects __schema for defineTool with simple type", () => {
    const source = `const tool = defineTool<{ city: string }>({
  name: "get_weather",
  description: "Get weather",
  tool: ({ city }) => ({ temp: 72 }),
});`;

    expect(transformSource(source)).toMatchInlineSnapshot(`
      "const tool = defineTool<{
          city: string;
      }>({
          name: "get_weather",
          description: "Get weather",
          tool: ({ city }) => ({ temp: 72 }),
          __schema: {
              type: "object",
              properties: {
                  city: {
                      type: "string"
                  }
              },
              required: ["city"],
              additionalProperties: false
          }
      });
      "
    `);
  });

  it("injects __schema for defineContextTool", () => {
    const source = `const tool = defineContextTool<{ query: string }, MyDeps>({
  name: "search",
  description: "Search",
  tool: (ctx, { query }) => ctx.deps.db.search(query),
});`;

    expect(transformSource(source)).toMatchInlineSnapshot(`
      "const tool = defineContextTool<{
          query: string;
      }, MyDeps>({
          name: "search",
          description: "Search",
          tool: (ctx, { query }) => ctx.deps.db.search(query),
          __schema: {
              type: "object",
              properties: {
                  query: {
                      type: "string"
                  }
              },
              required: ["query"],
              additionalProperties: false
          }
      });
      "
    `);
  });

  it("handles optional properties", () => {
    const source = `const tool = defineTool<{ city: string; units?: string }>({
  name: "get_weather",
  description: "Get weather",
  tool: ({ city, units }) => ({ temp: 72 }),
});`;

    expect(transformSource(source)).toMatchInlineSnapshot(`
      "const tool = defineTool<{
          city: string;
          units?: string;
      }>({
          name: "get_weather",
          description: "Get weather",
          tool: ({ city, units }) => ({ temp: 72 }),
          __schema: {
              type: "object",
              properties: {
                  city: {
                      type: "string"
                  },
                  units: {
                      type: "string"
                  }
              },
              required: ["city"],
              additionalProperties: false
          }
      });
      "
    `);
  });

  it("handles string literal unions (enums)", () => {
    const source = `const tool = defineTool<{ units: "celsius" | "fahrenheit" }>({
  name: "convert",
  description: "Convert",
  tool: ({ units }) => units,
});`;

    expect(transformSource(source)).toMatchInlineSnapshot(`
      "const tool = defineTool<{
          units: "celsius" | "fahrenheit";
      }>({
          name: "convert",
          description: "Convert",
          tool: ({ units }) => units,
          __schema: {
              type: "object",
              properties: {
                  units: {
                      type: "string",
                      enum: ["celsius", "fahrenheit"]
                  }
              },
              required: ["units"],
              additionalProperties: false
          }
      });
      "
    `);
  });

  it("does not override existing __schema", () => {
    const source = `const tool = defineTool<{ city: string }>({
  name: "get_weather",
  description: "Get weather",
  __schema: { type: "object", properties: {}, required: [], additionalProperties: false },
  tool: ({ city }) => ({ temp: 72 }),
});`;

    const result = transformSource(source);
    expect(result).toMatchInlineSnapshot(`
      "const tool = defineTool<{
          city: string;
      }>({
          name: "get_weather",
          description: "Get weather",
          __schema: { type: "object", properties: {}, required: [], additionalProperties: false },
          tool: ({ city }) => ({ temp: 72 }),
      });
      "
    `);
    // Verify only one __schema exists
    expect((result.match(/__schema/g) ?? []).length).toBe(1);
  });

  it("handles property access (llm.defineTool)", () => {
    const source = `const tool = llm.defineTool<{ city: string }>({
  name: "get_weather",
  description: "Get weather",
  tool: ({ city }) => ({ temp: 72 }),
});`;

    expect(transformSource(source)).toMatchInlineSnapshot(`
      "const tool = llm.defineTool<{
          city: string;
      }>({
          name: "get_weather",
          description: "Get weather",
          tool: ({ city }) => ({ temp: 72 }),
          __schema: {
              type: "object",
              properties: {
                  city: {
                      type: "string"
                  }
              },
              required: ["city"],
              additionalProperties: false
          }
      });
      "
    `);
  });

  it("leaves non-tool calls unchanged", () => {
    const source = `const result = someOtherFunction<{ city: string }>({
  name: "test",
});`;

    const result = transformSource(source);
    expect(result).toMatchInlineSnapshot(`
      "const result = someOtherFunction<{
          city: string;
      }>({
          name: "test",
      });
      "
    `);
    expect(result).not.toContain("__schema");
  });

  it("leaves calls without type arguments unchanged", () => {
    const source = `const tool = defineTool({
  name: "get_weather",
  description: "Get weather",
  tool: () => ({ temp: 72 }),
});`;

    const result = transformSource(source);
    expect(result).toMatchInlineSnapshot(`
      "const tool = defineTool({
          name: "get_weather",
          description: "Get weather",
          tool: () => ({ temp: 72 }),
      });
      "
    `);
    expect(result).not.toContain("__schema");
  });

  it("leaves calls with non-object type arguments unchanged", () => {
    const source = `const tool = defineTool<string>({
  name: "test",
  description: "Test",
  tool: (x) => x,
});`;

    const result = transformSource(source);
    expect(result).toMatchInlineSnapshot(`
      "const tool = defineTool<string>({
          name: "test",
          description: "Test",
          tool: (x) => x,
      });
      "
    `);
    expect(result).not.toContain("__schema");
  });

  it("leaves calls with non-object literal argument unchanged", () => {
    const source = `const opts = { name: "test" };
const tool = defineTool<{ x: string }>(opts);`;

    const result = transformSource(source);
    expect(result).toMatchInlineSnapshot(`
      "const opts = { name: "test" };
      const tool = defineTool<{
          x: string;
      }>(opts);
      "
    `);
    expect(result).not.toContain("__schema");
  });

  it("handles complex nested types", () => {
    const source = `const tool = defineTool<{
  user: { name: string; age: number };
  tags: string[];
}>({
  name: "process_user",
  description: "Process user",
  tool: ({ user, tags }) => ({ user, tags }),
});`;

    expect(transformSource(source)).toMatchInlineSnapshot(`
      "const tool = defineTool<{
          user: {
              name: string;
              age: number;
          };
          tags: string[];
      }>({
          name: "process_user",
          description: "Process user",
          tool: ({ user, tags }) => ({ user, tags }),
          __schema: {
              type: "object",
              properties: {
                  user: {
                      type: "object",
                      properties: {
                          name: {
                              type: "string"
                          },
                          age: {
                              type: "number"
                          }
                      },
                      required: ["name", "age"]
                  },
                  tags: {
                      type: "array",
                      items: {
                          type: "string"
                      }
                  }
              },
              required: ["user", "tags"],
              additionalProperties: false
          }
      });
      "
    `);
  });

  it("handles number literal unions", () => {
    const source = `const tool = defineTool<{ count: 1 | 2 | 3 }>({
  name: "counter",
  description: "Counter",
  tool: ({ count }) => count,
});`;

    expect(transformSource(source)).toMatchInlineSnapshot(`
      "const tool = defineTool<{
          count: 1 | 2 | 3;
      }>({
          name: "counter",
          description: "Counter",
          tool: ({ count }) => count,
          __schema: {
              type: "object",
              properties: {
                  count: {
                      type: "number",
                      enum: [1, 2, 3]
                  }
              },
              required: ["count"],
              additionalProperties: false
          }
      });
      "
    `);
  });

  it("handles boolean properties", () => {
    const source = `const tool = defineTool<{ enabled: boolean }>({
  name: "toggle",
  description: "Toggle",
  tool: ({ enabled }) => !enabled,
});`;

    expect(transformSource(source)).toMatchInlineSnapshot(`
      "const tool = defineTool<{
          enabled: boolean;
      }>({
          name: "toggle",
          description: "Toggle",
          tool: ({ enabled }) => !enabled,
          __schema: {
              type: "object",
              properties: {
                  enabled: {
                      type: "boolean"
                  }
              },
              required: ["enabled"],
              additionalProperties: false
          }
      });
      "
    `);
  });

  it("handles null properties", () => {
    const source = `const tool = defineTool<{ value: null }>({
  name: "nullify",
  description: "Nullify",
  tool: ({ value }) => value,
});`;

    expect(transformSource(source)).toMatchInlineSnapshot(`
      "const tool = defineTool<{
          value: null;
      }>({
          name: "nullify",
          description: "Nullify",
          tool: ({ value }) => value,
          __schema: {
              type: "object",
              properties: {
                  value: {
                      type: "null"
                  }
              },
              required: ["value"],
              additionalProperties: false
          }
      });
      "
    `);
  });
});

describe("transformer default export", () => {
  it("returns the same transformer as createToolSchemaTransformer", () => {
    const fileName = "test.ts";
    const libFileName = "lib.d.ts";
    const source = `
      const tool = defineTool<{ city: string }>({
        name: "test",
        description: "Test",
        tool: ({ city }) => city,
      });
    `;

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
        if (name === libFileName || name.includes("lib.")) return libFile;
        return undefined;
      },
      getDefaultLibFileName: () => libFileName,
      writeFile: () => {},
      getCurrentDirectory: () => "/",
      getCanonicalFileName: (f) => f,
      useCaseSensitiveFileNames: () => true,
      getNewLine: () => "\n",
      fileExists: (name) => name === fileName || name === libFileName,
      readFile: () => undefined,
    };

    const program = ts.createProgram(
      [fileName],
      { lib: ["lib.d.ts"], noLib: false },
      host,
    );

    // Test default export
    const defaultTransformer = transformer(program);
    const namedTransformer = createToolSchemaTransformer(program);

    // Both should produce the same result
    const result1 = ts.transform(sourceFile, [defaultTransformer]);
    const result2 = ts.transform(sourceFile, [namedTransformer]);

    const printer = ts.createPrinter();
    const output1 = printer.printFile(result1.transformed[0]!);
    const output2 = printer.printFile(result2.transformed[0]!);

    expect(output1).toBe(output2);
    expect(output1).toContain("__schema");
  });
});
