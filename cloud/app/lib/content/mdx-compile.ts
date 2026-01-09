/**
 * MDX Compilation Utilities
 *
 * Shared MDX compilation logic used by both the vite plugin and tests.
 */

import { compile, type CompileOptions } from "@mdx-js/mdx";
import remarkGfm from "remark-gfm";
import rehypePrettyCode from "rehype-pretty-code";
import type { ProcessedMDX, Frontmatter } from "@/app/lib/mdx/types";
import type { TOCItem } from "@/app/lib/content/types";
import { parseFrontmatter } from "./frontmatter";
import { extractTOC } from "./toc";

export interface CompileMDXOptions {
  /** Skip syntax highlighting (faster for tests) */
  skipHighlighting?: boolean;
}

export interface CompiledMDXResult {
  /** The compiled JSX code string */
  jsxCode: string;
  /** Extracted frontmatter */
  frontmatter: Record<string, string>;
  /** Table of contents */
  tableOfContents: TOCItem[];
  /** Raw content without frontmatter */
  content: string;
}

/**
 * Compile MDX content to JSX
 *
 * This is the core compilation logic shared between the vite plugin and tests.
 */
export async function compileMDXContent(
  rawContent: string,
  options: CompileMDXOptions = {},
): Promise<CompiledMDXResult> {
  // Parse frontmatter
  const { frontmatter, content } = parseFrontmatter(rawContent);

  // Extract TOC
  const tableOfContents = extractTOC(content);

  // Build compile options
  const compileOptions: CompileOptions = {
    development: process.env.NODE_ENV === "development",
    outputFormat: "program",
    remarkPlugins: [remarkGfm],
    rehypePlugins: options.skipHighlighting
      ? []
      : [
          [
            rehypePrettyCode,
            {
              theme: "github-dark",
              keepBackground: false,
            },
          ],
        ],
  };

  // Compile MDX to JSX
  const result = await compile(content, compileOptions);

  let jsxCode = String(result);

  // Remove ALL default exports from MDX output to avoid conflicts
  jsxCode = jsxCode.replace(/export\s+default\s+MDXContent;?\s*/g, "");

  return {
    jsxCode,
    frontmatter,
    tableOfContents,
    content,
  };
}

/**
 * Create a ProcessedMDX object from content and metadata
 *
 * This creates a mock MDX component with the metadata attached,
 * useful for testing without needing to actually render the component.
 */
export function createProcessedMDX(
  content: string,
  frontmatter: Frontmatter,
  tableOfContents: TOCItem[] = [],
): ProcessedMDX {
  // Create a simple component that renders null (for testing)
  const MockComponent = () => null;
  return Object.assign(MockComponent, {
    content,
    frontmatter,
    tableOfContents,
  }) as ProcessedMDX;
}
