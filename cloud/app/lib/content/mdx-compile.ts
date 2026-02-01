/**
 * MDX Compilation Utilities
 *
 * Shared MDX compilation logic used by both the vite plugin and tests.
 */

// NOTE: All imports in this file must use relative paths.
// Vite plugins cannot resolve path aliases such as "@/app/...",
// so using aliases here will cause module resolution failures.
// This ensures compatibility in both the vite plugin and other consumers.
import { compile, type CompileOptions } from "@mdx-js/mdx";
import remarkGfm from "remark-gfm";

import { rehypeCodeMeta } from "./rehype-code-meta";

/**
 * Compile MDX content to JSX function body
 *
 * This is the core compilation logic. Uses outputFormat: "function-body"
 * which produces code that can be evaluated with runSync() at runtime.
 */
export async function compileMDXContent(content: string): Promise<string> {
  // Build compile options
  const compileOptions: CompileOptions = {
    outputFormat: "function-body",
    development: process.env.NODE_ENV === "development",
    remarkPlugins: [remarkGfm],
    rehypePlugins: [rehypeCodeMeta],
  };

  // Compile MDX to JSX function body
  const result = await compile(content, compileOptions);

  return String(result);
}
