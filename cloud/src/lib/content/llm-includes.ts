/**
 * LLM Content Include Functions
 *
 * Build-time functions for creating LLMContent instances from filesystem sources.
 * These functions handle MDX processing, frontmatter parsing, and content wrapping.
 */

import fs from "fs";
import path from "path";
import { getAllDocInfo } from "./content";
import { preprocessMdx } from "./mdx-preprocessing";
import type { DocInfo } from "./spec";
import { LLMContent } from "./llm-content";
import { BASE_URL } from "@/src/lib/constants/site";

/**
 * Generate a slug from a route path
 * e.g., "/docs/mirascope/learn/calls" -> "docs-mirascope-learn-calls"
 */
function generateSlugFromRoute(routePath: string): string {
  return routePath
    .replace(/^\/+|\/+$/g, "") // Remove leading/trailing slashes
    .replace(/\//g, "-") // Replace slashes with hyphens
    .toLowerCase();
}

/**
 * Create LLMContent from a single DocInfo by reading and processing the MDX file
 */
function createLLMContentFromDoc(doc: DocInfo, docsRoot?: string): LLMContent {
  const root = docsRoot || path.join(process.cwd(), "content", "docs");
  const filePath = path.join(root, `${doc.path}.mdx`);

  if (!fs.existsSync(filePath)) {
    throw new Error(`Required doc file not found: ${filePath}`);
  }

  const { frontmatter, content } = preprocessMdx(filePath);
  // Build final formatted content with ContentSection wrapper
  let wrappedContent = `<Content`;

  if (frontmatter.title) {
    wrappedContent += ` title="${frontmatter.title}"`;
  }

  if (frontmatter.description) {
    wrappedContent += ` description="${frontmatter.description}"`;
  }

  wrappedContent += ` url="${BASE_URL}${doc.routePath}"`;
  wrappedContent += `>\n\n`;
  wrappedContent += content;
  wrappedContent += `\n\n</Content>`;

  return LLMContent.fromRawContent({
    slug: generateSlugFromRoute(doc.routePath),
    title: frontmatter.title || doc.label,
    description: frontmatter.description,
    content: wrappedContent,
    route: doc.routePath,
  });
}

/**
 * Filter docs based on pattern matching
 */
function filterDocsByPattern(
  docs: DocInfo[],
  pattern: string,
  type: "exact" | "directory" | "tree",
): DocInfo[] {
  const normalizedPattern = pattern.replace(/^\/+|\/+$/g, "");

  return docs.filter((doc) => {
    const normalizedPath = doc.path.replace(/^\/+|\/+$/g, "");

    switch (type) {
      case "exact":
        return normalizedPath === normalizedPattern.replace(/\.mdx$/, "");

      case "directory":
        // Match direct children only (no subdirectories)
        if (!normalizedPath.startsWith(normalizedPattern)) return false;
        const remainder = normalizedPath.slice(normalizedPattern.length);
        return remainder.startsWith("/") && !remainder.slice(1).includes("/");

      case "tree":
        // Match all descendants recursively
        return normalizedPath.startsWith(normalizedPattern);

      default:
        return false;
    }
  });
}

/**
 * Include functions for creating LLMContent from filesystem sources
 */
export const include = {
  /**
   * Include a single specific document by exact path
   * Returns a single LLMContent instance
   */
  file: (pattern: string, docsRoot?: string): LLMContent => {
    const allDocs = getAllDocInfo();
    const matchingDocs = filterDocsByPattern(allDocs, pattern, "exact");

    if (matchingDocs.length === 0) {
      throw new Error(`No document found for pattern: ${pattern}`);
    }

    if (matchingDocs.length > 1) {
      throw new Error(`Multiple documents found for exact pattern: ${pattern}`);
    }

    return createLLMContentFromDoc(matchingDocs[0], docsRoot);
  },

  /**
   * Include direct children of a directory (no subdirectories)
   * Returns an array of LLMContent instances
   */
  directory: (pattern: string, docsRoot?: string): LLMContent[] => {
    const allDocs = getAllDocInfo();
    const matchingDocs = filterDocsByPattern(allDocs, pattern, "directory");

    if (matchingDocs.length === 0) {
      throw new Error(`No documents found for directory pattern: ${pattern}`);
    }

    return matchingDocs.map((doc) => createLLMContentFromDoc(doc, docsRoot));
  },

  /**
   * Include all content recursively under a path (flat list)
   * Returns an array of LLMContent instances
   */
  flatTree: (pattern: string, docsRoot?: string): LLMContent[] => {
    const allDocs = getAllDocInfo();
    const matchingDocs = filterDocsByPattern(allDocs, pattern, "tree");

    if (matchingDocs.length === 0) {
      throw new Error(`No documents found for flatTree pattern: ${pattern}`);
    }

    return matchingDocs.map((doc) => createLLMContentFromDoc(doc, docsRoot));
  },
};
