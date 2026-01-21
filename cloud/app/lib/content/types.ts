// NOTE: Must use relative path instead of @/app alias because this file
// is imported by vite.config.ts during Vite's config processing phase, before
// the alias resolution is set up. Using the alias would cause module resolution errors.
import type { CompiledMDX, TOCItem } from "../mdx/types";

// Re-export TOCItem for consumers who expect it from this module
export type { TOCItem };

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
 * The meta and content are loaded from JSON, with MDX compiled on demand
 */
export interface Content<T extends ContentMeta = ContentMeta> {
  meta: T; // Typed, validated metadata
  content: string; // MDX with frontmatter stripped out
  mdx: CompiledMDX; // Compiled MDX ready for runtime evaluation
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
  sectionPath: string; // Hierarchical section path (e.g. "docs>mirascope>learn")
  searchWeight: number; // Computed weight based on hierarchical position
}

export type DocContent = Content<DocMeta>;

/* ========== POLICY CONTENT TYPES =========== */

/**
 * Policy-specific metadata extends the base ContentMeta
 */
export interface PolicyMeta extends ContentMeta {
  title: string;
  description: string;
  lastUpdated: string; // Last update date of the policy
}

export type PolicyContent = Content<PolicyMeta>;

/* ========== DEV CONTENT TYPES =========== */

/**
 * Dev-specific metadata (currently same as base ContentMeta)
 * Add dev-specific fields here if needed in the future
 */
export type DevMeta = ContentMeta;

export type DevContent = Content<DevMeta>;
