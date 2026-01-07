import type { TOCItem } from "@/app/lib/content/types";

/**
 * MDX Type Definitions
 *
 * Core types for MDX processing pipeline
 */

import type React from "react";

/**
 * Frontmatter extracted from MDX files
 */
export interface Frontmatter {
  title?: string;
  description?: string;
  date?: string;
  author?: string;
  [key: string]: unknown;
}

/**
 * Compiled MDX module (imported from .mdx files)
 * This is a React component with metadata attached as properties
 */
export type ProcessedMDX = React.ComponentType<{
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  components?: Record<string, React.ComponentType<any>>;
}> & {
  /** Extracted frontmatter metadata */
  frontmatter: Frontmatter;
  /** Table of contents extracted from headings */
  tableOfContents: TOCItem[];
  /** Raw MDX content (without frontmatter) */
  content: string;
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
