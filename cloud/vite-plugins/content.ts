/**
 * Vite plugin for content meta management
 *
 * This plugin scans the content directory for MDX files and maintains
 * metadata about all content for listing and querying.
 *
 * Features:
 * - Scans content directory on startup
 * - Builds metadata for all MDX files (title, description, slug, etc.)
 * - Exposes meta via virtual:content-meta module
 * - Supports Hot Module Replacement (HMR) in development
 *
 * Usage:
 * ```typescript
 * import { blogPosts, allContent } from "virtual:content-meta";
 *
 * // blogPosts: BlogMeta[] - blog posts sorted by date (newest first)
 * // allContent: ContentMeta[] - all MDX content entries
 * ```
 */

import type { Plugin } from "vite";
import fs from "node:fs";
import type { Dirent } from "node:fs";
import path from "node:path";
import type {
  ContentType,
  ContentMeta,
  BlogMeta,
} from "../app/lib/content/types";
import { parseFrontmatter } from "../app/lib/content/frontmatter";

const VIRTUAL_MODULE_ID = "virtual:content-meta";
// The "\0" prefix is a Vite convention that marks this as a virtual module,
// preventing Vite from trying to resolve it as a real file path
const RESOLVED_VIRTUAL_MODULE_ID = "\0" + VIRTUAL_MODULE_ID;

/** Content meta keyed by absolute file path */
const contentMeta = new Map<string, ContentMeta | BlogMeta>();

export interface ViteContentOptions {
  contentDir: string;
}

/**
 * Derive content type from file path relative to content directory
 */
function getContentType(contentDir: string, filePath: string): ContentType {
  const relativePath = path.relative(contentDir, filePath);
  const firstDir = relativePath.split(path.sep)[0];

  // Map directory names to content types
  const typeMap: Record<string, ContentType> = {
    blog: "blog",
    docs: "docs",
    policy: "policy",
    dev: "dev",
  };

  return typeMap[firstDir] || "docs";
}

/**
 * Build a meta entry from an MDX file
 */
function buildMetaEntry(
  contentDir: string,
  filePath: string,
  frontmatter: Record<string, string>,
): ContentMeta | BlogMeta {
  const urlPath = path.join(
    path
      .relative(path.join(process.cwd(), "content"), filePath)
      .replace(/\.mdx$/, ""),
  );
  const contentType = getContentType(contentDir, filePath);
  const slug = path.basename(filePath, ".mdx");
  const route = `/${contentType}/${slug}`;

  const baseEntry: ContentMeta = {
    title: frontmatter.title || slug,
    description: frontmatter.description || "",
    path: urlPath,
    slug,
    type: contentType,
    route,
  };

  // Add blog-specific fields if this is a blog post
  if (contentType === "blog") {
    const blogEntry: BlogMeta = {
      ...baseEntry,
      date: frontmatter.date || "",
      author: frontmatter.author || "",
      readTime: frontmatter.readTime || "",
      lastUpdated: frontmatter.lastUpdated || "",
    };
    return blogEntry;
  }

  return baseEntry;
}

/**
 * Update the meta entry for a single MDX file
 * Used for both initial scan and HMR updates
 */
async function updateMetaEntry(
  contentDir: string,
  filePath: string,
): Promise<void> {
  try {
    const rawContent = await fs.promises.readFile(filePath, "utf-8");
    const { frontmatter } = parseFrontmatter(rawContent);
    const metaEntry = buildMetaEntry(contentDir, filePath, frontmatter);
    contentMeta.set(filePath, metaEntry);
  } catch (error) {
    console.error(`[content] Error updating meta for ${filePath}:`, error);
  }
}

/**
 * Recursively scan a directory for MDX files and populate the content meta
 * Processes files in parallel batches with concurrency control
 */
async function scanContentDirectory(
  contentDir: string,
  currentDir: string,
): Promise<void> {
  const concurrency = 20;
  const entries = await fs.promises.readdir(currentDir, {
    withFileTypes: true,
  });

  const processEntry = async (entry: Dirent): Promise<void> => {
    const fullPath = path.join(currentDir, entry.name);

    if (entry.isDirectory()) {
      await scanContentDirectory(contentDir, fullPath);
    } else if (entry.isFile() && entry.name.endsWith(".mdx")) {
      await updateMetaEntry(contentDir, fullPath);
    }
  };

  // Process entries in parallel batches with concurrency limit
  for (let i = 0; i < entries.length; i += concurrency) {
    const batch = entries.slice(i, i + concurrency);
    await Promise.all(batch.map(processEntry));
  }
}

