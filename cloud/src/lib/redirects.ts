/**
 * Redirects configuration for the website
 *
 * This file defines redirects from old paths to new paths
 * and can be imported by the router to handle redirect routes.
 *
 * Note: Static redirects have been moved to public/_redirects for Cloudflare Pages.
 * Only include redirects here that need dynamic processing or aren't covered by Cloudflare.
 */
import { getAllDocInfo } from "@/src/lib/content";
import { isValidProductName } from "@/src/lib/route-types";
import { canonicalizePath } from "./utils";

// Group redirects map - this will be populated dynamically
const groupRedirects: Record<string, string> = {};

// Build the group redirects map from docs metadata
function buildGroupRedirects() {
  const allDocs = getAllDocInfo();

  // Track valid doc paths
  const validDocPaths = new Set<string>();

  // First pass: collect all valid doc paths
  allDocs.forEach((doc) => {
    validDocPaths.add(canonicalizePath(doc.routePath));
  });

  // Second pass: find potential group paths and their first document
  const groupToFirstDoc: Record<string, string> = {};

  // Use docs in their original order (from _meta.ts files)
  // Process each doc to find group paths
  allDocs.forEach((doc) => {
    const pathParts = doc.routePath.split("/");

    // Skip processing if this is a top-level doc
    if (pathParts.length <= 1) return;

    // Build potential group paths
    for (let i = 0; i < pathParts.length; i++) {
      const partialPath = pathParts.slice(0, i).join("/");

      // If this group path doesn't exist as a valid doc itself and
      // we haven't assigned a redirect target yet, use this doc
      if (!validDocPaths.has(partialPath) && !groupToFirstDoc[partialPath]) {
        groupToFirstDoc[partialPath] = canonicalizePath(doc.routePath);
      }
    }
  });

  // Convert to URL paths for our redirects
  Object.entries(groupToFirstDoc).forEach(([groupPath, docPath]) => {
    groupRedirects[groupPath] = canonicalizePath(docPath);
  });
}

// Initialize group redirects when module is loaded
buildGroupRedirects();
// Define pattern redirects - for patterns that need regex-like handling
export const patternRedirects: Array<{
  pattern: RegExp;
  replacement: string;
}> = [];

/**
 * Process a URL path through redirect rules
 * Returns the new path if a redirect is needed, or null if no redirect applies
 */
export function processRedirects(path: string): string | null {
  // 1. Check group redirects for docs paths
  if (groupRedirects[path]) {
    return groupRedirects[path];
  }

  // 2. Check pattern redirects
  for (const { pattern, replacement } of patternRedirects) {
    const match = path.match(pattern);
    if (match) {
      return path.replace(pattern, replacement);
    }
  }

  // 3. Special case: redirect /docs/{invalid-product} to /docs/mirascope
  const docsProductMatch = path.match(/^\/docs\/([^\/]+)(?:\/.*)?$/);
  if (docsProductMatch && !isValidProductName(docsProductMatch[1])) {
    return "/docs/mirascope";
  }

  // No redirect found
  return null;
}
