import {
  blogMetadata,
  docsMetadata,
  policyMetadata,
  devMetadata,
  // @ts-expect-error - virtual module resolved by vite plugin
} from "virtual:content-meta";

import type {
  BlogMeta,
  ContentMeta,
  DevMeta,
  DocMeta,
  PolicyMeta,
} from "@/app/lib/content/types";
import type { PreprocessedMDX } from "@/app/lib/mdx/types";

export function getAllBlogMeta(): BlogMeta[] {
  return blogMetadata as BlogMeta[];
}

export function getAllDocsMeta(): DocMeta[] {
  return docsMetadata as DocMeta[];
}

export function getAllPolicyMeta(): PolicyMeta[] {
  return policyMetadata as PolicyMeta[];
}

export function getAllDevMeta(): DevMeta[] {
  return devMetadata as DevMeta[];
}

export function getAllContentMeta(): ContentMeta[] {
  return [
    ...(blogMetadata as BlogMeta[]),
    ...(docsMetadata as DocMeta[]),
    ...(policyMetadata as PolicyMeta[]),
  ];
}

export type VirtualModuleExport = { default: PreprocessedMDX };

/**
 * Maps a content key to its MDX loader function.
 */
export type ModuleMap = Map<string, () => Promise<VirtualModuleExport>>;

/**
 * Build a module map from import.meta.glob, extracting keys via regex.
 *
 * @param modules - Result of import.meta.glob
 * @param pathRegex - Regex with capture group for the content key
 */
function buildModuleMap(
  modules: Record<string, () => Promise<VirtualModuleExport>>,
  pathRegex: RegExp,
): ModuleMap {
  const map = new Map<string, () => Promise<VirtualModuleExport>>();
  for (const [filePath, moduleLoader] of Object.entries(modules)) {
    const match = filePath.match(pathRegex);
    if (match) {
      map.set(match[1], moduleLoader as () => Promise<VirtualModuleExport>);
    }
  }
  return map;
}

/* ========== MODULE-LEVEL GLOB IMPORTS =========== */
// Evaluated once at module load for memory efficiency.

const BLOG_PATH_REGEX = /^\/?\.{2}\/content\/blog\/(.*)\.mdx$/;
const DOCS_PATH_REGEX = /^\/?\.{2}\/content\/docs\/(.*)\.mdx$/;
const POLICY_PATH_REGEX = /^\/?\.{2}\/content\/policy\/(.*)\.mdx$/;
const DEV_PATH_REGEX = /^\/?\.{2}\/content\/dev\/(.*)\.mdx$/;

const BLOG_MODULES = import.meta.glob<VirtualModuleExport>(
  "@/../content/blog/*.mdx",
  { eager: false },
);

const DOCS_MODULES = import.meta.glob<VirtualModuleExport>(
  "@/../content/docs/**/*.mdx",
  { eager: false },
);

const POLICY_MODULES = import.meta.glob<VirtualModuleExport>(
  "@/../content/policy/**/*.mdx",
  { eager: false },
);

const DEV_MODULES = import.meta.glob<VirtualModuleExport>(
  "@/../content/dev/*.mdx",
  { eager: false },
);

// Pre-build module maps once at module initialization
export const BLOG_MODULE_MAP = buildModuleMap(BLOG_MODULES, BLOG_PATH_REGEX);
export const DOCS_MODULE_MAP = buildModuleMap(DOCS_MODULES, DOCS_PATH_REGEX);
export const POLICY_MODULE_MAP = buildModuleMap(
  POLICY_MODULES,
  POLICY_PATH_REGEX,
);
export const DEV_MODULE_MAP = buildModuleMap(DEV_MODULES, DEV_PATH_REGEX);
