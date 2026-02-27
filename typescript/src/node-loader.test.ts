/**
 * Tests for the Node.js ESM loader.
 */

import { readFileSync } from "node:fs";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";
import {
  describe,
  it,
  expect,
  vi,
  beforeAll,
  afterAll,
  beforeEach,
} from "vitest";

import { transformSource, load } from "./node-loader";

// ── transformSource ─────────────────────────────────────────────────

describe("transformSource", () => {
  describe("with applyMirascopeTransform: false", () => {
    it("transpiles TypeScript to JavaScript (strips types)", () => {
      const source =
        'const greeting: string = "hello";\nexport { greeting };\n';
      const output = transformSource("/tmp/test.ts", source, false);

      // Types should be stripped
      expect(output).not.toContain(": string");
      // Value should remain
      expect(output).toContain("greeting");
      expect(output).toContain("hello");
    });

    it("preserves ES module syntax", () => {
      const source = "export const x: number = 42;\n";
      const output = transformSource("/tmp/test.ts", source, false);

      expect(output).toContain("export");
      expect(output).toContain("42");
    });
  });

  describe("with applyMirascopeTransform: true", () => {
    let tempDir: string;

    beforeAll(async () => {
      tempDir = await fs.mkdtemp(path.join(os.tmpdir(), "mirascope-loader-"));

      await fs.writeFile(
        path.join(tempDir, "tsconfig.json"),
        JSON.stringify({
          compilerOptions: {
            target: "ES2022",
            module: "ES2022",
            moduleResolution: "Node10",
            esModuleInterop: true,
            strict: true,
          },
        }),
      );
    });

    afterAll(async () => {
      await fs.rm(tempDir, { recursive: true });
    });

    it("applies the Mirascope transformer and injects __schema", async () => {
      const filePath = path.join(tempDir, "tool.ts");
      const source = `
export interface ToolArgs {
  city: string;
  units?: string;
}

export const defineTool = <T>(opts: {
  name: string;
  description: string;
  tool: (args: T) => unknown;
  __schema?: object;
}) => opts;

export const getWeather = defineTool<ToolArgs>({
  name: 'get_weather',
  description: 'Get weather for a city',
  tool: ({ city }) => ({ temp: 72, city }),
});
`.trim();

      await fs.writeFile(filePath, source);

      const output = transformSource(filePath, source, true);

      expect(output).toContain("__schema");
      expect(output).toContain("city");
    });

    it("uses cached tsconfig on second call for same project", async () => {
      const filePath1 = path.join(tempDir, "cache1.ts");
      const filePath2 = path.join(tempDir, "cache2.ts");
      const source = 'export const x: string = "hello";\n';
      await fs.writeFile(filePath1, source);
      await fs.writeFile(filePath2, source);

      // Both calls use applyMirascopeTransform: true to go through getCompilerOptions
      // First call parses tsconfig, second should hit cache
      const output1 = transformSource(filePath1, source, true);
      const output2 = transformSource(filePath2, source, true);

      expect(output1).toBe(output2);
    });
  });

  describe("without tsconfig.json", () => {
    let tempDir: string;

    beforeAll(async () => {
      // Create a directory with no tsconfig.json
      tempDir = await fs.mkdtemp(
        path.join(os.tmpdir(), "mirascope-loader-noconfig-"),
      );
    });

    afterAll(async () => {
      await fs.rm(tempDir, { recursive: true });
    });

    it("uses default compiler options when no tsconfig found", async () => {
      const filePath = path.join(tempDir, "test.ts");
      const source = "export const x: number = 1;\n";
      await fs.writeFile(filePath, source);

      // Use applyMirascopeTransform: true to exercise getCompilerOptions
      const output = transformSource(filePath, source, true);
      expect(output).toContain("1");
      expect(output).not.toContain(": number");
    });
  });

  describe("with invalid tsconfig.json", () => {
    let tempDir: string;

    beforeAll(async () => {
      tempDir = await fs.mkdtemp(
        path.join(os.tmpdir(), "mirascope-loader-badconfig-"),
      );
      await fs.writeFile(
        path.join(tempDir, "tsconfig.json"),
        "{ invalid json }",
      );
    });

    afterAll(async () => {
      await fs.rm(tempDir, { recursive: true });
    });

    it("falls back to defaults when tsconfig has parse errors", async () => {
      const filePath = path.join(tempDir, "test.ts");
      const source = "export const x: number = 1;\n";
      await fs.writeFile(filePath, source);

      const output = transformSource(filePath, source, true);
      expect(output).toContain("1");
      expect(output).not.toContain(": number");
    });
  });
});

// ── load ────────────────────────────────────────────────────────────

vi.mock("node:fs", async (importOriginal) => {
  const actual = await importOriginal<typeof import("node:fs")>();
  return {
    ...actual,
    readFileSync: vi.fn(actual.readFileSync),
  };
});

describe("load", () => {
  const nextLoad = vi.fn();
  const context = { conditions: [], format: null, importAttributes: {} };

  beforeEach(() => {
    vi.clearAllMocks();
    nextLoad.mockResolvedValue({ format: "module", source: "" });
  });

  it("delegates non-.ts files to nextLoad", async () => {
    const url = "file:///app/index.js";
    await load(url, context, nextLoad);

    expect(nextLoad).toHaveBeenCalledWith(url, context);
  });

  it("delegates node_modules .ts files to nextLoad", async () => {
    const url = "file:///app/node_modules/some-pkg/index.ts";
    await load(url, context, nextLoad);

    expect(nextLoad).toHaveBeenCalledWith(url, context);
  });

  it("transforms .ts files outside node_modules", async () => {
    const source = "export const x: number = 42;\n";
    const mockedReadFileSync = vi.mocked(readFileSync);
    mockedReadFileSync.mockReturnValueOnce(source);

    const url = pathToFileURL("/tmp/test-load.ts").href;
    const result = await load(url, context, nextLoad);

    expect(nextLoad).not.toHaveBeenCalled();
    expect(result.format).toBe("module");
    expect(result.shortCircuit).toBe(true);
    expect(typeof result.source).toBe("string");
    expect(result.source as string).toContain("42");
    expect(result.source as string).not.toContain(": number");
  });

  it("delegates .tsx files in node_modules to nextLoad", async () => {
    const url = "file:///app/node_modules/ui/Button.tsx";
    await load(url, context, nextLoad);

    expect(nextLoad).toHaveBeenCalledWith(url, context);
  });

  it("transforms .tsx files outside node_modules", async () => {
    const source = 'export const x: string = "hi";\n';
    const mockedReadFileSync = vi.mocked(readFileSync);
    mockedReadFileSync.mockReturnValueOnce(source);

    const url = pathToFileURL("/tmp/component.tsx").href;
    const result = await load(url, context, nextLoad);

    expect(nextLoad).not.toHaveBeenCalled();
    expect(result.format).toBe("module");
    expect(result.source as string).toContain("hi");
  });
});
