/**
 * Node.js ESM loader for Mirascope tool schema transformation.
 *
 * This loader intercepts TypeScript file loading, compiles TS to JS, and
 * applies the Mirascope transformer to inject tool schemas at runtime.
 * No `--experimental-strip-types` flag is needed — the loader handles
 * full TypeScript compilation.
 *
 * ## Usage
 *
 * Run with the --import flag (Node.js 20.6+):
 * ```bash
 * node --import mirascope/loader your-script.ts
 * ```
 *
 * Or use NODE_OPTIONS:
 * ```bash
 * NODE_OPTIONS='--import mirascope/loader' node your-script.ts
 * ```
 */

import type Module from "node:module";

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import ts from "typescript";

import {
  needsTransform,
  getCompilerOptions,
  createProgramForFile,
} from "./transform/compile";
import { createToolSchemaTransformer } from "./transform/transformer";

export { needsTransform } from "./transform/compile";

/** Node-specific compiler defaults (loader must emit JavaScript). */
const NODE_DEFAULTS: ts.CompilerOptions = {
  target: ts.ScriptTarget.ES2022,
  module: ts.ModuleKind.ES2022,
  moduleResolution: ts.ModuleResolutionKind.Node10,
  esModuleInterop: true,
  strict: true,
  noEmit: false,
  noEmitOnError: false,
};

/**
 * Transform TypeScript source code to inject tool schemas and compile to JavaScript.
 * @param filePath - Path to the TypeScript file
 * @param contents - Source code contents
 * @param applyMirascopeTransform - Whether to apply the Mirascope tool schema transformer
 */
export function transformSource(
  filePath: string,
  contents: string,
  applyMirascopeTransform: boolean,
): string {
  // If we need the Mirascope transform, create a full program
  if (applyMirascopeTransform) {
    const compilerOptions = getCompilerOptions(filePath, NODE_DEFAULTS);
    // Force emit flags — tsconfig may set noEmit: true but the loader must emit
    compilerOptions.noEmit = false;
    compilerOptions.noEmitOnError = false;

    const { program, sourceFile } = createProgramForFile(
      filePath,
      contents,
      compilerOptions,
    );

    // Capture the emitted output
    let output: string | undefined;

    const customTransformers: ts.CustomTransformers = {
      before: [createToolSchemaTransformer(program)],
    };

    // Emit JavaScript with transformers applied, capturing output in memory
    program.emit(
      sourceFile,
      (fileName, data) => {
        if (fileName.endsWith(".js")) {
          output = data;
        }
      },
      undefined,
      false,
      customTransformers,
    );

    // Coverage ignored: TypeScript emits output even with type errors.
    // This is a defensive fallback for unexpected compiler failures.
    /* v8 ignore next 3 */
    if (!output) {
      throw new Error(`Failed to emit JavaScript for: ${filePath}`);
    }

    return output;
  }

  // For files without Mirascope features, use simple transpilation
  const result = ts.transpileModule(contents, {
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.ES2022,
      moduleResolution: ts.ModuleResolutionKind.Node10,
      esModuleInterop: true,
    },
    fileName: filePath,
  });

  return result.outputText;
}

/**
 * Node.js loader hook for loading TypeScript files.
 * This hook intercepts .ts and .tsx files and applies the Mirascope transform.
 */
export async function load(
  url: string,
  context: Module.LoadHookContext,
  nextLoad: (
    url: string,
    context?: Partial<Module.LoadHookContext>,
  ) => Module.LoadFnOutput | Promise<Module.LoadFnOutput>,
): Promise<Module.LoadFnOutput> {
  // Only process TypeScript files
  if (!url.endsWith(".ts") && !url.endsWith(".tsx")) {
    return nextLoad(url, context);
  }

  // Skip node_modules
  if (url.includes("/node_modules/")) {
    return nextLoad(url, context);
  }

  const filePath = fileURLToPath(url);
  const contents = readFileSync(filePath, "utf-8");

  // Check if we need to apply the Mirascope transformer
  const applyMirascopeTransform = needsTransform(contents);

  // Always transpile TypeScript to JavaScript, but only apply the Mirascope
  // transformer if the file contains defineTool, version, etc.
  const transformed = transformSource(
    filePath,
    contents,
    applyMirascopeTransform,
  );

  return {
    format: "module",
    source: transformed,
    shortCircuit: true,
  };
}
