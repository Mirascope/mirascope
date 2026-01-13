// @ts-expect-error - virtual module resolved by vite plugin
import { blogMetadata, docsMetadata } from "virtual:content-meta";
import type { ProcessedMDX } from "@/app/lib/mdx/types";
import type { BlogMeta, DocMeta } from "@/app/lib/content/types";

export function getAllBlogMeta(): BlogMeta[] {
  return blogMetadata as BlogMeta[];
}

export function getAllDocsMeta(): DocMeta[] {
  return docsMetadata as DocMeta[];
}

/**
 * Maps a content key to its MDX loader function.
 */
export type ModuleMap = Map<string, () => Promise<{ mdx: ProcessedMDX }>>;

/**
 * Build a module map from import.meta.glob, extracting keys via regex.
 *
 * @param modules - Result of import.meta.glob
 * @param pathRegex - Regex with capture group for the content key
 */
function buildModuleMap(
  modules: Record<string, () => Promise<{ mdx: ProcessedMDX }>>,
  pathRegex: RegExp,
): ModuleMap {
  const map = new Map<string, () => Promise<{ mdx: ProcessedMDX }>>();
  for (const [filePath, moduleLoader] of Object.entries(modules)) {
    const match = filePath.match(pathRegex);
    if (match) {
      map.set(match[1], moduleLoader as () => Promise<{ mdx: ProcessedMDX }>);
    }
  }
  return map;
}

/* ========== MODULE-LEVEL GLOB IMPORTS =========== */
// Evaluated once at module load for memory efficiency.

const BLOG_PATH_REGEX = /^\/content\/blog\/(.*)\.mdx$/;
const DOCS_PATH_REGEX = /^\/content\/docs\/(.*)\.mdx$/;

const BLOG_MODULES = import.meta.glob<{ mdx: ProcessedMDX }>(
  "@/content/blog/*.mdx",
  { eager: false },
);

const DOCS_MODULES = import.meta.glob<{ mdx: ProcessedMDX }>(
  "@/content/docs/**/*.mdx",
  { eager: false },
);

// Pre-build module maps once at module initialization
export const BLOG_MODULE_MAP = buildModuleMap(BLOG_MODULES, BLOG_PATH_REGEX);
export const DOCS_MODULE_MAP = buildModuleMap(DOCS_MODULES, DOCS_PATH_REGEX);
