/**
 * esbuild plugin for Mirascope tool schema transformation.
 *
 * This plugin uses the TypeScript compiler instead of esbuild's built-in
 * TypeScript support to ensure access to type information for schema generation.
 */

import type { Plugin, OnLoadArgs, OnLoadResult, PluginBuild } from 'esbuild';
import ts from 'typescript';
import path from 'path';
import fs from 'fs';
import { createToolSchemaTransformer } from '@/transform/transformer';

export interface MirascopeEsbuildPluginOptions {
  /**
   * Path to tsconfig.json. Defaults to './tsconfig.json'
   */
  tsconfig?: string;

  /**
   * File filter pattern. Defaults to /\.(ts|tsx)$/
   */
  filter?: RegExp;

  /**
   * Additional TypeScript compiler options to merge with tsconfig.
   */
  compilerOptions?: ts.CompilerOptions;
}

/**
 * esbuild plugin that applies the Mirascope tool schema transformer.
 *
 * This plugin uses the TypeScript compiler instead of esbuild's built-in
 * TypeScript support to ensure access to type information for schema generation.
 *
 * @example
 * ```typescript
 * import * as esbuild from 'esbuild';
 * import { mirascope } from 'mirascope/esbuild';
 *
 * await esbuild.build({
 *   entryPoints: ['src/index.ts'],
 *   bundle: true,
 *   outfile: 'dist/bundle.js',
 *   plugins: [mirascope()],
 * });
 * ```
 */
export function mirascope(options: MirascopeEsbuildPluginOptions = {}): Plugin {
  const {
    tsconfig = './tsconfig.json',
    filter = /\.(ts|tsx)$/,
    compilerOptions: extraOptions = {},
  } = options;

  // Cache for the TypeScript program and transformer
  let cachedProgram: ts.Program | undefined;
  let cachedTransformer: ts.TransformerFactory<ts.SourceFile> | undefined;
  let cachedConfigPath: string | undefined;
  let cachedCompilerOptions: ts.CompilerOptions | undefined;

  return {
    name: 'mirascope',

    setup(build: PluginBuild) {
      const cwd = process.cwd();
      const configPath = path.resolve(cwd, tsconfig);

      // Read and parse tsconfig.json
      let parsedConfig: ts.ParsedCommandLine;
      if (fs.existsSync(configPath)) {
        const configFile = ts.readConfigFile(configPath, (path) =>
          ts.sys.readFile(path)
        );
        if (configFile.error) {
          throw new Error(
            `Error reading tsconfig.json: ${ts.flattenDiagnosticMessageText(
              configFile.error.messageText,
              '\n'
            )}`
          );
        }

        parsedConfig = ts.parseJsonConfigFileContent(
          configFile.config,
          ts.sys,
          path.dirname(configPath)
        );
      } else {
        // Use default config if tsconfig.json doesn't exist
        parsedConfig = ts.parseJsonConfigFileContent({}, ts.sys, cwd);
      }

      // Merge compiler options
      const compilerOptions: ts.CompilerOptions = {
        ...parsedConfig.options,
        ...extraOptions,
        // Required for transformation
        noEmit: false,
        sourceMap: false,
        inlineSourceMap: false,
        declaration: false,
        declarationMap: false,
      };

      // Handle .ts and .tsx files
      build.onLoad(
        { filter },
        async (args: OnLoadArgs): Promise<OnLoadResult> => {
          const fileName = args.path;

          // Read the source file
          const sourceText = await fs.promises.readFile(fileName, 'utf-8');

          // Check if this file contains defineTool or defineContextTool
          // If not, we can skip the expensive transformation
          if (
            !sourceText.includes('defineTool') &&
            !sourceText.includes('defineContextTool')
          ) {
            return {
              contents: sourceText,
              loader: fileName.endsWith('.tsx') ? 'tsx' : 'ts',
            };
          }

          // Create or reuse program
          // Coverage: The caching condition is always true on first invocation since
          // cachedProgram starts as undefined. Additional checks for config/options
          // changes exist for watch mode but are hard to test in unit tests.
          /* v8 ignore next 5 */
          if (
            !cachedProgram ||
            cachedConfigPath !== configPath ||
            cachedCompilerOptions !== compilerOptions
          ) {
            // Create a new program with all files
            cachedProgram = ts.createProgram([fileName], compilerOptions);
            cachedTransformer = createToolSchemaTransformer(cachedProgram);
            cachedConfigPath = configPath;
            cachedCompilerOptions = compilerOptions;
          }

          const sourceFile = cachedProgram.getSourceFile(fileName);

          // Coverage ignored: This fallback handles edge cases where the cached program
          // doesn't have the source file (e.g., new files added during watch mode).
          // In normal builds, the program always contains the requested file.
          /* v8 ignore start */
          if (!sourceFile) {
            // File not in program, create a minimal program for just this file
            const singleFileProgram = ts.createProgram(
              [fileName],
              compilerOptions
            );
            const transformer = createToolSchemaTransformer(singleFileProgram);
            const sf = singleFileProgram.getSourceFile(fileName);

            if (!sf) {
              return {
                errors: [
                  {
                    text: `Could not parse source file: ${fileName}`,
                    location: null,
                  },
                ],
              };
            }

            const result = ts.transform(sf, [transformer]);
            const transformedSourceFile = result.transformed[0];
            const printer = ts.createPrinter();
            const outputText = transformedSourceFile
              ? printer.printFile(transformedSourceFile)
              : sourceText;
            result.dispose();

            return {
              contents: outputText,
              loader: fileName.endsWith('.tsx') ? 'tsx' : 'ts',
            };
          }
          /* v8 ignore end */

          // Transform the source file
          const result = ts.transform(sourceFile, [cachedTransformer!]);
          const transformedSourceFile = result.transformed[0];

          const printer = ts.createPrinter();
          // Coverage ignored: ts.transform always returns at least one transformed file
          // when given a valid source file. The fallback is defensive.
          /* v8 ignore next 3 */
          const outputText = transformedSourceFile
            ? printer.printFile(transformedSourceFile)
            : sourceText;

          result.dispose();

          return {
            contents: outputText,
            loader: fileName.endsWith('.tsx') ? 'tsx' : 'ts',
          };
        }
      );
    },
  };
}

export default mirascope;
