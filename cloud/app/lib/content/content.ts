/**
 * Unified Content Service
 *
 * This module provides a centralized service for loading and managing various
 * content types (blogs, docs, policies) with a consistent interface.
 *
 * The service handles:
 * - Content type definitions and metadata interfaces
 * - Content loading from static JSON files
 * - MDX processing and rendering
 * - Structured error handling
 * - Type-specific content operations
 */

import { environment } from "./environment";
import { processMDXContent } from "./mdx-processing";
import { docRegistry, type DocInfo } from "./doc-registry";
import { type Product } from "./spec";
import { type TOCItem } from "@/app/components/blocks/table-of-contents";

// Re-export docRegistry for convenience
export { docRegistry };

/* ========== CONTENT TYPES =========== */

/**
 * All recognized content types in the system
 * Each type is mapped to:
 * - Source directory: content/{type}
 * - Output directory: static/content/{type}
 * - Metadata file: static/content-meta/{type}/index.json
 */
export type ContentType = "docs" | "blog" | "policy" | "dev" | "llm-docs";
export const CONTENT_TYPES: ContentType[] = ["docs", "blog", "policy", "dev"];

/**
 * Base metadata interface that all content types extend
 * This metadata is generated during preprocessing and stored with the content
 */
export interface ContentMeta {
  title: string;
  description: string;
  path: string;
  slug: string;
  type: ContentType;
  route: string; // Full URL route for cross-referencing with search results
}

/**
 * Core content interface that combines metadata with content
 * The meta and content are loaded from JSON, with MDX processed on demand
 */
export interface Content<T extends ContentMeta = ContentMeta> {
  meta: T; // Typed, validated metadata
  content: string; // MDX with frontmatter stripped out

  // MDX structure expected by components (used in MDXRenderer)
  mdx: {
    code: string; // Compiled MDX code
    frontmatter: Record<string, any>; // Extracted frontmatter
    tableOfContents: TOCItem[]; // Table of contents extracted from headings
  };
}

/* ========== BLOG CONTENT TYPES =========== */

/**
 * Blog-specific metadata extends the base ContentMeta
 */
export interface BlogMeta extends ContentMeta {
  date: string; // Publication date in YYYY-MM-DD format
  author: string; // Author name
  readTime: string; // Estimated reading time
  lastUpdated: string; // Last update date
}

export type BlogContent = Content<BlogMeta>;

/* ========== DOC CONTENT TYPES =========== */

/**
 * Documentation-specific metadata extends the base ContentMeta
 */
export interface DocMeta extends ContentMeta {
  product: Product; // Which product this doc belongs to
  sectionPath: string; // Hierarchical section path (e.g. "docs>mirascope>learn")
  searchWeight: number; // Computed weight based on hierarchical position
}

export type DocContent = Content<DocMeta>;

/* ========== POLICY CONTENT TYPES =========== */

/**
 * Policy-specific metadata extends the base ContentMeta
 */
export interface PolicyMeta extends ContentMeta {
  lastUpdated: string; // Last update date of the policy
}

export type PolicyContent = Content<PolicyMeta>;

/* ========== DEV CONTENT TYPES =========== */

/**
 * Dev-specific metadata extends the base ContentMeta
 */
export interface DevMeta extends ContentMeta {
  // Add dev-specific metadata fields here if needed
}

export type DevContent = Content<DevMeta>;

/* ========== ERROR HANDLING =========== */

/**
 * Base content error class for consistent error handling
 */
export class ContentError extends Error {
  constructor(
    message: string,
    public path?: string,
    public cause?: Error,
  ) {
    super(message);
    this.name = "ContentError";
  }
}

/**
 * Specific error for document not found conditions
 */
export class DocumentNotFoundError extends ContentError {
  constructor(path: string) {
    super(`document not found: ${path}`, path);
    this.name = "DocumentNotFoundError";
  }
}

/**
 * Specific error for content loading failures
 */
export class ContentLoadError extends ContentError {
  constructor(path: string, cause?: Error) {
    super(
      `Failed to load content: ${path}${cause ? ` - ${cause.message}` : ""}`,
      path,
      cause,
    );
    this.name = "ContentLoadError";
  }
}

