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

import { plugin } from "bun";
import { readFileSync } from "node:fs";
import ts from "typescript";

import {
  needsTransform,
  getCompilerOptions,
  createProgramForFile,
} from "./transform/compile";
import { createToolSchemaTransformer } from "./transform/transformer";

/** Bun-specific compiler defaults (Bun handles TS→JS compilation itself). */
const BUN_DEFAULTS: ts.CompilerOptions = {
  target: ts.ScriptTarget.ESNext,
  module: ts.ModuleKind.ESNext,
  moduleResolution: ts.ModuleResolutionKind.Bundler,
  esModuleInterop: true,
  strict: true,
};

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
 * Transform TypeScript source code to inject tool schemas.
 */
function transformSource(
  filePath: string,
  contents: string,
): string | undefined {
  const compilerOptions = getCompilerOptions(filePath, BUN_DEFAULTS);
  const { program, sourceFile } = createProgramForFile(
    filePath,
    contents,
    compilerOptions,
  );

  const transformer = createToolSchemaTransformer(program);
  const result = ts.transform(sourceFile, [transformer]);
  const transformedSourceFile = result.transformed[0];

  if (!transformedSourceFile) {
    result.dispose();
    return undefined;
  }

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
