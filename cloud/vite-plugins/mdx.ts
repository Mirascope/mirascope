/**
 * Vite plugin for MDX file imports
 *
 * This plugin transforms `.mdx` files into importable ES modules at build time.
 * It exports serializable preprocessed data that can be compiled at runtime.
 *
 * Features:
 * - Parses YAML frontmatter from MDX files
 * - Generates table of contents from headings
 * - Resolves CodeExample directives by inlining code files
 * - Exports serializable PreprocessedMDX data (not compiled code)
 * - Supports Hot Module Replacement (HMR) in development
 *
 * Usage:
 * ```typescript
 * import mdx from "@/content/docs/v1/test.mdx";
 *
 * // mdx is a PreprocessedMDX object (serializable JSON):
 * // - mdx.frontmatter: { title, description, etc. }
 * // - mdx.tableOfContents: [{ id, text, level }, ...]
 * // - mdx.content: string (raw MDX with frontmatter stripped)
 * //
 * // The content is compiled at runtime using compileMDXContent()
 * // and evaluated using runSync() in the renderer.
 * ```
 */

import type { Plugin } from "vite";
import { preprocessMdx } from "../app/lib/content/mdx-preprocessing";

export function viteMDX(): Plugin {
  return {
    name: "vite-plugin-mdx",

    // Transform .mdx files into importable modules
    async transform(_code, id) {
      // Only process .mdx files
      if (!id.endsWith(".mdx")) {
        return null;
      }

      try {
        // Read the preprocessed MDX file examples inlined into content
        const preprocessedMdx = await preprocessMdx(id);

        // Export as default export containing serializable preprocessed data
        const moduleCode = `
// Export preprocessed MDX
/** @type {import('../app/lib/mdx/types').PreprocessedMDX} */
export default ${JSON.stringify(preprocessedMdx)};
        `.trim();

        return {
          code: moduleCode,
          map: null,
        };
      } catch (error) {
        console.error(`Error processing MDX file ${id}:`, error);
        throw error;
      }
    },

    // Enable HMR for .mdx files
    handleHotUpdate({ file, server }) {
      if (file.endsWith(".mdx")) {
        console.log(`[mdx] Hot reloading ${file}`);
        const module = server.moduleGraph.getModuleById(file);
        if (module) {
          server.moduleGraph.invalidateModule(module);
        }
        server.ws.send({
          type: "full-reload",
          path: "*",
        });
      }
    },
  };
}
