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

import type { Plugin, ViteDevServer } from "vite";
import fs from "node:fs";
import fsp from "node:fs/promises";
import { glob } from "glob";
import path from "node:path";

import {
  CONTENT_TYPES,
  type ContentType,
  type ContentMeta,
  type BlogMeta,
  type DocMeta,
  type PolicyMeta,
  type DevMeta,
} from "../app/lib/content/types";
import { parseFrontmatter } from "../app/lib/content/frontmatter";
import { getDocInfoByPath } from "../content/docs/_meta";

const VIRTUAL_MODULE_ID = "virtual:content-meta";
// The "\0" prefix is a Vite convention that marks this as a virtual module,
// preventing Vite from trying to resolve it as a real file path
const RESOLVED_VIRTUAL_MODULE_ID = "\0" + VIRTUAL_MODULE_ID;

export interface ViteContentOptions {
  contentDir: string;
}

export function viteContent(options: ViteContentOptions): Plugin {
  if (!options.contentDir) {
    throw new Error(
      "[vite-plugin-content] contentDir option is required and must be a non-empty string",
    );
  }

  const contentDir = path.resolve(options.contentDir);
  const processor = new ContentProcessor(contentDir, true);
  let isBuild = false;
  let serverInstance: ViteDevServer | null = null;

  // Debounced processing for HMR - prevents rapid-fire reprocessing
  // when multiple files change in quick succession (e.g., git operations, autosave)
  const debouncedProcessAndInvalidate = debounce(async () => {
    await processor.processAllContent();

    // Invalidate the virtual meta module after processing
    if (serverInstance) {
      const metaModule = serverInstance.moduleGraph.getModuleById(
        RESOLVED_VIRTUAL_MODULE_ID,
      );
      if (metaModule) {
        serverInstance.moduleGraph.invalidateModule(metaModule);
      }
    }
  }, 100);

  return {
    name: "vite-plugin-content",

    // Detect build vs serve mode
    config(_config, { command }) {
      isBuild = command === "build";
    },

    async configureServer(server) {
      serverInstance = server;
      // Scan content directory on startup
      await processor.processAllContent();
    },

    async buildStart() {
      // Scan content directory during build (only in build mode)
      if (!isBuild) {
        return;
      }
      await processor.processAllContent();
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
        return processor.generateExport();
      }
    },

    // Watch for file additions and deletions
    watchChange(id, { event }) {
      if (!processor.isRelevantMdxFile(id)) {
        return;
      }
      if (event === "create" || event === "delete") {
        console.log(`[content] File ${event}: ${id}`);
        void debouncedProcessAndInvalidate();
      }
    },

    // Enable HMR for content meta updates (modifications)
    async handleHotUpdate({ file }) {
      if (!processor.isRelevantMdxFile(file)) {
        return;
      }
      console.log(`[content] Updating meta for ${file}`);
      await debouncedProcessAndInvalidate();
    },
  };
}

/**
 * Path representation for consistent handling across the application
 */
export interface ContentPath {
  // The complete path with content type prefix (e.g., "blog/my-post")
  typePath: string;

  // The path after content type (e.g., "my-post" for "blog/my-post")
  subpath: string;

  // The last segment of the path, typically the filename without extension
  slug: string;
}

type SourceContentType = Exclude<ContentType, "llm-docs">;
const SOURCE_CONTENT_TYPES: SourceContentType[] = CONTENT_TYPES.filter(
  (t) => t !== "llm-docs",
);

/**
 * ContentPreprocessor - A class that handles preprocessing of MDX content files
 * into static JSON files with validated metadata.
 */
export default class ContentProcessor {
  // Content directory
  private readonly contentDir: string;

  // Content tracking with type-specific collections
  private metadata = {
    blog: [] as BlogMeta[],
    docs: [] as DocMeta[],
    policy: [] as PolicyMeta[],
    dev: [] as DevMeta[],
  } satisfies Record<SourceContentType, ContentMeta[]>;

  // Track errors for reporting
  private errors: string[] = [];

  // Validation pattern for filenames/slugs
  private static readonly VALID_SLUG_PATTERN = /^[a-z0-9]+(?:[-_][a-z0-9]+)*$/;
  private verbose: boolean;

