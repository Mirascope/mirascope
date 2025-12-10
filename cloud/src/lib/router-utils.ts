// scripts/lib/router-utils.ts
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { getAllDocInfo, type BlogMeta } from "@/src/lib/content";
import llmMeta from "@/content/llms/_llms-meta";
import type { LLMContent } from "@/src/lib/content/llm-content";

import { isHiddenRoute } from "@/src/lib/hidden-routes";
export { isHiddenRoute };

// Base URL for the site
export const SITE_URL = "https://mirascope.com";

// Exclude these static routes as they auto-redirect to other pages
const ROUTES_TO_EXCLUDE = ["/docs/", "/terms/"];

// Re-export for backward compatibility (build scripts import from this file)

// Get the project root directory
export function getProjectRoot(): string {
  // Get the directory name for the current module
  const __dirname = path.dirname(fileURLToPath(import.meta.url));
  // Project root directory (2 levels up from src/lib)
  return path.join(__dirname, "..", "..");
}

// Get path to blog metadata json
export function getPostsListPath(): string {
  return path.join(getProjectRoot(), "public", "static", "content-meta", "blog", "index.json");
}

/**
 * Extract static routes from TanStack Router's generated route tree file
 * This avoids having to duplicate route definitions
 */
export function getStaticRoutes(): string[] {
  // Read the routeTree.gen.ts file to extract routes
  const routeTreePath = path.join(getProjectRoot(), "src", "routeTree.gen.ts");
  const routeTreeContent = fs.readFileSync(routeTreePath, "utf-8");

  // Extract routes from the manifest section
  const manifestMatch = routeTreeContent.match(
    /ROUTE_MANIFEST_START\s*(\{[\s\S]*?\})\s*ROUTE_MANIFEST_END/
  );
  if (manifestMatch && manifestMatch[1]) {
    try {
      const manifest = JSON.parse(manifestMatch[1]);

      if (manifest.routes) {
        // Extract all routes from the manifest
        const routes = Object.keys(manifest.routes);

        // Filter out the root and dynamic routes
        return routes
          .filter(
            (route) =>
              route !== "__root__" &&
              !route.includes("$") &&
              !ROUTES_TO_EXCLUDE.some((exclude) => route == exclude)
          )
          .map((route) => {
            // Normalize trailing slashes to match real URLs
            if (route.endsWith("/") && route !== "/") {
              return route.slice(0, -1);
            }
            return route;
          })
          .sort();
      }
    } catch (error) {
      console.warn("Failed to parse route manifest, falling back to regex extraction");
    }
  }

  // Fallback to the previous regex approach if manifest extraction fails
  const staticRoutes: string[] = [];

  // Match all path entries in the FileRoutesByPath interface
  const pathRegex = /\s+'\/[^']*':\s+{/g;
  let match;

  while ((match = pathRegex.exec(routeTreeContent)) !== null) {
    // Extract and clean up the path
    let route = match[0].trim().split("'")[1];

    // Skip dynamic routes for static generation
    if (route.includes("$")) {
      continue;
    }

    // Normalize trailing slashes to match TanStack behavior
    // TanStack path: '/blog/' but actual URL is '/blog'
    if (route.endsWith("/") && route !== "/") {
      route = route.slice(0, -1);
    }

    staticRoutes.push(route);
  }

  return staticRoutes.sort();
}

/**
 * Get blog post routes by scanning the content/blog directory
 */
export function getBlogRoutes(): string[] {
  try {
    // First try using the posts list if it exists (for production)
    const postsListPath = getPostsListPath();
    if (fs.existsSync(postsListPath)) {
      try {
        const postsList: BlogMeta[] = JSON.parse(fs.readFileSync(postsListPath, "utf8"));
        return postsList.map((post) => `/blog/${post.slug}`).sort();
      } catch (error) {
        // Fall through to the file system method if this fails
        console.warn(`Failed to load posts list, falling back to file system: ${error}`);
      }
    }

    // Fall back to scanning the directory (for development/tests)
    const postsDir = path.join(getProjectRoot(), "content", "blog");
    if (!fs.existsSync(postsDir)) {
      throw new Error(`Blog posts directory not found at: ${postsDir}`);
    }

    // Get all .mdx files in the posts directory
    const postFiles = fs.readdirSync(postsDir).filter((file) => file.endsWith(".mdx"));

    // Convert filenames to routes by stripping the .mdx extension
    return postFiles.map((file) => `/blog/${file.replace(".mdx", "")}`).sort();
  } catch (error) {
    throw new Error(`Failed to get blog routes: ${error}`);
  }
}

/**
 * Get dev page routes by scanning the content/dev directory
 */
export function getDevRoutes(): string[] {
  try {
    const devDir = path.join(getProjectRoot(), "content", "dev");
    if (!fs.existsSync(devDir)) {
      return [];
    }

    // Get all .mdx files in the dev directory
    const devFiles = fs.readdirSync(devDir).filter((file) => file.endsWith(".mdx"));

    // Convert filenames to routes by stripping the .mdx extension
    return devFiles.map((file) => `/dev/${file.replace(".mdx", "")}`).sort();
  } catch (error) {
    throw new Error(`Failed to get dev routes: ${error}`);
  }
}

/**
 * Get doc routes
 */
export function getDocsRoutes(): string[] {
  const allDocs = getAllDocInfo();
  return allDocs
    .map((doc) => {
      return doc.routePath;
    })
    .sort();
}

/**
 * Get LLM document routes
 */
export function getLLMDocRoutes(): string[] {
  function getRoute(doc: LLMContent): string {
    if (!doc.route) {
      throw new Error(`LLM document ${doc.slug} does not have a route defined`);
    }
    return doc.route;
  }
  return llmMeta.map(getRoute).sort();
}

/**
 * Get all routes (static + blogs + docs + llm docs + dev)
 */
export function getAllRoutes(includeHidden = false): string[] {
  const staticRoutes = getStaticRoutes();
  const blogRoutes = getBlogRoutes();
  const docRoutes = getDocsRoutes();
  const llmDocRoutes = getLLMDocRoutes();
  const devRoutes = getDevRoutes();

  // Combine all routes and remove duplicates
  const allRoutes = [...staticRoutes, ...blogRoutes, ...docRoutes, ...llmDocRoutes, ...devRoutes];
  return [...new Set(allRoutes)].filter((route) => includeHidden || !isHiddenRoute(route)).sort();
}
