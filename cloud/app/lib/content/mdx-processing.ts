import { Effect } from "effect";
import remarkGfm from "remark-gfm";
import { compile } from "@mdx-js/mdx";
import { rehypeCodeMeta } from "./rehype-code-meta";
import type { TOCItem } from "@/app/components/blocks/table-of-contents";
import { extractHeadings } from "@/app/lib/mdx/heading-utils";
import { ContentError } from "./errors";

/**
 * Result of frontmatter parsing
 */
export interface FrontmatterResult {
  frontmatter: Record<string, unknown>;
  content: string;
}

/**
 * Result of MDX processing
 */
export interface ProcessedContent {
  content: string;
  frontmatter: Record<string, unknown>;
  code: string;
  tableOfContents: TOCItem[];
}

/**
 * Parses frontmatter from document content
 *
 * @param content - The document content with frontmatter
 * @returns An object containing the parsed frontmatter and the cleaned content
 */
export function parseFrontmatter(content: string): FrontmatterResult {
  try {
    // Check for content with frontmatter pattern
    if (!content.startsWith("---")) {
      return {
        frontmatter: {},
        content,
      };
    }

    const parts = content.split("---");

    // Handle case with empty frontmatter (---\n---)
    if (parts.length >= 3 && parts[1].trim() === "") {
      return {
        frontmatter: {},
        content: parts.slice(2).join("---").trimStart(),
      };
    }

    // Normal case with frontmatter content
    if (parts.length >= 3) {
      const frontmatterStr = parts[1].trim();
      const contentParts = parts.slice(2).join("---");
      const cleanContent = contentParts.trimStart();

      // Parse frontmatter into key-value pairs
      const frontmatter: Record<string, unknown> = {};

      // Split by lines and process each line
      frontmatterStr.split("\n").forEach((line) => {
        const trimmedLine = line.trim();
        if (!trimmedLine) return; // Skip empty lines

        // Look for key: value format
        const colonIndex = trimmedLine.indexOf(":");
        if (colonIndex > 0) {
          const key = trimmedLine.slice(0, colonIndex).trim();
          const value = trimmedLine.slice(colonIndex + 1).trim();

          // Remove quotes if present
          frontmatter[key] = value.replace(/^["'](.*)["']$/, "$1");
        }
      });

      return {
        frontmatter,
        content: cleanContent,
      };
    }

    // If no proper frontmatter found, return original content
    return {
      frontmatter: {},
      content,
    };
  } catch {
    // In case of parsing error, return the original content
    return {
      frontmatter: {},
      content,
    };
  }
}

/**
 * Merges frontmatter from different sources with optional overwriting
 *
 * @param target - The target frontmatter object
 * @param source - The source frontmatter object
 * @param overwrite - Whether to overwrite existing values (default: false)
 * @returns The merged frontmatter
 */
export function mergeFrontmatter(
  target: Record<string, unknown>,
  source: Record<string, unknown>,
  overwrite = false,
): Record<string, unknown> {
  const result = { ...target };

  for (const [key, value] of Object.entries(source)) {
    // Only add if the key doesn't exist or overwrite is true
    if (overwrite || !(key in result)) {
      result[key] = value;
    }
  }

  return result;
}

/**
 * MDX processing that parses frontmatter and compiles MDX content
 *
 * @param rawContent - Raw content string with frontmatter
 * @param options - Additional processing options
 * @returns Effect that yields processed content with frontmatter, content and compiled code
 */
export function processMDXContent(
  rawContent: string,
  options?: {
    path?: string; // Optional path for better error reporting
  },
): Effect.Effect<ProcessedContent, ContentError> {
  return Effect.gen(function* () {
    if (!rawContent) {
      return yield* Effect.fail(
        new ContentError({
          message: "Empty content provided",
          path: options?.path,
        }),
      );
    }

    // Extract frontmatter (pure function, won't throw)
    const { frontmatter, content } = parseFrontmatter(rawContent);

    // Extract table of contents (pure function)
    const tableOfContents = extractHeadings(content);

    // Compile MDX content using Effect.tryPromise
    const compiledResult = yield* Effect.tryPromise({
      try: () =>
        compile(content, {
          outputFormat: "function-body",
          providerImportSource: "@mdx-js/react",
          development: process.env.NODE_ENV !== "production",
          remarkPlugins: [remarkGfm],
          rehypePlugins: [rehypeCodeMeta],
        }),
      catch: (error) =>
        new ContentError({
          message: `Error processing MDX content: ${error instanceof Error ? error.message : String(error)}`,
          path: options?.path,
          cause: error,
        }),
    });

    // Return processed content
    return {
      content,
      frontmatter,
      code: String(compiledResult),
      tableOfContents,
    };
  });
}