  /**
   * Constructor - initializes directory structure
   */
  constructor(contentDir: string, verbose = false) {
    this.contentDir = contentDir;
    this.verbose = verbose;
  }

  /**
   * Check if a file path is a relevant MDX file in the content directory
   */
  isRelevantMdxFile(filePath: string): boolean {
    return filePath.endsWith(".mdx") && filePath.startsWith(this.contentDir);
  }

  /**
   * Process all content types
   */
  async processAllContent(): Promise<void> {
    if (this.verbose) console.log("[content] Processing all content...");

    // Clear existing metadata to prevent accumulation on HMR updates
    this.metadata = {
      blog: [],
      docs: [],
      policy: [],
      dev: [],
    };
    this.errors = [];

    // Process each content type
    for (const contentType of SOURCE_CONTENT_TYPES) {
      await this.processContentType(contentType);
    }

    // Report any errors
    if (this.errors.length > 0) {
      console.error("\n[content] Content preprocessing failed with errors:");
      this.errors.forEach((error) => console.error(`- ${error}`));
      throw new Error("Content preprocessing failed. See errors above.");
    }

    if (this.verbose) console.log("[content] Content preprocessing complete!");
  }

  generateExport(): string {
    return `
    /** @type {import('../app/lib/content/types').BlogMeta[]} */
    export const blogMetadata = ${JSON.stringify(this.metadata.blog)};
    /** @type {import('../app/lib/content/types').DocMeta[]} */
    export const docsMetadata = ${JSON.stringify(this.metadata.docs)};
    /** @type {import('../app/lib/content/types').PolicyMeta[]} */
    export const policyMetadata = ${JSON.stringify(this.metadata.policy)};
    /** @type {import('../app/lib/content/types').DevMeta[]} */
    export const devMetadata = ${JSON.stringify(this.metadata.dev)};
    `.trim();
  }

  /**
   * Process a specific content type
   */
  private async processContentType(
    contentType: SourceContentType,
  ): Promise<void> {
    if (this.verbose)
      console.log(`[content] Processing ${contentType} content...`);

    const srcDir = path.join(this.contentDir, contentType);

    // Skip if source directory doesn't exist
    if (!fs.existsSync(srcDir)) {
      if (this.verbose)
        console.warn(
          `[content] Source directory for ${contentType} not found: ${srcDir}`,
        );
      return;
    }

    try {
      await this.processContentDirectory(srcDir, contentType);

      // Sort blog posts by date if applicable
      if (contentType === "blog") {
        this.sortBlogPosts();
      }
    } catch (error) {
      this.addError(
        `Error processing ${contentType} content: ${error instanceof Error ? error.message : String(error)}`,
      );
    }
  }

  /**
   * Process a content directory using glob to find all MDX files
   */
  private async processContentDirectory(
    srcDir: string,
    contentType: SourceContentType,
    // outputBase: string,
  ): Promise<void> {
    // Use glob to find all MDX files in the source directory
    const mdxFiles = await glob(path.join(srcDir, "**/*.mdx"));

    if (this.verbose) {
      console.log(
        `[content] Found ${mdxFiles.length} MDX files for ${contentType}`,
      );
    }

    // Process each MDX file
    for (const filePath of mdxFiles) {
      try {
        await this.processMdxFile(filePath, srcDir, contentType);
      } catch (error) {
        this.addError(
          `Error processing ${filePath}: ${error instanceof Error ? error.message : String(error)}`,
        );
      }
    }
  }

  /**
   * Create a consistent ContentPath object from file path components
   */
  private createContentPath(
    contentType: SourceContentType,
    relativePath: string,
    filename: string,
  ): ContentPath {
    // Remove .mdx extension from relative path
    const cleanPath = relativePath.replace(/\.mdx$/, "");

    // The type-scoped path (e.g., "blog/my-post")
    const typePath = `${contentType}/${cleanPath}`;

    // The portion after content type
    const subpath = cleanPath;

    // The filename without extension (slug)
    const slug = filename;

    return {
      typePath,
      subpath,
      slug,
    };
  }

