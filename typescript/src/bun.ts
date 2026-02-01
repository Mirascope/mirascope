/**
 * Bun preload plugin for Mirascope tool schema transformation.
 *
 * This plugin intercepts TypeScript file loading and applies the Mirascope
 * transformer to inject tool schemas at runtime.
 *
 * ## Usage
 *
 * Create a preload file (e.g., `preload.ts`):
 * ```typescript
 * import { mirascope } from 'mirascope/bun';
 * mirascope();
 * ```
 *
 * Add to your `bunfig.toml`:
 * ```toml
 * preload = ["./preload.ts"]
 * ```
 *
 * Then run your files normally:
 * ```bash
 * bun run my-file.ts
 * ```
 */

/* eslint-disable @typescript-eslint/unbound-method */
import { plugin } from "bun";
import { readFileSync } from "fs";
import { resolve, dirname } from "path";
import ts from "typescript";

import { createToolSchemaTransformer } from "./transform/transformer";

/**
 * Options for the Mirascope Bun plugin.
 */
export interface MirascopeBunPluginOptions {
  /**
   * File filter pattern. Defaults to /\.tsx?$/
   */
  filter?: RegExp;

  /**
   * Patterns to exclude. Files matching these won't be transformed.
   * Defaults to [/node_modules/]
   */
  exclude?: RegExp[];
}

/**
 * Check if a file contains defineTool, defineContextTool, or defineFormat calls.
 * Quick regex check to avoid expensive TypeScript compilation for files that don't need it.
 */
function needsTransform(contents: string): boolean {
  return /\bdefineTool\b|\bdefineContextTool\b|\bdefineFormat\b/.test(contents);
}

/**
 * Transform TypeScript source code to inject tool schemas.
 */
function transformSource(
  filePath: string,
  contents: string,
): string | undefined {
  // Find tsconfig.json
  const configPath = ts.findConfigFile(
    dirname(filePath),
    ts.sys.fileExists,
    "tsconfig.json",
  );

  const compilerOptions: ts.CompilerOptions = {
    target: ts.ScriptTarget.ESNext,
    module: ts.ModuleKind.ESNext,
    moduleResolution: ts.ModuleResolutionKind.Bundler,
    esModuleInterop: true,
    strict: true,
  };

  // Load tsconfig if found
  if (configPath) {
    const configFile = ts.readConfigFile(configPath, ts.sys.readFile);
    if (!configFile.error) {
      const parsed = ts.parseJsonConfigFileContent(
        configFile.config,
        ts.sys,
        dirname(configPath),
      );
      Object.assign(compilerOptions, parsed.options);
    }
  }

  // Create a program with just this file
  const host = ts.createCompilerHost(compilerOptions);
  const originalGetSourceFile = host.getSourceFile;

  // Override to provide our in-memory source
  host.getSourceFile = (
    fileName: string,
    languageVersion: ts.ScriptTarget,
    onError?: (message: string) => void,
    shouldCreateNewSourceFile?: boolean,
  ) => {
    if (resolve(fileName) === resolve(filePath)) {
      return ts.createSourceFile(fileName, contents, languageVersion, true);
    }
    return originalGetSourceFile(
      fileName,
      languageVersion,
      onError,
      shouldCreateNewSourceFile,
    );
  };

  const program = ts.createProgram([filePath], compilerOptions, host);
  const sourceFile = program.getSourceFile(filePath);

  if (!sourceFile) {
    return undefined;
  }

  // Apply the transformer
  const transformer = createToolSchemaTransformer(program);
  const result = ts.transform(sourceFile, [transformer]);
  const transformedSourceFile = result.transformed[0];

  if (!transformedSourceFile) {
    result.dispose();
    return undefined;
  }

  // Print the transformed source back to string
  const printer = ts.createPrinter({ newLine: ts.NewLineKind.LineFeed });
  const output = printer.printFile(transformedSourceFile);

  result.dispose();
  return output;
}

/**
 * Register the Mirascope Bun plugin for tool schema transformation.
 *
 * @param options - Plugin options.
 *
 * @example
 * ```typescript
 * // preload.ts
 * import { mirascope } from 'mirascope/bun';
 * mirascope();
 * ```
 */
export function mirascope(options: MirascopeBunPluginOptions = {}): void {
  const { filter = /\.tsx?$/, exclude = [/node_modules/] } = options;

  plugin({
    name: "mirascope",
    setup(build) {
      build.onLoad({ filter }, (args) => {
        // Check exclusions - let Bun handle these normally
        for (const pattern of exclude) {
          if (pattern.test(args.path)) {
            // Return undefined to let Bun handle it normally
            return;
          }
        }

        const contents = readFileSync(args.path, "utf-8");
        const loader = args.path.endsWith(".tsx") ? "tsx" : "ts";

        // Quick check: skip files without tool definitions
        if (!needsTransform(contents)) {
          // Return original contents to keep Bun happy
          return { contents, loader };
        }

        const transformed = transformSource(args.path, contents);

        // Return transformed or original contents
        return {
          contents: transformed ?? contents,
          loader,
        };
      });
    },
  });
}

export default mirascope;
