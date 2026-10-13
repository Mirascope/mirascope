/**
 * Shared compilation utilities for Mirascope runtime loaders and build plugins.
 *
 * Provides common functions for detecting files that need transformation,
 * resolving TypeScript compiler options, and creating single-file programs
 * with in-memory source overrides.
 */

/* eslint-disable @typescript-eslint/unbound-method */
import { dirname, resolve } from "node:path";
import ts from "typescript";

/**
 * Pattern matching calls that need compile-time transformation:
 * - defineTool, defineContextTool: Tool schema injection
 * - defineFormat: Format schema injection
 * - version, versionCall: Closure metadata injection for versioning
 */
const TRANSFORM_PATTERN =
  /\b(?:defineTool|defineContextTool|defineFormat|version(?:Call)?)\s*[<(]/;

/**
 * Check if a file contains calls that need compile-time transformation.
 * Quick regex check to avoid expensive TypeScript compilation for files that don't need it.
 */
export function needsTransform(contents: string): boolean {
  return TRANSFORM_PATTERN.test(contents);
}

/** Default compiler options used when no tsconfig is found and no defaults are provided. */
const DEFAULT_COMPILER_OPTIONS: ts.CompilerOptions = {
  target: ts.ScriptTarget.ES2022,
  module: ts.ModuleKind.ES2022,
  moduleResolution: ts.ModuleResolutionKind.Node10,
  esModuleInterop: true,
  strict: true,
};

/** Cache for parsed tsconfig compiler options, keyed by resolved tsconfig path. */
const tsconfigCache = new Map<string, ts.CompilerOptions>();

/**
 * Resolve and cache compiler options from the nearest tsconfig.json.
 * Falls back to the provided defaults (or built-in defaults) if no tsconfig is found.
 *
 * @param filePath - Path to the file being compiled (used to locate tsconfig.json)
 * @param defaults - Base compiler options to use; tsconfig values override these
 */
export function getCompilerOptions(
  filePath: string,
  defaults: ts.CompilerOptions = DEFAULT_COMPILER_OPTIONS,
): ts.CompilerOptions {
  const configPath = ts.findConfigFile(
    dirname(filePath),
    ts.sys.fileExists,
    "tsconfig.json",
  );

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
  };

  tsconfigCache.set(configPath, options);
  return options;
}

/**
 * Create a TypeScript program for a single file with in-memory source content.
 *
 * This overrides the compiler host's file reading so that the provided `contents`
 * are used instead of reading from disk, enabling transformation of source that
 * may not yet be written to the filesystem.
 *
 * @param filePath - Path to the file (used for module resolution and as program root)
 * @param contents - In-memory source code for the file
 * @param compilerOptions - TypeScript compiler options
 */
export function createProgramForFile(
  filePath: string,
  contents: string,
  compilerOptions: ts.CompilerOptions,
): { program: ts.Program; sourceFile: ts.SourceFile } {
  const host = ts.createCompilerHost(compilerOptions);
  const originalGetSourceFile = host.getSourceFile;

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

  // The getSourceFile override above always returns the in-memory file,
  // so this branch is unreachable in normal operation.
  /* v8 ignore next 3 */
  if (!sourceFile) {
    throw new Error(`Could not load source file: ${filePath}`);
  }

  return { program, sourceFile };
}