/**
 * Handles content errors consistently, classifying unknown errors
 * and wrapping them in appropriate error types
 *
 * @param error - The error to handle
 * @param contentType - The type of content being processed
 * @param path - The path to the content
 * @throws A well-typed error with consistent format
 */
export function handleContentError(error: unknown, path: string): never {
  // Pass the error to the environment handler, to e.g. let the prerenderer know the build is broken
  environment.onError(
    error instanceof Error ? error : new Error(String(error)),
  );

  // Handle known error types
  if (error instanceof DocumentNotFoundError || error instanceof ContentError) {
    throw error;
  }

  // Check for 404-like errors
  if (
    error instanceof Error &&
    (error.message.includes("404") ||
      error.message.includes("not found") ||
      error.message.includes("ENOENT"))
  ) {
    throw new DocumentNotFoundError(path);
  }

  // Wrap other errors
  throw new ContentLoadError(
    path,
    error instanceof Error ? error : new Error(String(error)),
  );
}

/* ========== CORE CONTENT LOADING =========== */

/**
 * Maps a URL path to a content JSON file path
 * Ensures the path has the correct format with type prefix
 *
 * @param path - The URL path to resolve
 * @param type - The content type
 * @returns Resolved path to JSON content file
 */
function resolveContentPath(path: string, type: ContentType): string {
  if (!path) {
    throw new Error("Path cannot be empty");
  }

  // Remove leading slash if present
  if (path.startsWith("/")) {
    path = path.slice(1);
  }

  // Ensure path has the content type prefix
  path = !path.startsWith(`${type}/`) ? `${type}/${path}` : path;

  // Handle trailing slash as index
  if (path.endsWith("/")) {
    path = `${path}index`;
  }

  // Return the full path to the content file
  return `/static/content/${path}.json`;
}

/**
 * Generic JSON fetching utility that handles common error cases
 *
 * @param path - URL path to fetch JSON from
 * @param contentType - The content type being fetched (for error handling)
 * @param errorPath - Optional specific path to use in error messages
 * @returns The parsed JSON data
 * @throws ContentError on fetch or parsing failures
 */
async function fetchJSON<T>(
  path: string,
  errorPath: string = path,
): Promise<T> {
  try {
    // Fetch the JSON file
    const response = await environment.fetch(path);

    if (!response.ok) {
      throw new Error(
        `Failed to fetch: ${response.status} ${response.statusText}`,
      );
    }

    // Parse the JSON data
    return await response.json();
  } catch (error) {
    console.error(`Error fetching JSON from ${path}:`, error);
    environment.onError(
      error instanceof Error ? error : new Error(String(error)),
    );
    throw new ContentError(
      `Failed to fetch data: ${error instanceof Error ? error.message : String(error)}`,
      errorPath,
    );
  }
}

/**
 * Core content loading function used by all content types
 *
 * This function implements the unified content loading pipeline:
 * 1. Resolves the content path from the URL path
 * 2. Fetches the preprocessed JSON file
 * 3. Processes the MDX content for rendering
 * 4. Combines metadata and processed content
 *
 * @param path - URL path for the content
 * @param contentType - Type of content being loaded
 * @returns Fully processed content ready for rendering
 * @throws ContentError or derived errors on failures
 */
export async function loadContent<T extends ContentMeta>(
  path: string,
  contentType: ContentType,
): Promise<Content<T>> {
  try {
    // Get content path
    const contentPath = resolveContentPath(path, contentType);

    // Fetch content JSON data using the shared utility
    const data = await fetchJSON<{ meta: T; content: string }>(
      contentPath,
      path,
    );

    // Raw content from JSON (includes frontmatter)
    const rawContent = data.content;

    // Process MDX for rendering
    const processed = await processMDXContent(rawContent, {
      path: path,
    });

    // Use the metadata from preprocessing - no need to recreate it
    const meta = data.meta;

    // Return complete content
    return {
      meta,
      content: processed.content,
      mdx: {
        code: processed.code,
        frontmatter: processed.frontmatter,
        tableOfContents: processed.tableOfContents,
      },
    };
  } catch (error) {
    return handleContentError(error, path);
  }
}

