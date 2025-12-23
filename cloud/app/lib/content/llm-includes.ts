/**
 * LLM Content Include Functions
 *
 * Build-time functions for creating LLMContent instances from filesystem sources.
 * These functions handle MDX processing, frontmatter parsing, and content wrapping.
 *
 * Note: These functions use synchronous Node.js fs operations because:
 * 1. LLM content is generated at module import time (top-level)
 * 2. Module imports must be synchronous in JavaScript/TypeScript
 * 3. The Effect-based preprocessMdx uses async operations that can't run with runSync
 */

import fs from "fs";
import path from "path";
import { getAllDocInfo } from "./content";
import { parseFrontmatter } from "./mdx-processing";
import { inferLanguageFromPath } from "./mdx-preprocessing";
import type { DocInfo } from "./spec";
import { LLMContent } from "./llm-content";
import { BASE_URL } from "@/app/lib/site";

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
 * Resolves the base path for code examples based on the file path.
 */
function resolveExampleBasePath(filePath: string): string {
  const pathsToTry = [
    "content/docs/mirascope/v2",
    "content/docs/mirascope",
    "content/docs",
    "content",
  ];

  for (const pathSegment of pathsToTry) {
    if (filePath.includes(pathSegment)) {
      const index = filePath.indexOf(pathSegment);
      return filePath.slice(0, index + pathSegment.length);
    }
  }

  throw new Error(`Could not resolve example base path for: ${filePath}`);
}

/**
 * Regex to match <CodeExample file="..." /> with optional lines, lang, and highlight attributes
 */
const CODE_EXAMPLE_REGEX =
  /<CodeExample\s+file="([^"]+)"(?:\s+lines="([^"]+)")?(?:\s+lang="([^"]+)")?(?:\s+highlight="([^"]+)")?\s*\/>/g;

/**
 * Process CodeExample directives synchronously
 */
function processCodeExamplesSync(filePath: string, content: string): string {
  const basePath = resolveExampleBasePath(filePath);

  // Reset regex state
  CODE_EXAMPLE_REGEX.lastIndex = 0;

  return content.replace(
    CODE_EXAMPLE_REGEX,
    (
      _fullMatch: string,
      file: string,
      lines: string | undefined,
      lang: string | undefined,
      highlight: string | undefined,
    ) => {
      // Resolve the file path
      const resolvedPath = file.startsWith("@/")
        ? path.join(basePath, file.slice(2))
        : path.resolve(basePath, file);

      // Read the example file
      if (!fs.existsSync(resolvedPath)) {
        throw new Error(
          `Code example file not found: ${resolvedPath} (referenced from ${filePath})`,
        );
      }
      let exampleContent = fs.readFileSync(resolvedPath, "utf-8");

      // Process lines if specified
      if (lines) {
        const [start, end] = lines
          .split("-")
          .map((n: string) => parseInt(n.trim(), 10));
        if (!isNaN(start) && !isNaN(end)) {
          const fileLines = exampleContent.split("\n");
          exampleContent = fileLines.slice(start - 1, end).join("\n");
        }
      }

      // Infer language from file extension if not provided
      const finalLang = lang || inferLanguageFromPath(resolvedPath);

      // Format as code block
      const metaInfo = highlight ? ` {${highlight}}` : "";
      return `\`\`\`${finalLang}${metaInfo}\n${exampleContent}\n\`\`\``;
    },
  );
}

/**
 * Preprocess MDX file synchronously (for use at module import time)
 */
function preprocessMdxSync(filePath: string): {
  frontmatter: Record<string, unknown>;
  content: string;
} {
  // Read the file
  const rawContent = fs.readFileSync(filePath, "utf-8");

  // Process code examples
  const contentWithCodeExamples = processCodeExamplesSync(filePath, rawContent);

  // Parse frontmatter
  return parseFrontmatter(contentWithCodeExamples);
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

  // Use synchronous preprocessing (required for module-level execution)
  const { frontmatter, content } = preprocessMdxSync(filePath);

  // Build final formatted content with ContentSection wrapper
  let wrappedContent = `<Content`;

  if (frontmatter.title && typeof frontmatter.title === "string") {
    wrappedContent += ` title="${frontmatter.title}"`;
  }

  if (frontmatter.description && typeof frontmatter.description === "string") {
    wrappedContent += ` description="${frontmatter.description}"`;
  }

  wrappedContent += ` url="${BASE_URL}${doc.routePath}"`;
  wrappedContent += `>\n\n`;
  wrappedContent += content;
  wrappedContent += `\n\n</Content>`;

  return LLMContent.fromRawContent({
    slug: generateSlugFromRoute(doc.routePath),
    title: (frontmatter.title as string) || doc.label,
    description: frontmatter.description as string | undefined,
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

      case "directory": {
        // Match direct children only (no subdirectories)
        if (!normalizedPath.startsWith(normalizedPattern)) return false;
        const remainder = normalizedPath.slice(normalizedPattern.length);
        return remainder.startsWith("/") && !remainder.slice(1).includes("/");
      }

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
