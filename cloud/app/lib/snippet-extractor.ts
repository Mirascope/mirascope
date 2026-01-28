/**
 * Snippet extraction module.
 *
 * This module provides low-level functions for extracting code snippets from MDX files
 * and generating runnable Python examples.
 */

import * as fs from "fs/promises";
import * as path from "path";
// Import from shared provider config
import { replaceProviderVariables } from "@/app/components/mdx/elements/model-provider-provider";

/**
 * Check if a path exists (async replacement for fs.existsSync)
 */
async function pathExists(filePath: string): Promise<boolean> {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

/**
 * Extract Python snippets from MDX content string
 */
export function extractSnippetsFromContent(content: string): string[] {
  // First, check for any python-* blocks that aren't our supported types
  const pythonPrefixRegex = /```(python-[^`\n {]+)(?:\s*{[^}]+})?\n/g;
  let prefixMatch;
  while ((prefixMatch = pythonPrefixRegex.exec(content)) !== null) {
    const blockType = prefixMatch[1];
    // Only allow python-snippet-concat and python-snippet-skip
    if (
      blockType !== "python-snippet-concat" &&
      blockType !== "python-snippet-skip"
    ) {
      throw new Error(
        `Unsupported Python block type "${blockType}". Only python, python-snippet-concat, and python-snippet-skip are allowed.`,
      );
    }
  }

  // Match Python blocks (regular), python-snippet-concat blocks, and python-snippet-skip blocks
  // Also handles meta directives like ```python{1,2} or ```python {1,2}
  const snippetRegex =
    /```(python|python-snippet-concat|python-snippet-skip)(?:\s*{[^}]+})?\n([\s\S]*?)```/g;
  const snippets: string[] = [];

  // Count lines up to each match
  let match;
  while ((match = snippetRegex.exec(content)) !== null) {
    const blockType = match[1];
    const codeContent = match[2].trim();

    if (blockType === "python-snippet-skip") {
      continue;
    }

    if (blockType === "python-snippet-concat" && snippets.length > 0) {
      // Append to the previous snippet
      snippets[snippets.length - 1] += "\n\n" + codeContent;
    } else {
      // Create a new snippet
      snippets.push(codeContent);
    }
  }

  return snippets;
}

/**
 * Extract Python snippets from an MDX file
 */
export async function extractSnippets(filePath: string): Promise<string[]> {
  const content = await fs.readFile(filePath, "utf-8");

  try {
    return extractSnippetsFromContent(content);
  } catch (error) {
    // Enhance error message with file information
    if (error instanceof Error) {
      throw new Error(`${error.message} (in file ${filePath})`);
    }
    throw error;
  }
}

/**
 * Generate a runnable Python file for a single snippet
 */
export async function generatePythonFile(
  snippet: string,
  outputDir: string,
  index: number,
  baseName: string = "example",
  sourceFilePath: string = "",
): Promise<string> {
  // Replace provider variables using shared function
  const processedSnippet = replaceProviderVariables(snippet, "openai");

  // Ensure the output directory exists
  if (!(await pathExists(outputDir))) {
    await fs.mkdir(outputDir, { recursive: true });
  }

  // Create the output file name with index (provider is always OpenAI)
  const fileName = `${baseName}_${index + 1}.py`;
  const outputFile = path.join(outputDir, fileName);

  // Create the output file content
  // Convert absolute path to one relative to project root
  const projectRoot = process.cwd();
  const relativePath = sourceFilePath.startsWith(projectRoot)
    ? sourceFilePath.substring(projectRoot.length + 1) // +1 to remove the leading slash
    : sourceFilePath;

  const content = `# Example ${index + 1}
# Source: ${relativePath}
# This file is auto-generated; any edits should be made in the source file

${processedSnippet}
`;

  // Write the file
  await fs.writeFile(outputFile, content);

  return outputFile;
}

/**
 * Process a single MDX file for a given provider
 */
export async function processFile(mdxFile: string): Promise<string[]> {
  if (!(await pathExists(mdxFile))) {
    console.error(`Error: File ${mdxFile} not found`);
    return [];
  }

  // Extract snippets and headings
  const snippets = await extractSnippets(mdxFile);

  if (snippets.length === 0) {
    return [];
  }

  // Get the base filename without extension
  const baseName = path.basename(mdxFile, path.extname(mdxFile));

  // Find the path relative to the content directory
  const contentDirPath = path.join(process.cwd(), "content"); // Assuming content is at the root
  let relativePath = path.relative(contentDirPath, path.dirname(mdxFile));

  // Handle case where the file isn't in the content directory
  if (relativePath.startsWith("..")) {
    console.warn(
      `Warning: File ${mdxFile} is not within the content directory`,
    );
    // Fallback to just using the immediate parent directory
    relativePath = path.basename(path.dirname(mdxFile));
  }

  // Create the output directory with the full relative path structure preserved
  const outputDir = path.join(
    process.cwd(),
    ".extracted-snippets",
    relativePath,
    baseName,
  );

  // Ensure the output directory exists
  await fs.mkdir(outputDir, { recursive: true });

  // Generate a separate Python file for each snippet
  const generatedFiles: string[] = [];
  for (let index = 0; index < snippets.length; index++) {
    const file = await generatePythonFile(
      snippets[index],
      outputDir,
      index,
      baseName,
      mdxFile,
    );
    generatedFiles.push(file);
  }

  return generatedFiles;
}
