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
import { compile } from "@mdx-js/mdx";
import remarkGfm from "remark-gfm";
import rehypePrettyCode from "rehype-pretty-code";
import fs from "node:fs";

/**
 * Parse frontmatter from MDX content
 */
function parseFrontmatter(content: string): {
  frontmatter: Record<string, string>;
  content: string;
} {
  if (!content.startsWith("---")) {
    return { frontmatter: {}, content };
  }

  const parts = content.split("---");

  if (parts.length >= 3 && parts[1].trim() === "") {
    return {
      frontmatter: {},
      content: parts.slice(2).join("---").trimStart(),
    };
  }

  if (parts.length >= 3) {
    const frontmatterStr = parts[1].trim();
    const contentParts = parts.slice(2).join("---");
    const cleanContent = contentParts.trimStart();

    const frontmatter: Record<string, string> = {};

    frontmatterStr.split("\n").forEach((line) => {
      const trimmedLine = line.trim();
      if (!trimmedLine) return;

      const colonIndex = trimmedLine.indexOf(":");
      if (colonIndex > 0) {
        const key = trimmedLine.slice(0, colonIndex).trim();
        const value = trimmedLine.slice(colonIndex + 1).trim();
        frontmatter[key] = value.replace(/^["'](.*)["']$/, "$1");
      }
    });

    return { frontmatter, content: cleanContent };
  }

  return { frontmatter: {}, content };
}

/**
 * Extract table of contents from MDX content
 */
function extractTOC(content: string): Array<{
  id: string;
  text: string;
  level: number;
}> {
  const headingRegex = /^(#{1,6})\s+(.+)$/gm;
  const toc: Array<{ id: string; text: string; level: number }> = [];
  let match;

  while ((match = headingRegex.exec(content)) !== null) {
    const level = match[1].length;
    const text = match[2].trim();
    const id = text
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "");

    toc.push({ id, text, level });
  }

  return toc;
}

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

        // Parse frontmatter
        const { frontmatter, content } = parseFrontmatter(rawContent);

        // Extract TOC
        const tableOfContents = extractTOC(content);

        // Compile MDX to JSX
        const result = await compile(content, {
          development: process.env.NODE_ENV === "development",
          outputFormat: "program", // Output as a full ESM program
          remarkPlugins: [remarkGfm],
          rehypePlugins: [
            [
              rehypePrettyCode,
              {
                theme: "github-dark",
                keepBackground: false,
              },
            ],
          ],
        });

        let jsxCode = String(result);

        // Remove ALL default exports from MDX output to avoid conflicts
        jsxCode = jsxCode.replace(/export\s+default\s+MDXContent;?\s*/g, "");

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
