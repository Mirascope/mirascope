/**
 * MDX Type Definitions
 *
 * Core types for MDX processing pipeline
 */

/**
 * Table of contents item extracted from MDX headings
 * NOTE: Defined here (not in content/types.ts) to avoid circular imports
 * that would break vite.config.ts loading
 */
export type TOCItem = {
  id: string;
  content: string;
  level: number;
  children?: TOCItem[];
};

/**
 * Frontmatter extracted from MDX files
 */
export interface Frontmatter {
  title?: string;
  description?: string;
  date?: string;
  author?: string;
}

/**
 * Preprocessed MDX data (serializable, from Vite plugin)
 * Contains raw MDX content with frontmatter and TOC extracted
 */
export type PreprocessedMDX = {
  /** Extracted frontmatter metadata */
  frontmatter: Frontmatter;
  /** Table of contents extracted from headings */
  tableOfContents: TOCItem[];
  /** Raw MDX content (without frontmatter) */
  content: string;
};

/**
 * Compiled MDX ready for runtime evaluation
 * Contains the compiled JSX code string that can be evaluated with runSync()
 */
export type CompiledMDX = PreprocessedMDX & {
  /** Compiled JSX code string (for runtime evaluation) */
  code: string;
};

/**
 * MDX file metadata
 */
export interface MDXFileInfo {
  /** Absolute file path */
  path: string;
  /** Relative path from content root */
  relativePath: string;
  /** URL slug/route */
  slug: string;
  /** Last modified timestamp */
  lastModified: number;
}

/**
 * Error types for MDX processing
 */
export class MDXProcessingError extends Error {
  constructor(
    message: string,
    public readonly filePath?: string,
    public readonly cause?: Error,
  ) {
    super(message);
    this.name = "MDXProcessingError";
  }
}

export class MDXFrontmatterError extends Error {
  constructor(
    message: string,
    public readonly filePath?: string,
    public readonly cause?: Error,
  ) {
    super(message);
    this.name = "MDXFrontmatterError";
  }
}
