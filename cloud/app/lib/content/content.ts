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
 * - Structured error handling via Effect
 * - Type-specific content operations
 */

import { Effect } from "effect";
import { HttpClient, FetchHttpClient } from "@effect/platform";
import { processMDXContent } from "./mdx-processing";
import { docRegistry, type DocInfo } from "./doc-registry";
import { type Product } from "./spec";
import { type TOCItem } from "@/app/components/blocks/table-of-contents";
import {
  ContentError,
  DocumentNotFoundError,
  ContentLoadError,
} from "./errors";

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
    frontmatter: Record<string, unknown>; // Extracted frontmatter
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
 * Currently no additional fields, but kept as a type alias for consistency
 */
export type DevMeta = ContentMeta;

export type DevContent = Content<DevMeta>;

/* ========== HTTP CLIENT =========== */

/**
 * Re-export FetchHttpClient.layer for consumers who need to provide the HttpClient.
 * This is the standard Effect HTTP client implementation using the browser's fetch API.
 */
export const ContentClientLive = FetchHttpClient.layer;

/**
 * Classifies and wraps content errors into appropriate error types.
 * Used with Effect.mapError to transform errors consistently.
 */
function classifyContentError(
  error: unknown,
  path: string,
): ContentError | DocumentNotFoundError | ContentLoadError {
  // Check for 404-like errors
  if (
    error instanceof Error &&
    (error.message.includes("404") ||
      error.message.includes("not found") ||
      error.message.includes("ENOENT"))
  ) {
    return new DocumentNotFoundError({
      message: `document not found: ${path}`,
      path,
    });
  }

  // Wrap other errors in ContentLoadError
  return new ContentLoadError({
    message: `Failed to load content: ${path}${error instanceof Error ? ` - ${error.message}` : ""}`,
    path,
    cause: error,
  });
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
    return `/static/content/${type}/index.json`;
  }

  let resultPath = path;

  // Remove leading slash if present
  if (resultPath.startsWith("/")) {
    resultPath = resultPath.slice(1);
  }

  // Ensure path has the content type prefix
  resultPath = !resultPath.startsWith(`${type}/`)
    ? `${type}/${resultPath}`
    : resultPath;

  // Handle trailing slash as index
  if (resultPath.endsWith("/")) {
    resultPath = `${resultPath}index`;
  }

  // Return the full path to the content file
  return `/static/content/${resultPath}.json`;
}

/**
 * Effect that fetches and parses JSON from a URL.
 *
 * Uses Effect's HttpClient for robust HTTP handling with proper error types.
 *
 * @param path - URL path to fetch JSON from
 * @param errorPath - Optional specific path to use in error messages
 * @returns Effect that yields the parsed JSON data
 */
function fetchJSON<T>(
  path: string,
  errorPath: string = path,
): Effect.Effect<T, ContentError, HttpClient.HttpClient> {
  return Effect.gen(function* () {
    const client = yield* HttpClient.HttpClient;

    // Fetch the JSON file using HttpClient
    const response = yield* client.get(path).pipe(
      Effect.mapError(
        (error) =>
          new ContentError({
            message: `Fetch failed: ${error.message}`,
            path: errorPath,
            cause: error,
          }),
      ),
    );

    if (response.status >= 400) {
      return yield* Effect.fail(
        new ContentError({
          message: `Failed to fetch: ${response.status}`,
          path: errorPath,
        }),
      );
    }

    // Parse the JSON data from response
    return yield* response.json.pipe(
      Effect.map((data) => data as T),
      Effect.mapError(
        (error) =>
          new ContentError({
            message: `Failed to parse JSON: ${error.message}`,
            path: errorPath,
            cause: error,
          }),
      ),
    );
  });
}

/**
 * Effect that loads and processes content for any content type.
 *
 * Implements the unified content loading pipeline:
 * 1. Resolves the content path from the URL path
 * 2. Fetches the preprocessed JSON file
 * 3. Processes the MDX content for rendering
 * 4. Combines metadata and processed content
 *
 * @param path - URL path for the content
 * @param contentType - Type of content being loaded
 * @returns Effect that yields fully processed content ready for rendering
 */
export function loadContent<T extends ContentMeta>(
  path: string,
  contentType: ContentType,
): Effect.Effect<
  Content<T>,
  ContentError | DocumentNotFoundError | ContentLoadError,
  HttpClient.HttpClient