  /**
   * Generate a full URL route from content type and path
   * This creates routes that match the actual URLs used in the site
   */
  private generateRouteFromPath(
    contentType: SourceContentType,
    contentPath: ContentPath,
  ): string {
    switch (contentType) {
      case "blog":
        return `/blog/${contentPath.slug}`;

      case "docs": {
        // Use the DocRegistry to get the pre-calculated routePath
        const docInfo = getDocInfoByPath(contentPath.subpath);

        if (docInfo) {
          return docInfo.routePath;
        }

        // If doc not found in registry, this is an error condition
        throw new Error(
          `Doc not found in registry: ${contentPath.subpath}. Make sure it's defined in the _meta.ts file.`,
        );
      }

      case "policy":
        if (contentPath.subpath.startsWith("terms/")) {
          return `/${contentPath.subpath}`;
        }
        return `/${contentPath.subpath}`;

      case "dev":
        return `/dev/${contentPath.slug}`;

      default:
        return `/${contentPath.subpath}`;
    }
  }

  /**
   * Validate that a filename is a valid slug
   */
  private validateSlug(filename: string, filePath: string): void {
    if (!ContentProcessor.VALID_SLUG_PATTERN.test(filename)) {
      throw new Error(
        `Invalid filename "${filename}" in ${filePath}. ` +
          `Filenames must be lowercase, contain only letters, numbers, and hyphens, ` +
          `and cannot have consecutive or leading/trailing hyphens.`,
      );
    }
  }

  /**
   * Add an error to the collection for later reporting
   */
  private addError(message: string): void {
    this.errors.push(message);
    console.error(message);
  }

  /**
   * Process a single MDX file
   */
  private async processMdxFile(
    filePath: string,
    srcDir: string,
    contentType: SourceContentType,
    // outputBase: string,
  ): Promise<void> {
    const rawContent = await fsp.readFile(filePath, "utf8");
    const { frontmatter } = parseFrontmatter(rawContent);

    // Get the relative path from the source directory
    const relativePath = path.relative(srcDir, filePath);

    // Get the file name without extension
    const filename = path.basename(filePath, ".mdx");

    // Validate the filename is a valid slug
    this.validateSlug(filename, filePath);

    // Create a consistent content path object
    const contentPath = this.createContentPath(
      contentType,
      relativePath,
      filename,
    );

    // Create and validate metadata in one step
    const metadata = this.createAndValidateMetadata(
      contentType,
      frontmatter,
      contentPath,
      filePath,
    );

    // Add to the appropriate metadata collection
    this.addToMetadataCollection(contentType, metadata);
  }

