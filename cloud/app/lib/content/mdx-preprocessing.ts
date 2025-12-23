import { join, resolve } from "path";
import { Effect } from "effect";
import { FileSystem } from "@effect/platform";
import { ContentError } from "./errors";
import { parseFrontmatter } from "./mdx-processing";

/**
 * Options for MDX preprocessing
 */
export interface PreprocessMdxOptions {
  basePath: string; // Base path to resolve @/ file paths
  filePath?: string; // Current file path for error reporting
}

/**
 * Result of MDX preprocessing with code examples resolved
 */
export interface PreprocessedMdxResult {
  frontmatter: Record<string, unknown>;
  content: string; // Body content only (no frontmatter)
  fullContent: string; // Full file content with frontmatter
}

/**
 * Resolves the base path for code examples based on the file path.
 * This is a pure function that determines where to look for example files.
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
 * Infers programming language from file path.
 * This is a pure function.
 */
export function inferLanguageFromPath(filePath: string): string {
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
 * Regex to match <CodeExample file="..." /> with optional lines, lang, and highlight attributes
 */
const CODE_EXAMPLE_REGEX =
  /<CodeExample\s+file="([^"]+)"(?:\s+lines="([^"]+)")?(?:\s+lang="([^"]+)")?(?:\s+highlight="([^"]+)")?\s*\/>/g;

/**
 * Represents a CodeExample match found in the MDX content
 */
interface CodeExampleMatch {
  fullMatch: string;
  file: string;
  lines?: string;
  lang?: string;
  highlight?: string;
}

/**
 * Extracts all CodeExample matches from content.
 * This is a pure function.
 */
function extractCodeExampleMatches(content: string): CodeExampleMatch[] {
  const matches: CodeExampleMatch[] = [];
  let match: RegExpExecArray | null;

  // Reset regex state
  CODE_EXAMPLE_REGEX.lastIndex = 0;

  while ((match = CODE_EXAMPLE_REGEX.exec(content)) !== null) {
    matches.push({
      fullMatch: match[0],
      file: match[1],
      lines: match[2],
      lang: match[3],
      highlight: match[4],
    });
  }

  return matches;
}

/**
 * Processes line ranges in content (e.g., "1-5" or "10-20").
 * This is a pure function.
 */
function processLineRange(content: string, lines: string): string {
  const [start, end] = lines.split("-").map((n) => parseInt(n.trim(), 10));
  if (!isNaN(start) && !isNaN(end)) {
    const fileLines = content.split("\n");
    return fileLines.slice(start - 1, end).join("\n");
  }
  return content;
}

/**
 * Formats content as a code block with optional language and highlighting.
 * This is a pure function.
 */
function formatAsCodeBlock(
  content: string,
  lang: string,
  highlight?: string,
): string {
  const metaInfo = highlight ? ` {${highlight}}` : "";
  return `\`\`\`${lang}${metaInfo}\n${content}\n\`\`\``;
}

/**
 * Reads a single code example file and returns its formatted content.
 */
const readCodeExample = (
  basePath: string,
  match: CodeExampleMatch,
  sourceFilePath: string,
): Effect.Effect<
  { fullMatch: string; replacement: string },
  ContentError,
  FileSystem.FileSystem
> =>
  Effect.gen(function* () {
    const fs = yield* FileSystem.FileSystem;

    // Resolve the file path
    const resolvedPath = match.file.startsWith("@/")
      ? join(basePath, match.file.slice(2))
      : resolve(basePath, match.file);

    // Read the example file
    const exampleContent = yield* fs.readFileString(resolvedPath).pipe(
      Effect.mapError(
        (error) =>
          new ContentError({
            message: `Error reading code example file ${resolvedPath}: ${error.message}`,
            path: sourceFilePath,
            cause: error,
          }),
      ),
    );

    // Process lines if specified
    const processedContent = match.lines
      ? processLineRange(exampleContent, match.lines)
      : exampleContent;

    // Infer language from file extension if not provided
    const lang = match.lang || inferLanguageFromPath(resolvedPath);

    // Format as code block
    const replacement = formatAsCodeBlock(
      processedContent,
      lang,
      match.highlight,
    );

    return { fullMatch: match.fullMatch, replacement };
  });

/**
 * Processes CodeExample directives in MDX content by replacing them with actual code blocks.
 * Returns an Effect that requires FileSystem.
 */
const processCodeExamples = (
  filePath: string,
  content: string,
): Effect.Effect<string, ContentError, FileSystem.FileSystem> =>
  Effect.gen(function* () {
    // Determine the base path for resolving example files
    const basePath = resolveExampleBasePath(filePath);

    // Extract all code example matches
    const matches = extractCodeExampleMatches(content);

    // If no matches, return content as-is
    if (matches.length === 0) {
      return content;
    }

    // Read all code examples in parallel
    const replacements = yield* Effect.all(
      matches.map((match) => readCodeExample(basePath, match, filePath)),
      { concurrency: "unbounded" },
    );

    // Apply all replacements
    let result = content;
    for (const { fullMatch, replacement } of replacements) {
      result = result.replace(fullMatch, replacement);
    }

    return result;
  });

/**
 * Reads a file and processes CodeExample directives.
 * Returns an Effect that requires FileSystem.
 */
const readAndProcessFile = (
  filePath: string,
): Effect.Effect<string, ContentError, FileSystem.FileSystem> =>
  Effect.gen(function* () {
    const fs = yield* FileSystem.FileSystem;

    // Read the main file
    const content = yield* fs.readFileString(filePath).pipe(
      Effect.mapError(
        (error) =>
          new ContentError({
            message: `Error reading MDX file ${filePath}: ${error.message}`,
            path: filePath,
            cause: error,
          }),
      ),
    );

    // Process code examples
    return yield* processCodeExamples(filePath, content);
  });

/**
 * Preprocesses MDX content by resolving CodeExample directives and parsing frontmatter.
 * This is the main entry point for preprocessing.
 *
 * @param filePath - Path to the MDX file to preprocess
 * @returns Effect that yields PreprocessedMdxResult
 */
export const preprocessMdx = (
  filePath: string,
): Effect.Effect<PreprocessedMdxResult, ContentError, FileSystem.FileSystem> =>
  Effect.gen(function* () {
    // Read and process the file (resolves code examples)
    const contentWithCodeExamples = yield* readAndProcessFile(filePath);

    // Parse frontmatter (pure function)
    const { frontmatter, content } = parseFrontmatter(contentWithCodeExamples);

    return {
      frontmatter,
      content,
      fullContent: contentWithCodeExamples,
    };
  });
