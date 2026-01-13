import type { ReactNode } from "react";
import type { ProcessedMDX } from "@/app/lib/mdx/types";

/**
 * Table of contents item extracted from MDX headings
 */
export type TOCItem = {
  id: string;
  content: string | ReactNode;
  level: number;
  children?: TOCItem[];
};

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
  mdx: ProcessedMDX; // Pre-compiled MDX component with metadata
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
