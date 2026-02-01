import { readFile } from "fs/promises";
import { join, resolve, normalize } from "path";

import type { PreprocessedMDX } from "../mdx/types";

import { extractHeadings } from "../mdx/heading-utils";
// NOTE: All imports in this file must use relative paths.
// Vite plugins cannot resolve path aliases such as "@/app/...",
// so using aliases here will cause module resolution failures.
// This ensures compatibility in both the vite plugin and other consumers.
import { parseFrontmatter } from "./frontmatter";

/**
 * Options for MDX preprocessing
 */
export interface PreprocessMdxOptions {
  basePath: string; // Base path to resolve @/ file paths
  filePath?: string; // Current file path for error reporting
}

function resolveExampleBasePath(filePath: string): string {
  // Find the cloud/ or content/ directory and resolve to project root (parent of both)
  const cloudIndex = filePath.indexOf("/cloud/");
  if (cloudIndex !== -1) {
    return filePath.slice(0, cloudIndex + 1); // Include trailing slash after removing "cloud/"
  }

  const contentIndex = filePath.indexOf("/content/");
  if (contentIndex !== -1) {
    return filePath.slice(0, contentIndex + 1); // Include trailing slash after removing "content/"
  }

  throw new Error(`Could not resolve example base path for: ${filePath}`);
}

/**
 * Validates and resolves a file path with security checks to prevent directory traversal.
 * Ensures the resolved path stays within the basePath or at most one level up.
 *
 * @param basePath - The base directory to resolve paths from
 * @param filePath - The file path to resolve (may contain .. components)
 * @returns The resolved and validated absolute path
 * @throws Error if the path escapes beyond allowed boundaries
 */
function resolveSecurePath(basePath: string, filePath: string): string {
  // Count the number of actual .. directory traversal components
  // Split by path separators and count standalone ".." entries
  const pathParts = filePath.split(/[/\\]/);
  const parentDirCount = pathParts.filter((part) => part === "..").length;

  // Allow at most one directory traversal up
  if (parentDirCount > 1) {
    throw new Error(
      `Path contains too many directory traversals (${parentDirCount}): ${filePath}. Maximum allowed is 1.`,
    );
  }

  // Resolve the path to get the absolute path
  const resolvedPath = resolve(basePath, filePath);
  const normalizedBasePath = normalize(resolve(basePath));
  const normalizedResolvedPath = normalize(resolvedPath);

  // Ensure the resolved path doesn't escape beyond the basePath
  // Allow at most one level up from basePath
  const basePathParent = resolve(normalizedBasePath, "..");
  const normalizedBasePathParent = normalize(basePathParent);

  // Check if resolved path is within basePath or its parent
  // Use path comparison that works on both Unix and Windows
  const isWithinBasePath =
    normalizedResolvedPath === normalizedBasePath ||
    normalizedResolvedPath.startsWith(normalizedBasePath + "/") ||
    normalizedResolvedPath.startsWith(normalizedBasePath + "\\");

  const isWithinBasePathParent =
    normalizedResolvedPath === normalizedBasePathParent ||
    normalizedResolvedPath.startsWith(normalizedBasePathParent + "/") ||
    normalizedResolvedPath.startsWith(normalizedBasePathParent + "\\");

  if (!isWithinBasePath && !isWithinBasePathParent) {
    throw new Error(
      `Path traversal detected: resolved path "${normalizedResolvedPath}" escapes beyond allowed boundaries (base: "${normalizedBasePath}")`,
    );
  }

  return normalizedResolvedPath;
}

/**
 * Processes CodeExample directives in MDX content by replacing them with actual code blocks
 */
async function processCodeExamples(filePath: string): Promise<string> {
  // Regex to match <CodeExample file="..." /> with optional lines, lang, and highlight attributes
  const codeExampleRegex =
    /<CodeExample\s+file="([^"]+)"(?:\s+lines="([^"]+)")?(?:\s+lang="([^"]+)")?(?:\s+highlight="([^"]+)")?\s*\/>/g;

  const content = await readFile(filePath, "utf-8");
  const basePath = resolveExampleBasePath(filePath);

  // Find all matches first
  const matchesArr = Array.from(content.matchAll(codeExampleRegex));
  const matches = matchesArr.map((match) => ({
    match: match[0],
    file: match[1],
    lines: match[2],
    lang: match[3],
    highlight: match[4],
    index: match.index,
  }));

  // Process all matches asynchronously
  const replacements = await Promise.all(
    matches.map(async ({ file, lines, lang, highlight }) => {
      try {
        // Resolve @/ paths relative to basePath
        // @/ resolves to cloud/ from the project root, so prepend "cloud" when resolving @/ paths
        const resolvedPath = file.startsWith("@/")
          ? resolveSecurePath(basePath, join("cloud", file.slice(2)))
          : resolveSecurePath(basePath, file);

        const exampleContent = await readFile(resolvedPath, "utf-8");

        // Process lines if specified (e.g., "1-5" or "10-20")
        let processedContent = exampleContent;
        if (lines) {
          const [start, end] = lines
            .split("-")
            .map((n) => parseInt(n.trim(), 10));
          if (!isNaN(start) && !isNaN(end)) {
            const fileLines = exampleContent.split("\n");
            // Convert to 0-based indexing and slice
            processedContent = fileLines.slice(start - 1, end).join("\n");
          }
        }

        // Infer language from file extension if not provided
        const inferredLang = lang || inferLanguageFromPath(resolvedPath);

        // Add highlight metadata if provided
        const metaInfo = highlight ? ` {${highlight}}` : "";

        // Return as a code block with optional highlighting
        return `\`\`\`${inferredLang}${metaInfo}\n${processedContent}\n\`\`\``;
      } catch (error) {
        throw new Error(
          `Error processing CodeExample in ${filePath}: ${error instanceof Error ? error.message : String(error)}`,
        );
      }
    }),
  );

  // Replace matches in reverse order to preserve indices
  let result = content;
  for (let i = matches.length - 1; i >= 0; i--) {
    const { match, index } = matches[i];
    result =
      result.slice(0, index) +
      replacements[i] +
      result.slice(index + match.length);
  }

  return result;
}

/**
 * Infers programming language from file path
 */
function inferLanguageFromPath(filePath: string): string {
  const ext = filePath.split(".").pop()?.toLowerCase();
  if (!ext) return "text";

  const langMap: Record<string, string> = {
    py: "python",
    js: "javascript",
    ts: "typescript",
    jsx: "jsx",
    tsx: "tsx",
    json: "json",
    yaml: "yaml",
    yml: "yaml",
    md: "markdown",
    sh: "bash",
    bash: "bash",
    zsh: "bash",
    sql: "sql",
    css: "css",
    html: "html",
    xml: "xml",
    toml: "toml",
    rs: "rust",
    go: "go",
    java: "java",
    c: "c",
    cpp: "cpp",
    h: "c",
    hpp: "cpp",
  };

  return langMap[ext] || "text";
}

/**
 * Preprocesses MDX content by resolving CodeExample directives and parsing frontmatter
 */
export async function preprocessMdx(
  filePath: string,
): Promise<PreprocessedMDX> {
  const contentWithCodeExamples = await processCodeExamples(filePath);
  // Parse frontmatter and get content with frontmatter stripped
  const { frontmatter, content } = parseFrontmatter(contentWithCodeExamples);
  // Extract table of contents from content without frontmatter
  const tableOfContents = extractHeadings(content);

  return {
    frontmatter,
    tableOfContents,
    content,
  };
}
