import { readFile } from "fs/promises";
import { join, resolve } from "path";

/**
 * Options for MDX preprocessing
 */
export interface PreprocessMdxOptions {
  basePath: string; // Base path to resolve @/ file paths
  filePath?: string; // Current file path for error reporting
}

function resolveExampleBasePath(filePath: string): string {
  const pathsToTry = ["content/docs/v1", "content/docs", "content"];

  for (const pathSegment of pathsToTry) {
    if (filePath.includes(pathSegment)) {
      const index = filePath.indexOf(pathSegment);
      return filePath.slice(0, index + pathSegment.length);
    }
  }

  throw new Error(`Could not resolve example base path for: ${filePath}`);
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
        const resolvedPath = file.startsWith("@/")
          ? join(basePath, file.slice(2))
          : resolve(basePath, file);

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
export async function preprocessMdx(filePath: string): Promise<string> {
  const contentWithCodeExamples = await processCodeExamples(filePath);

  return contentWithCodeExamples;
}
