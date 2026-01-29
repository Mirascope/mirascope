/**
 * Vite plugin for Mirascope tool schema transformation.
 *
 * This plugin uses @rollup/plugin-typescript under the hood to ensure
 * access to TypeScript's type checker for schema generation.
 */

import type { Plugin } from 'vite';
import type ts from 'typescript';
import typescript from '@rollup/plugin-typescript';
import type { RollupTypescriptOptions } from '@rollup/plugin-typescript';
import { createToolSchemaTransformer } from '../transformer';

export interface MirascopeVitePluginOptions {
  /**
   * Options to pass to @rollup/plugin-typescript.
   * Note: The 'transformers' option will be merged with the Mirascope transformer.
   */
  typescript?: Omit<RollupTypescriptOptions, 'transformers'>;

  /**
   * Additional transformers to run alongside the Mirascope transformer.
   */
  additionalTransformers?: ts.CustomTransformers;

  /**
   * File filter pattern. Defaults to /\.(ts|tsx)$/
   */
  include?: RegExp | string | string[];

  /**
   * Files to exclude. Defaults to /node_modules/
   */
  exclude?: RegExp | string | string[];
}

/**
 * Vite plugin that applies the Mirascope tool schema transformer.
 *
 * This plugin uses @rollup/plugin-typescript under the hood to ensure
 * access to TypeScript's type checker for schema generation.
 *
 * @example
 * ```typescript
 * // vite.config.ts
 * import { defineConfig } from 'vite';
 * import { mirascope } from 'mirascope/vite';
 *
 * export default defineConfig({
 *   plugins: [mirascope()]
 * });
 * ```
 */
export function mirascope(options: MirascopeVitePluginOptions = {}): Plugin[] {
  const {
    typescript: tsOptions = {},
    additionalTransformers,
    include = /\.(ts|tsx)$/,
    exclude = /node_modules/,
  } = options;

  // Create the transformers function for @rollup/plugin-typescript
  // Coverage ignored: This callback is invoked by @rollup/plugin-typescript
  // during actual Vite builds, not during plugin creation.
  /* v8 ignore start */
  const transformers = (program: ts.Program): ts.CustomTransformers => {
    const mirascopeTransformer = createToolSchemaTransformer(program);

    return {
      before: [mirascopeTransformer, ...(additionalTransformers?.before ?? [])],
      after: additionalTransformers?.after,
      afterDeclarations: additionalTransformers?.afterDeclarations,
    };
  };
  /* v8 ignore end */

  return [
    {
      name: 'mirascope:pre',
      enforce: 'pre',
      config() {
        return {
          esbuild: {
            // Disable esbuild's TypeScript handling for matched files
            // We'll handle them with @rollup/plugin-typescript instead
            include: exclude, // Only let esbuild handle excluded files
            exclude: include, // Exclude our target files from esbuild
          },
        };
      },
    },
    // Cast needed because @rollup/plugin-typescript returns Rollup plugin
    typescript({
      ...tsOptions,
      transformers,
      include: include as string | string[],
      exclude: exclude as string | string[],
    }) as unknown as Plugin,
  ];
}

export default mirascope;
