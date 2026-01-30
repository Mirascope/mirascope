/**
 * Build system plugins for the Mirascope TypeScript transformer.
 *
 * These plugins integrate the tool schema transformer with various
 * build tools, ensuring type information is available during compilation.
 */

export { mirascope as vitePlugin } from "./vite";
export type { MirascopeVitePluginOptions } from "./vite";

export { mirascope as esbuildPlugin } from "./esbuild";
export type { MirascopeEsbuildPluginOptions } from "./esbuild";

export type { TransformerConfig } from "./types";