  /**
   * Create and validate metadata for a content file
   */
  private createAndValidateMetadata(
    contentType: SourceContentType,
    frontmatter: Record<string, unknown>,
    contentPath: ContentPath,
    filePath: string,
  ): ContentMeta {
    // Start with collecting missing fields
    const missingFields: string[] = [];

    // Check base required fields for all content types
    if (!frontmatter.title) missingFields.push("title");
    if (!frontmatter.description) missingFields.push("description");

    // Generate route based on content type and path
    const route = this.generateRouteFromPath(contentType, contentPath);

    // Type-specific required fields and validation
    let metadata: Partial<ContentMeta> = {
      type: contentType,
      path: contentPath.typePath,
      slug: contentPath.slug,
      route: route,
    };

    switch (contentType) {
      case "blog": {
        // Check required blog fields
        if (!frontmatter.date) missingFields.push("date");
        if (!frontmatter.author) missingFields.push("author");
        if (!frontmatter.readTime) missingFields.push("readTime");

        // Validate date format
        const dateValue = frontmatter.date as string | undefined;
        if (dateValue && !/^\d{4}-\d{2}-\d{2}$/.test(dateValue)) {
          throw new Error(
            `Invalid date format in ${filePath}. Date must be in YYYY-MM-DD format.`,
          );
        }

        // Construct blog metadata
        const blogTitle = frontmatter.title as string;
        const blogDescription = frontmatter.description as string;
        const blogDate = frontmatter.date as string;
        const blogReadTime = frontmatter.readTime as string;
        const blogAuthor = frontmatter.author as string;
        const blogLastUpdated = frontmatter.lastUpdated as string | undefined;
        metadata = {
          ...metadata,
          title: blogTitle,
          description: blogDescription,
          date: blogDate,
          readTime: blogReadTime,
          author: blogAuthor,
          ...(blogLastUpdated && {
            lastUpdated: blogLastUpdated,
          }),
        } as Partial<BlogMeta>;
        break;
      }

      case "docs": {
        // Extract product from path, assuming format: docs/product/...

        // Find matching DocInfo from docRegistry to get section path and search weight
        const docInfo = getDocInfoByPath(contentPath.subpath);

        if (!docInfo) {
          throw new Error(
            `No DocInfo found for path: ${contentPath.subpath}. ` +
              `Ensure this document is defined in the product's _meta.ts file.`,
          );
        }
        // Construct doc metadata with section path and search weight
        const docTitle = frontmatter.title as string;
        const docDescription = frontmatter.description as string;
        metadata = {
          ...metadata,
          title: docTitle,
          description: docDescription,
          searchWeight: docInfo.searchWeight,
        } as Partial<DocMeta>;
        break;
      }

      case "policy": {
        // Check required policy fields
        if (!frontmatter.lastUpdated) missingFields.push("lastUpdated");

        // Construct policy metadata
        const policyTitle = frontmatter.title as string;
        const policyDescription = frontmatter.description as string;
        const policyLastUpdated = frontmatter.lastUpdated as string;
        metadata = {
          ...metadata,
          title: policyTitle,
          description: policyDescription,
          lastUpdated: policyLastUpdated,
        } as Partial<PolicyMeta>;
        break;
      }

      default: {
        // For other types, just use base fields
        const defaultTitle = frontmatter.title as string;
        const defaultDescription = frontmatter.description as string;
        metadata = {
          ...metadata,
          title: defaultTitle,
          description: defaultDescription,
        };
      }
    }

    // Throw error if any required fields are missing
    if (missingFields.length > 0) {
      throw new Error(
        `Missing required fields in ${filePath}: ${missingFields.join(", ")}. ` +
          `These fields must be provided in the frontmatter.`,
      );
    }

    return metadata as ContentMeta;
  }

  /**
   * Add metadata to the appropriate collection based on content type
   */
  private addToMetadataCollection(
    contentType: SourceContentType,
    metadata: ContentMeta | BlogMeta | DocMeta | PolicyMeta,
  ): void {
    (this.metadata[contentType] as ContentMeta[]).push(metadata);
  }

  /**
   * Sort blog posts by date (newest first)
   */
  private sortBlogPosts(): void {
    if (this.metadata.blog.length > 0) {
      this.metadata.blog.sort((a, b) => {
        return (
          new Date(b.date || "").getTime() - new Date(a.date || "").getTime()
        );
      });

      if (this.verbose) {
        console.log(
          `[content] Sorted ${this.metadata.blog.length} blog posts by date`,
        );
      }
    }
  }
}

/**
 * Creates a debounced version of an async function.
 * Multiple calls within the delay period will only execute once after the delay.
 * If processing is already running when the timer fires, it will queue another run
 * after the current one completes.
 */
function debounce<T extends (...args: unknown[]) => Promise<void>>(
  fn: T,
  ms: number,
): (...args: Parameters<T>) => Promise<void> {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;
  let isProcessing = false;
  let queuedExecution: { args: Parameters<T>; resolve: () => void } | null =
    null;

  const execute = async (args: Parameters<T>): Promise<void> => {
    if (isProcessing) {
      // Return a promise that will resolve when this queued work actually completes
      return new Promise<void>((resolve) => {
        // If there's already a queued execution, replace args (debounce behavior)
        queuedExecution = { args, resolve };
      });
    }

    isProcessing = true;
    try {
      await fn(...args);
    } finally {
      isProcessing = false;
      timeoutId = null;

      // Process queued execution
      if (queuedExecution) {
        const { args: queuedArgs, resolve } = queuedExecution;
        queuedExecution = null;
        await fn(...queuedArgs);
        resolve();
      }
    }
  };

  return (...args: Parameters<T>): Promise<void> => {
    if (timeoutId) clearTimeout(timeoutId);

    const promise = new Promise<void>((resolve) => {
      timeoutId = setTimeout(() => {
        void execute(args).then(resolve);
      }, ms);
    });

    return promise;
  };
}
