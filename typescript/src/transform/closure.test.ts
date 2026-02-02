/**
 * Tests for closure extraction with real Call definitions.
 *
 * These tests transform real TypeScript files and verify that the
 * closure extraction correctly captures the full Call definition.
 */

import * as fs from "fs";
import * as path from "path";
import ts from "typescript";
import { describe, it, expect } from "vitest";

import { createToolSchemaTransformer } from "./transformer";

/**
 * Transform a real TypeScript file and return the output.
 */
function transformFile(filePath: string): string {
  const absolutePath = path.resolve(__dirname, filePath);
  const source = fs.readFileSync(absolutePath, "utf-8");
  const fileName = path.basename(filePath);

  const sourceFile = ts.createSourceFile(
    fileName,
    source,
    ts.ScriptTarget.Latest,
    true,
  );

  // Create a minimal compiler host
  const host: ts.CompilerHost = {
    getSourceFile: (name) => {
      if (name === fileName) return sourceFile;
      // Return a minimal lib file for type checking
      if (name.includes("lib.")) {
        return ts.createSourceFile(
          name,
          "interface Array<T> { length: number; }",
          ts.ScriptTarget.Latest,
          true,
        );
      }
      return undefined;
    },
    getDefaultLibFileName: () => "lib.d.ts",
    writeFile: () => {},
    getCurrentDirectory: () => path.dirname(absolutePath),
    getCanonicalFileName: (f) => f,
    useCaseSensitiveFileNames: () => true,
    getNewLine: () => "\n",
    fileExists: (name) => name === fileName || fs.existsSync(name),
    readFile: (name) => {
      if (name === fileName) return source;
      if (fs.existsSync(name)) return fs.readFileSync(name, "utf-8");
      return undefined;
    },
  };

  const program = ts.createProgram([fileName], { lib: ["lib.d.ts"] }, host);
  const transformer = createToolSchemaTransformer(program);
  const result = ts.transform(sourceFile, [transformer]);
  const printer = ts.createPrinter({ newLine: ts.NewLineKind.LineFeed });
  const output = printer.printFile(result.transformed[0]!);
  result.dispose();
  return output;
}

describe("closure extraction with real Call definitions", () => {
  const transformed = transformFile("./__fixtures__/closure-test-calls.ts");

  describe("versionedSimpleCall", () => {
    it("injects __closure metadata", () => {
      expect(transformed).toContain("__closure");
    });

    it("captures the full defineCall expression", () => {
      // The closure should contain the model configuration
      expect(transformed).toContain("openai/gpt-4o-mini");
    });
  });

  describe("versionedCallWithVars", () => {
    it("captures template with variables", () => {
      expect(transformed).toContain("Please answer:");
    });

    it("captures maxTokens configuration", () => {
      expect(transformed).toContain("1024");
    });
  });

  describe("versionedCallWithTools", () => {
    it("includes the tool definition in closure", () => {
      // The closure should capture the tool dependency
      expect(transformed).toContain("weatherTool");
    });
  });

  describe("versionedCallWithMessages", () => {
    it("captures message helper usage", () => {
      expect(transformed).toContain("llm.messages.system");
      expect(transformed).toContain("llm.messages.user");
    });

    it("captures the template content", () => {
      expect(transformed).toContain("You are a helpful assistant");
      expect(transformed).toContain("Explain");
    });

    it("captures model configuration", () => {
      expect(transformed).toContain("anthropic/claude-sonnet");
      expect(transformed).toContain("2048");
    });
  });

  describe("closure code structure", () => {
    it("includes hash in closure metadata", () => {
      // Check that hash is present in the closure
      const hashMatch = transformed.match(/hash:\s*"([a-f0-9]+)"/);
      expect(hashMatch).not.toBeNull();
      expect(hashMatch![1]).toHaveLength(64); // SHA-256 hash
    });

    it("includes signature in closure metadata", () => {
      expect(transformed).toContain("signature:");
      expect(transformed).toContain("signatureHash:");
    });

    it("includes code in closure metadata", () => {
      expect(transformed).toContain("code:");
    });
  });
});