/**
 * Print content statistics based on types in the map
 */
function printContentStats(
  contentMeta: Map<string, ContentMeta | BlogMeta>,
  verb: "Generated" | "Updated",
  additionalInfo?: string,
): void {
  const allEntries = Array.from(contentMeta.values());
  const typeCounts = new Map<ContentType, number>();

  // Count entries by type
  for (const entry of allEntries) {
    const count = typeCounts.get(entry.type) || 0;
    typeCounts.set(entry.type, count + 1);
  }

  // Build stats string
  const statsParts: string[] = [];
  for (const [type, count] of typeCounts.entries()) {
    statsParts.push(`${count} ${type}${count !== 1 ? "s" : ""}`);
  }

  const statsString = statsParts.join(", ");
  const totalString = `${allEntries.length} total entr${allEntries.length !== 1 ? "ies" : "y"}`;
  const infoString = additionalInfo ? ` ${additionalInfo}` : "";

  console.log(
    `[content] ${verb} virtual module: ${statsString}, ${totalString}${infoString}`,
  );
}

/**
 * Generate the virtual module code from the content meta
 */
function generateMetaModule(): string {
  const allEntries = Array.from(contentMeta.values());

  // Filter and sort blog posts by date (newest first)
  const blogPosts = allEntries
    .filter((entry): entry is BlogMeta => entry.type === "blog")
    .sort((a, b) => {
      return new Date(b.date || 0).getTime() - new Date(a.date || 0).getTime();
    });

  return `
/** @type {import('../app/lib/content/types').BlogMeta[]} */
export const blogPosts = ${JSON.stringify(blogPosts, null, 2)};
/** @type {import('../app/lib/content/types').ContentMeta[]} */
export const allContent = ${JSON.stringify(allEntries, null, 2)};
  `.trim();
}

/**
 * Scan content directory and build meta
 */
async function buildContentMeta(contentDir: string): Promise<void> {
  if (fs.existsSync(contentDir)) {
    console.log(`[content] Building content meta from: ${contentDir}`);
    const startTime = Date.now();
    await scanContentDirectory(contentDir, contentDir);
    const duration = Date.now() - startTime;
    printContentStats(contentMeta, "Generated", `in ${duration}ms`);
  } else {
    console.warn(`[content] Content directory not found: ${contentDir}`);
  }
}

export function viteContent(options: ViteContentOptions): Plugin {
  if (!options.contentDir) {
    throw new Error(
      "[vite-plugin-content] contentDir option is required and must be a non-empty string",
    );
  }

  const contentDir = path.resolve(options.contentDir);
  let isBuild = false;

  return {
    name: "vite-plugin-content",

    // Detect build vs serve mode
    config(_config, { command }) {
      isBuild = command === "build";
    },

    async configureServer() {
      // Scan content directory on startup
      await buildContentMeta(contentDir);
    },

    async buildStart() {
      // Scan content directory during build (only in build mode)
      if (!isBuild) {
        return;
      }
      await buildContentMeta(contentDir);
    },

    // Resolve virtual module imports
    resolveId(id) {
      if (id === VIRTUAL_MODULE_ID) {
        return RESOLVED_VIRTUAL_MODULE_ID;
      }
    },

    // Load the virtual module content
    load(id) {
      if (id === RESOLVED_VIRTUAL_MODULE_ID) {
        return generateMetaModule();
      }
    },

    // Enable HMR for content meta updates
    async handleHotUpdate({ file, server }) {
      if (file.endsWith(".mdx") && file.startsWith(contentDir)) {
        console.log(`[content] Updating meta for ${file}`);

        // Update meta entry for the changed file
        await updateMetaEntry(contentDir, file);

        // Invalidate the virtual meta module so it regenerates
        const metaModule = server.moduleGraph.getModuleById(
          RESOLVED_VIRTUAL_MODULE_ID,
        );
        if (metaModule) {
          server.moduleGraph.invalidateModule(metaModule);
        }
      }
    },
  };
}
