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

describe("version transform", () => {
  it("injects __closure for version() with inline arrow function", () => {
    const source = `const fn = version(async (text: string): Promise<number[]> => {
  return [1, 2, 3];
});`;

    const result = transformSource(source);
    expect(result).toContain("__closure");
    expect(result).toContain("code");
    expect(result).toContain("hash");
    expect(result).toContain("signature");
    expect(result).toContain("signatureHash");
  });

  it("infers variable name from assignment", () => {
    const source = `const myFunction = version(async (x: string) => x.toUpperCase());`;

    const result = transformSource(source);
    // Should inject the inferred name "myFunction"
    expect(result).toContain('name: "myFunction"');
  });

  it("does not override explicit name with inferred name", () => {
    const source = `const myFunction = version(async (x: string) => x, {
  name: "explicit-name",
});`;

    const result = transformSource(source);
    // Should keep the explicit name, not use "myFunction"
    expect(result).toContain('name: "explicit-name"');
    expect(result).not.toContain('name: "myFunction"');
  });

  it("injects __closure with correct signature for arrow function", () => {
    const source = `const fn = version(async (text: string): Promise<number[]> => {
  return [1, 2, 3];
});`;

    const result = transformSource(source);
    expect(result).toContain("(text: string): Promise<number[]>");
  });

  it("injects __closure for version() with function expression", () => {
    const source = `const fn = version(async function compute(x: number) {
  return x * 2;
});`;

    const result = transformSource(source);
    expect(result).toContain("__closure");
    expect(result).toContain("hash");
  });

  it("merges __closure into existing options object", () => {
    const source = `const fn = version(async (x: string) => x, {
  name: "my-function",
  tags: ["prod"],
});`;

    const result = transformSource(source);
    expect(result).toContain("__closure");
    expect(result).toContain('name: "my-function"');
    expect(result).toContain('tags: ["prod"]');
  });

  it("does not override existing __closure", () => {
    const source = `const fn = version(async (x: string) => x, {
  name: "test",
  __closure: { code: "existing", hash: "abc", signature: "()", signatureHash: "def" },
});`;

    const result = transformSource(source);
    // Should only have one __closure
    expect((result.match(/__closure/g) ?? []).length).toBe(1);
    expect(result).toContain('code: "existing"');
  });

  it("handles ops.version() property access syntax", () => {
    const source = `const fn = ops.version(async (x: number) => x * 2);`;

    const result = transformSource(source);
    expect(result).toContain("__closure");
    expect(result).toContain("hash");
  });

  it("computes different hashes for different functions", () => {
    const source1 = `const fn1 = version(async (x: string) => x.toUpperCase());`;
    const source2 = `const fn2 = version(async (x: string) => x.toLowerCase());`;

    const result1 = transformSource(source1);
    const result2 = transformSource(source2);

    // Extract hash values from results
    const hashMatch1 = result1.match(/hash: "([a-f0-9]+)"/);
    const hashMatch2 = result2.match(/hash: "([a-f0-9]+)"/);

    expect(hashMatch1).not.toBeNull();
    expect(hashMatch2).not.toBeNull();
    expect(hashMatch1![1]).not.toBe(hashMatch2![1]);
  });

  it("computes same hash for same-named identical functions", () => {
    // Hash includes the full declaration (const name = ...), so same variable names
    // and function bodies should produce the same hash
    const source1 = `const fn = version(async (x: string) => x.toUpperCase());`;
    const source2 = `const fn = version(async (x: string) => x.toUpperCase());`;

    const result1 = transformSource(source1);
    const result2 = transformSource(source2);

    // Extract hash values from results
    const hashMatch1 = result1.match(/hash: "([a-f0-9]+)"/);
    const hashMatch2 = result2.match(/hash: "([a-f0-9]+)"/);

    expect(hashMatch1).not.toBeNull();
    expect(hashMatch2).not.toBeNull();
    expect(hashMatch1![1]).toBe(hashMatch2![1]);
  });

  it("computes different hash for different-named identical functions", () => {
    // Since the closure includes the full declaration (const fn1 = ... vs const fn2 = ...),
    // different variable names produce different hashes even with identical bodies
    const source1 = `const fn1 = version(async (x: string) => x.toUpperCase());`;
    const source2 = `const fn2 = version(async (x: string) => x.toUpperCase());`;

    const result1 = transformSource(source1);
    const result2 = transformSource(source2);

    // Extract hash values from results
    const hashMatch1 = result1.match(/hash: "([a-f0-9]+)"/);
    const hashMatch2 = result2.match(/hash: "([a-f0-9]+)"/);

    expect(hashMatch1).not.toBeNull();
    expect(hashMatch2).not.toBeNull();
    // Different variable names = different hashes (because closure includes full declaration)
    expect(hashMatch1![1]).not.toBe(hashMatch2![1]);
  });

  it("leaves curried version(options) unchanged (no fn available)", () => {
    const source = `const withVersion = version({ name: "test", tags: ["v1"] });`;

    const result = transformSource(source);
    // Should not inject __closure since we don't have the function
    expect(result).not.toContain("__closure");
    expect(result).toContain('name: "test"');
  });

  it("leaves non-version calls unchanged", () => {
    const source = `const result = someOtherFunction(async (x: string) => x);`;

    const result = transformSource(source);
    expect(result).not.toContain("__closure");
  });

  it("leaves version calls without function argument unchanged", () => {
    const source = `const fn = version();`;

    const result = transformSource(source);
    expect(result).not.toContain("__closure");
  });

  it("captures full function body in code field", () => {
    const source = `const fn = version(async (data: { name: string }) => {
  const processed = data.name.trim();
  return processed.length;
});`;

    const result = transformSource(source);
    expect(result).toContain("__closure");
    // The code should contain the function body
    expect(result).toContain("data.name.trim()");
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
