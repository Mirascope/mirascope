/**
 * TypeScript transformer for Mirascope tool schema injection.
 *
 * This module provides a TypeScript transformer that automatically
 * generates JSON schemas from type parameters in `defineTool<T>()` calls.
 *
 * ## Usage with ts-patch
 *
 * 1. Install ts-patch: `npm install -D ts-patch`
 * 2. Patch TypeScript: `npx ts-patch install`
 * 3. Add to your `tsconfig.json`:
 *
 * ```json
 * {
 *   "compilerOptions": {
 *     "plugins": [
 *       { "transform": "mirascope/transform" }
 *     ]
 *   }
 * }
 * ```
 *
 * 4. Use `tspc` instead of `tsc`
 *
 * ## Usage with Vite
 *
 * ```typescript
 * // vite.config.ts
 * import { defineConfig } from "vite";
 * import { mirascope } from "mirascope/vite";
 *
 * export default defineConfig({
 *   plugins: [mirascope()]
 * });
 * ```
 *
 * ## Usage with esbuild
 *
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
 *
 * ## What it does
 *
 * Transforms this:
 * ```typescript
 * const getWeather = defineTool<{ city: string }>({
 *   name: "get_weather",
 *   description: "Get weather for a city",
 *   tool: ({ city }) => ({ temp: 72 }),
 * });
 * ```
 *
 * Into this:
 * ```typescript
 * const getWeather = defineTool<{ city: string }>({
 *   name: "get_weather",
 *   description: "Get weather for a city",
 *   tool: ({ city }) => ({ temp: 72 }),
 *   __schema: {
 *     type: "object",
 *     properties: { city: { type: "string" } },
 *     required: ["city"],
 *     additionalProperties: false
 *   },
 * });
 * ```
 */

export {
  createToolSchemaTransformer,
  default as transformer,
} from "@/transform/transformer";

export {
  typeToJsonSchema,
  typeToToolParameterSchema,
  createConversionContext,
} from "@/transform/type-to-schema";

// Shared compilation utilities
export {
  needsTransform,
  getCompilerOptions,
  createProgramForFile,
} from "@/transform/compile";

// Plugin exports
export {
  vitePlugin,
  esbuildPlugin,
  type MirascopeVitePluginOptions,
  type MirascopeEsbuildPluginOptions,
  type TransformerConfig,
} from "@/transform/plugins";