/* ========== BLOG CONTENT OPERATIONS =========== */

/**
 * Get blog content by slug
 *
 * @param slug - The blog post slug or path
 * @returns The fully processed blog content
 */
export async function getBlogContent(slug: string): Promise<BlogContent> {
  return loadContent<BlogMeta>(slug, "blog");
}

/**
 * Get all blog post metadata
 *
 * Retrieves the complete list of blog metadata from the index file,
 * which is pre-sorted by date (newest first)
 *
 * @returns Array of blog metadata objects
 */
export async function getAllBlogMeta(): Promise<BlogMeta[]> {
  // Use the shared fetchJSON utility to get blog metadata
  return fetchJSON<BlogMeta[]>(
    "/static/content-meta/blog/index.json",
    "blog/index",
  );
}

/* ========== DOC CONTENT OPERATIONS =========== */

/**
 * Get documentation content by path
 *
 * @param path - The document path
 * @returns The fully processed document content
 */
export async function getDocContent(path: string): Promise<DocContent> {
  return loadContent<DocMeta>(path, "docs");
}

/**
 * Get basic info (not full metadata) for all available docs, based on the spec.
 *
 * @returns Array of DocInfo objects with path info
 */
export function getAllDocInfo(): DocInfo[] {
  return docRegistry.getAllDocs();
}

/**
 * Get all documentation metadata from disk.
 *
 * @returns Array of document metadata objects
 */
export async function getAllDocMeta(): Promise<DocMeta[]> {
  return fetchJSON<DocMeta[]>(
    "/static/content-meta/docs/index.json",
    "docs/index",
  );
}

/* ========== POLICY CONTENT OPERATIONS =========== */

/**
 * List of known policy paths in the system
 */
const KNOWN_POLICY_PATHS = ["privacy", "terms/service", "terms/use"];

/**
 * Get policy content by path
 *
 * @param path - The policy document path
 * @returns The fully processed policy content
 */
export async function getPolicy(path: string): Promise<PolicyContent> {
  return loadContent<PolicyMeta>(path, "policy");
}

/**
 * Get all policy metadata
 *
 * @returns Array of policy metadata objects
 */
export async function getAllPolicyMeta(): Promise<PolicyMeta[]> {
  try {
    // For policies, we have a known set of paths
    const policies: PolicyMeta[] = [];

    for (const path of KNOWN_POLICY_PATHS) {
      try {
        const policy = await getPolicy(path);
        policies.push(policy.meta);
      } catch (error) {
        console.error(`Error loading policy at path ${path}:`, error);
        // Skip this policy and continue with others
      }
    }

    return policies;
  } catch (error) {
    throw new ContentError(
      `Failed to get all policy documents: ${error instanceof Error ? error.message : String(error)}`,
      "policy",
      undefined,
    );
  }
}

/**
 * Creates a loader function for a policy page
 * This makes it easy to inline policy loaders in route files
 *
 * @param policyPath - The path to the policy to load
 * @returns A function that loads the specified policy
 */
export function createPolicyLoader(policyPath: string) {
  return async () => {
    try {
      return await getPolicy(policyPath);
    } catch (error) {
      console.error(`Error loading policy: ${policyPath}`, error);
      throw error;
    }
  };
}

/* ========== DEV CONTENT OPERATIONS =========== */

/**
 * Get dev content by slug
 *
 * @param slug - The dev page slug
 * @returns The fully processed dev content
 */
export async function getDevContent(slug: string): Promise<DevContent> {
  return loadContent<DevMeta>(slug, "dev");
}

/**
 * Get all dev page metadata
 *
 * @returns Array of dev page metadata objects
 */
export async function getAllDevMeta(): Promise<DevMeta[]> {
  return fetchJSON<DevMeta[]>(
    "/static/content-meta/dev/index.json",
    "dev/index",
  );
}
