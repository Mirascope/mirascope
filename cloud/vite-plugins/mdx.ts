/**
 * Vite plugin for MDX file imports
 *
 * This plugin transforms `.mdx` files into importable ES modules at build time.
 *
 * Features:
 * - Parses YAML frontmatter from MDX files
 * - Generates table of contents from headings
 * - Compiles MDX to JSX using @mdx-js/mdx
 * - Adds syntax highlighting with rehype-pretty-code
 * - Exports a single `mdx` named export containing the component and metadata
 * - Supports Hot Module Replacement (HMR) in development
 *
 * Usage:
 * ```typescript
 * import { mdx } from "@/content/docs/v1/test.mdx";
 *
 * // mdx is a React component with metadata attached:
 * // - mdx.frontmatter: { title, description, etc. }
 * // - mdx.tableOfContents: [{ id, text, level }, ...]
 * // - mdx.content: string (raw MDX without frontmatter)
 * ```
 */

import type { Plugin } from "vite";
import fs from "node:fs";
import { compileMDXContent } from "../app/lib/content/mdx-compile";

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
        // Read the MDX file content
        const rawContent = fs.readFileSync(id, "utf-8");

        // Compile MDX using shared utility
        const { jsxCode, frontmatter, tableOfContents, content } =
          await compileMDXContent(rawContent);

        // Export as a named export 'mdx' containing component and metadata
        const moduleCode = `
${jsxCode}

// Export mdx object with component and metadata
export const mdx = Object.assign(MDXContent, {
  frontmatter: ${JSON.stringify(frontmatter)},
  tableOfContents: ${JSON.stringify(tableOfContents)},
  content: ${JSON.stringify(content)}
});
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
