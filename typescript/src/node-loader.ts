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
import { dirname, resolve as resolvePath } from "node:path";
import { fileURLToPath } from "node:url";
import ts from "typescript";

import { createToolSchemaTransformer } from "./transform/transformer";

/**
 * Check if a file contains calls that need compile-time transformation.
 * Quick regex check to avoid expensive TypeScript compilation for files that don't need it.
 *
 * Patterns that trigger transformation:
 * - defineTool, defineContextTool: Tool schema injection
 * - defineFormat: Format schema injection
 * - version, versionCall: Closure metadata injection for versioning
 */
export function needsTransform(contents: string): boolean {
  return /\b(?:defineTool|defineContextTool|defineFormat|version(?:Call)?)\s*[<(]/.test(
    contents,
  );
}

/** Cache for parsed tsconfig compiler options, keyed by resolved tsconfig path. */
const tsconfigCache = new Map<string, ts.CompilerOptions>();

/**
 * Resolve and cache compiler options from the nearest tsconfig.json.
 * Falls back to default options if no tsconfig is found.
 */
function getCompilerOptions(filePath: string): ts.CompilerOptions {
  const configPath = ts.findConfigFile(
    dirname(filePath),
    ts.sys.fileExists,
    "tsconfig.json",
  );

  const defaults: ts.CompilerOptions = {
    target: ts.ScriptTarget.ES2022,
    module: ts.ModuleKind.ES2022,
    moduleResolution: ts.ModuleResolutionKind.Node10,
    esModuleInterop: true,
    strict: true,
    noEmit: false,
    noEmitOnError: false,
  };

  if (!configPath) {
    return defaults;
  }

  const cached = tsconfigCache.get(configPath);
  if (cached) {
    return cached;
  }

  const configFile = ts.readConfigFile(configPath, ts.sys.readFile);
  if (configFile.error) {
    return defaults;
  }

  const parsed = ts.parseJsonConfigFileContent(
    configFile.config,
    ts.sys,
    dirname(configPath),
  );

  const options: ts.CompilerOptions = {
    ...defaults,
    ...parsed.options,
    noEmit: false,
    noEmitOnError: false,
  };

  tsconfigCache.set(configPath, options);
  return options;
}

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
    const compilerOptions = getCompilerOptions(filePath);

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
      if (resolvePath(fileName) === resolvePath(filePath)) {
        return ts.createSourceFile(fileName, contents, languageVersion, true);
      }
      return originalGetSourceFile(
        fileName,
        languageVersion,
        onError,
        shouldCreateNewSourceFile,
      );
    };

    // Capture the emitted output
    let output: string | undefined;
    host.writeFile = (fileName, data) => {
      if (fileName.endsWith(".js")) {
        output = data;
      }
      // Don't write to disk
    };

    const program = ts.createProgram([filePath], compilerOptions, host);
    const sourceFile = program.getSourceFile(filePath);

    // Coverage ignored: The getSourceFile override above always returns the
    // in-memory file, so this branch is unreachable in normal operation.
    /* v8 ignore next 3 */
    if (!sourceFile) {
      throw new Error(`Could not load source file: ${filePath}`);
    }

    // Apply the Mirascope transformer
    const customTransformers: ts.CustomTransformers = {
      before: [createToolSchemaTransformer(program)],
    };

    // Emit JavaScript with transformers applied
    program.emit(sourceFile, undefined, undefined, false, customTransformers);

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
