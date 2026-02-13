/**
 * Tests for shared compilation utilities.
 */

import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import ts from "typescript";
import { describe, it, expect, beforeAll, afterAll } from "vitest";

import {
  needsTransform,
  getCompilerOptions,
  createProgramForFile,
} from "./compile";

// ── needsTransform ──────────────────────────────────────────────────

describe("needsTransform", () => {
  it("returns true for defineTool(", () => {
    expect(needsTransform('const t = defineTool({ name: "x" })')).toBe(true);
  });

  it("returns true for defineContextTool(", () => {
    expect(needsTransform("defineContextTool({ name: 'y' })")).toBe(true);
  });

  it("returns true for defineFormat(", () => {
    expect(needsTransform("defineFormat({ schema })")).toBe(true);
  });

  it("returns true for version(", () => {
    expect(needsTransform("ops.version(fn, opts)")).toBe(true);
  });

  it("returns true for versionCall(", () => {
    expect(needsTransform("ops.versionCall(fn, opts)")).toBe(true);
  });

  it("returns true with whitespace before paren", () => {
    expect(needsTransform("defineTool  (args)")).toBe(true);
  });

  it("returns true for generic call syntax", () => {
    expect(needsTransform("defineTool<ToolArgs>({})")).toBe(true);
  });

  it("returns false for plain text without calls", () => {
    expect(needsTransform('const x = "hello world";')).toBe(false);
  });

  it('returns false for "version" as a property name', () => {
    expect(needsTransform('const obj = { version: "1.0.0" };')).toBe(false);
  });

  it('returns false for "version" in a comment', () => {
    expect(needsTransform("// bump the version number")).toBe(false);
  });

  it('returns false for "version" in a string', () => {
    expect(needsTransform('const v = "version 2.0"')).toBe(false);
  });

  it("returns false for empty string", () => {
    expect(needsTransform("")).toBe(false);
  });
});

// ── getCompilerOptions ──────────────────────────────────────────────

describe("getCompilerOptions", () => {
  describe("with valid tsconfig.json", () => {
    let tempDir: string;

    beforeAll(async () => {
      tempDir = await fs.mkdtemp(path.join(os.tmpdir(), "mirascope-compile-"));
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

    it("parses tsconfig and returns merged options", () => {
      const filePath = path.join(tempDir, "test.ts");
      const options = getCompilerOptions(filePath);

      expect(options.strict).toBe(true);
      expect(options.esModuleInterop).toBe(true);
    });

    it("caches options for the same tsconfig", () => {
      const filePath1 = path.join(tempDir, "a.ts");
      const filePath2 = path.join(tempDir, "b.ts");

      const options1 = getCompilerOptions(filePath1);
      const options2 = getCompilerOptions(filePath2);

      // Same object reference means caching works
      expect(options1).toBe(options2);
    });

    it("uses caller-provided defaults as base", () => {
      const filePath = path.join(tempDir, "test.ts");
      const customDefaults: ts.CompilerOptions = {
        target: ts.ScriptTarget.ESNext,
        module: ts.ModuleKind.ESNext,
        moduleResolution: ts.ModuleResolutionKind.Bundler,
      };

      // With custom defaults, the tsconfig overrides apply on top
      const options = getCompilerOptions(filePath, customDefaults);
      expect(options).toBeDefined();
    });
  });

  describe("without tsconfig.json", () => {
    let tempDir: string;

    beforeAll(async () => {
      tempDir = await fs.mkdtemp(
        path.join(os.tmpdir(), "mirascope-compile-noconfig-"),
      );
    });

    afterAll(async () => {
      await fs.rm(tempDir, { recursive: true });
    });

    it("returns default options when no tsconfig found", () => {
      const filePath = path.join(tempDir, "test.ts");
      const options = getCompilerOptions(filePath);

      expect(options.target).toBe(ts.ScriptTarget.ES2022);
      expect(options.module).toBe(ts.ModuleKind.ES2022);
      expect(options.esModuleInterop).toBe(true);
      expect(options.strict).toBe(true);
    });

    it("returns caller-provided defaults when no tsconfig found", () => {
      const filePath = path.join(tempDir, "test.ts");
      const customDefaults: ts.CompilerOptions = {
        target: ts.ScriptTarget.ESNext,
        module: ts.ModuleKind.ESNext,
      };

      const options = getCompilerOptions(filePath, customDefaults);
      expect(options.target).toBe(ts.ScriptTarget.ESNext);
      expect(options.module).toBe(ts.ModuleKind.ESNext);
    });
  });

  describe("with invalid tsconfig.json", () => {
    let tempDir: string;

    beforeAll(async () => {
      tempDir = await fs.mkdtemp(
        path.join(os.tmpdir(), "mirascope-compile-badconfig-"),
      );
      await fs.writeFile(
        path.join(tempDir, "tsconfig.json"),
        "{ invalid json }",
      );
    });

    afterAll(async () => {
      await fs.rm(tempDir, { recursive: true });
    });

    it("falls back to defaults when tsconfig has parse errors", () => {
      const filePath = path.join(tempDir, "test.ts");
      const options = getCompilerOptions(filePath);

      expect(options.target).toBe(ts.ScriptTarget.ES2022);
      expect(options.strict).toBe(true);
    });
  });
});

// ── createProgramForFile ────────────────────────────────────────────

describe("createProgramForFile", () => {
  it("creates a program and returns sourceFile for valid input", () => {
    const source = "export const x: number = 42;\n";
    const { program, sourceFile } = createProgramForFile(
      "/tmp/test-program.ts",
      source,
      { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ES2022 },
    );

    expect(program).toBeDefined();
    expect(sourceFile).toBeDefined();
    expect(sourceFile.text).toContain("42");
  });

  it("uses in-memory source instead of filesystem", () => {
    const source = "export const unique_marker_12345 = true;\n";
    const { sourceFile } = createProgramForFile(
      "/tmp/nonexistent-file-abc.ts",
      source,
      { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ES2022 },
    );

    // The in-memory source should be used, not the filesystem
    expect(sourceFile.text).toContain("unique_marker_12345");
  });
});