> {
  return Effect.gen(function* () {
    // Get content path
    const contentPath = resolveContentPath(path, contentType);

    // Fetch content JSON data using the shared utility
    const data = yield* fetchJSON<{ meta: T; content: string }>(
      contentPath,
      path,
    ).pipe(Effect.mapError((error) => classifyContentError(error, path)));

    // Raw content from JSON (includes frontmatter)
    const rawContent = data.content;

    // Process MDX for rendering
    const processed = yield* processMDXContent(rawContent, {
      path: path,
    }).pipe(Effect.mapError((error) => classifyContentError(error, path)));

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
  });
}

/* ========== BLOG CONTENT OPERATIONS =========== */

/**
 * Effect that loads blog content by slug.
 *
 * @param slug - The blog post slug or path
 * @returns Effect that yields the fully processed blog content
 */
export function getBlogContent(
  slug: string,
): Effect.Effect<
  BlogContent,
  ContentError | DocumentNotFoundError | ContentLoadError,
  HttpClient.HttpClient
> {
  return loadContent<BlogMeta>(slug, "blog");
}

/**
 * Effect that fetches all blog post metadata.
 *
 * Retrieves the complete list of blog metadata from the index file,
 * which is pre-sorted by date (newest first).
 *
 * @returns Effect that yields array of blog metadata objects
 */
export function getAllBlogMeta(): Effect.Effect<
  BlogMeta[],
  ContentError,
  HttpClient.HttpClient
> {
  return fetchJSON<BlogMeta[]>(
    "/static/content-meta/blog/index.json",
    "blog/index",
  );
}

/* ========== DOC CONTENT OPERATIONS =========== */

/**
 * Effect that loads documentation content by path.
 *
 * @param path - The document path
 * @returns Effect that yields the fully processed document content
 */
export function getDocContent(
  path: string,
): Effect.Effect<
  DocContent,
  ContentError | DocumentNotFoundError | ContentLoadError,
  HttpClient.HttpClient
> {
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
 * Effect that fetches all documentation metadata.
 *
 * @returns Effect that yields array of document metadata objects
 */
export function getAllDocMeta(): Effect.Effect<
  DocMeta[],
  ContentError,
  HttpClient.HttpClient
> {
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
 * Effect that loads policy content by path.
 *
 * @param path - The policy document path
 * @returns Effect that yields the fully processed policy content
 */
export function getPolicy(
  path: string,
): Effect.Effect<
  PolicyContent,
  ContentError | DocumentNotFoundError | ContentLoadError,
  HttpClient.HttpClient
> {
  return loadContent<PolicyMeta>(path, "policy");
}

/**
 * Effect that fetches all policy metadata.
 *
 * @returns Effect that yields array of policy metadata objects
 */
export function getAllPolicyMeta(): Effect.Effect<
  PolicyMeta[],
  ContentError,
  HttpClient.HttpClient
> {
  return Effect.gen(function* () {
    const policies: PolicyMeta[] = [];

    for (const path of KNOWN_POLICY_PATHS) {
      // Try to load each policy, skip on error
      const result = yield* getPolicy(path).pipe(
        Effect.map((policy) => policy.meta),
        Effect.option,
      );

      if (result._tag === "Some") {
        policies.push(result.value);
      }
    }

    return policies;
  });
}

/**
 * Creates a loader function for a policy page
 * This makes it easy to inline policy loaders in route files
 *
 * @param policyPath - The path to the policy to load
 * @returns A function that loads the specified policy (runs Effect internally)
 */
export function createPolicyLoader(policyPath: string) {
  return () =>
    getPolicy(policyPath).pipe(
      Effect.provide(ContentClientLive),
      Effect.runPromise,
    );
}

/* ========== DEV CONTENT OPERATIONS =========== */

/**
 * Effect that loads dev content by slug.
 *
 * @param slug - The dev page slug
 * @returns Effect that yields the fully processed dev content
 */
export function getDevContent(
  slug: string,
): Effect.Effect<
  DevContent,
  ContentError | DocumentNotFoundError | ContentLoadError,
  HttpClient.HttpClient
> {
  return loadContent<DevMeta>(slug, "dev");
}

/**
 * Effect that fetches all dev page metadata.
 *
 * @returns Effect that yields array of dev page metadata objects
 */
export function getAllDevMeta(): Effect.Effect<
  DevMeta[],
  ContentError,
  HttpClient.HttpClient
> {
  return fetchJSON<DevMeta[]>(
    "/static/content-meta/dev/index.json",
    "dev/index",
  );
}
