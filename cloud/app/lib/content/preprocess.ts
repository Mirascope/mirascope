import path from "path";
import { Effect, Array as A, Ref, Console } from "effect";
import { FileSystem } from "@effect/platform";
import {
  CONTENT_TYPES,
  type ContentType,
  type ContentMeta,
  type BlogMeta,
  type DocMeta,
  type PolicyMeta,
  docRegistry,
} from "./content";
import { type Product } from "./spec";
import { preprocessMdx } from "./mdx-preprocessing";
import { ContentError, MetadataValidationError } from "./errors";

// =============================================================================
// Types
// =============================================================================

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

/**
 * Result of content preprocessing containing all collected metadata
 */
export interface PreprocessResult {
  blog: BlogMeta[];
  docs: DocMeta[];
  policy: PolicyMeta[];
  dev: ContentMeta[];
}

/**
 * Configuration for content preprocessing
 */
export interface PreprocessConfig {
  baseDir: string;
  verbose: boolean;
}

// =============================================================================
// Pure Functions
// =============================================================================

/**
 * Validation pattern for filenames/slugs
 */
const VALID_SLUG_PATTERN = /^[a-z0-9]+(?:[-_][a-z0-9]+)*$/;

/**
 * Create a consistent ContentPath object from file path components.
 * This is a pure function.
 */
function createContentPath(
  contentType: ContentType,
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
 * Generate a full URL route from content type and path.
 * Returns an Effect that fails with ContentError if doc not found in registry.
 */
function generateRouteFromPath(
  contentType: ContentType,
  contentPath: ContentPath,
  filePath: string,
): Effect.Effect<string, ContentError> {
  switch (contentType) {
    case "blog":
      return Effect.succeed(`/blog/${contentPath.slug}`);

    case "docs": {
      // Use the DocRegistry to get the pre-calculated routePath
      const docInfo = docRegistry.getDocInfoByPath(contentPath.subpath);

      if (docInfo) {
        return Effect.succeed(docInfo.routePath);
      }

      // If doc not found in registry, this is an error condition
      return Effect.fail(
        new ContentError({
          message: `Doc not found in registry: ${contentPath.subpath}. Make sure it's defined in the _meta.ts file.`,
          path: filePath,
        }),
      );
    }

    case "policy":
      return Effect.succeed(`/${contentPath.subpath}`);

    case "dev":
      return Effect.succeed(`/dev/${contentPath.slug}`);

    default:
      return Effect.succeed(`/${contentPath.subpath}`);
  }
}

/**
 * Validate that a filename is a valid slug.
 * Returns an Effect that fails with ContentError if the slug is invalid.
 */
function validateSlug(
  filename: string,
  filePath: string,
): Effect.Effect<void, ContentError> {
  if (!VALID_SLUG_PATTERN.test(filename)) {
    return Effect.fail(
      new ContentError({
        message:
          `Invalid filename "${filename}" in ${filePath}. ` +
          `Filenames must be lowercase, contain only letters, numbers, and hyphens, ` +
          `and cannot have consecutive or leading/trailing hyphens.`,
        path: filePath,
      }),
    );
  }
  return Effect.void;
}

/**
 * Sort blog posts by date (newest first).
 * This is a pure function.
 */
function sortBlogPosts(posts: BlogMeta[]): BlogMeta[] {
  return [...posts].sort((a, b) => {
    return new Date(b.date || "").getTime() - new Date(a.date || "").getTime();
  });
}

/**
 * Create and validate metadata for a content file.
 * Returns an Effect that yields the metadata or fails with validation errors.
 */
function createAndValidateMetadata(
  contentType: ContentType,
  frontmatter: Record<string, unknown>,
  contentPath: ContentPath,
  filePath: string,
): Effect.Effect<ContentMeta, MetadataValidationError | ContentError> {
  return Effect.gen(function* () {
    // Start with collecting missing fields
    const missingFields: string[] = [];

    // Check base required fields for all content types
    if (!frontmatter.title) missingFields.push("title");
    if (!frontmatter.description) missingFields.push("description");

    // Generate route based on content type and path
    const route = yield* generateRouteFromPath(
      contentType,
      contentPath,
      filePath,
    );

    // Type-specific required fields and validation
    let metadata: Partial<ContentMeta> = {
      type: contentType,
      path: contentPath.typePath,
      slug: contentPath.slug,
      route: route,
    };

    switch (contentType) {
      case "blog":
        // Check required blog fields
        if (!frontmatter.date) missingFields.push("date");
        if (!frontmatter.author) missingFields.push("author");
        if (!frontmatter.readTime) missingFields.push("readTime");

        // Validate date format
        if (
          frontmatter.date &&
          !/^\d{4}-\d{2}-\d{2}$/.test(frontmatter.date as string)
        ) {
          return yield* Effect.fail(
            new ContentError({
              message: `Invalid date format in ${filePath}. Date must be in YYYY-MM-DD format.`,
              path: filePath,
            }),
          );
        }

        // Construct blog metadata
        metadata = {
          ...metadata,
          title: frontmatter.title as string,
          description: frontmatter.description as string,
          date: frontmatter.date as string,
          readTime: frontmatter.readTime as string,
          author: frontmatter.author as string,
        } as Partial<BlogMeta>;
        if (frontmatter.lastUpdated) {
          (metadata as Partial<BlogMeta>).lastUpdated =
            frontmatter.lastUpdated as string;
        }
        break;

      case "docs": {
        // Find matching DocInfo from docRegistry to get section path and search weight
        const docInfo = docRegistry.getDocInfoByPath(contentPath.subpath);

        if (!docInfo) {
          return yield* Effect.fail(
            new ContentError({
              message:
                `No DocInfo found for path: ${contentPath.subpath}. ` +
                `Ensure this document is defined in the product's _meta.ts file.`,
              path: filePath,
            }),
          );
        }
        const product: Product = docInfo.product;

        // Construct doc metadata with section path and search weight
        metadata = {
          ...metadata,
          title: frontmatter.title as string,
          description: frontmatter.description as string,
          product,
          searchWeight: docInfo.searchWeight,
        } as Partial<DocMeta>;
        break;
      }

      case "policy":
        // Check required policy fields
        if (!frontmatter.lastUpdated) missingFields.push("lastUpdated");

        // Construct policy metadata
        metadata = {
          ...metadata,
          title: frontmatter.title as string,
          description: frontmatter.description as string,
          lastUpdated: frontmatter.lastUpdated as string,
        } as Partial<PolicyMeta>;
        break;

      default:
        // For other types, just use base fields
        metadata = {
          ...metadata,
          title: frontmatter.title as string,
          description: frontmatter.description as string,
        };
    }

    // Return error if any required fields are missing
    if (missingFields.length > 0) {
      return yield* Effect.fail(
        new MetadataValidationError({
          message: `Missing required fields in ${filePath}: ${missingFields.join(", ")}. These fields must be provided in the frontmatter.`,
          path: filePath,
          missingFields,
        }),
      );
    }

    return metadata as ContentMeta;
  });
}

// =============================================================================
// Effect-based File Operations
// =============================================================================

/**
 * Recursively find all MDX files in a directory.
 */
const findMdxFiles = (
  dir: string,
): Effect.Effect<string[], ContentError, FileSystem.FileSystem> =>
  Effect.gen(function* () {
    const fs = yield* FileSystem.FileSystem;

    // Check if directory exists
    const exists = yield* fs.exists(dir).pipe(
      Effect.mapError(
        (error) =>
          new ContentError({
            message: `Failed to check if directory exists ${dir}: ${error.message}`,
            path: dir,
            cause: error,
          }),
      ),
    );
    if (!exists) {
      return [];
    }

    // Read directory contents
    const entries = yield* fs.readDirectory(dir).pipe(
      Effect.mapError(
        (error) =>
          new ContentError({
            message: `Failed to read directory ${dir}: ${error.message}`,
            path: dir,
            cause: error,
          }),
      ),
    );

    // Process each entry
    const results: string[][] = yield* Effect.all(
      entries.map((entry) =>
        Effect.gen(function* () {
          const fullPath = path.join(dir, entry);
          const stat = yield* fs.stat(fullPath).pipe(
            Effect.mapError(
              (error) =>
                new ContentError({
                  message: `Failed to stat ${fullPath}: ${error.message}`,
                  path: fullPath,
                  cause: error,
                }),
            ),
          );

          if (stat.type === "Directory") {
            // Recursively find MDX files in subdirectory
            return yield* findMdxFiles(fullPath);
          } else if (entry.endsWith(".mdx")) {
            return [fullPath];
          }
          return [] as string[];
        }),
      ),
      { concurrency: "unbounded" },
    );

    return A.flatten(results);
  });

/**
 * Ensure a directory exists, creating it if necessary.
 */
const ensureDir = (
  dir: string,
): Effect.Effect<void, ContentError, FileSystem.FileSystem> =>
  Effect.gen(function* () {
    const fs = yield* FileSystem.FileSystem;
    yield* fs.makeDirectory(dir, { recursive: true }).pipe(
      Effect.mapError(
        (error) =>
          new ContentError({
            message: `Failed to create directory ${dir}: ${error.message}`,
            path: dir,
            cause: error,
          }),
      ),
    );
  });

/**
 * Write content to a file.
 */
const writeFile = (
  filePath: string,
  content: string,
): Effect.Effect<void, ContentError, FileSystem.FileSystem> =>
  Effect.gen(function* () {
    const fs = yield* FileSystem.FileSystem;
    yield* fs.writeFileString(filePath, content).pipe(
      Effect.mapError(
        (error) =>
          new ContentError({
            message: `Failed to write file ${filePath}: ${error.message}`,
            path: filePath,
            cause: error,
          }),
      ),
    );
  });

// =============================================================================
// Content Processing Effects
// =============================================================================

/**
 * Initialize the directory structure for content preprocessing.
 */
const initializeDirectories = (
  config: PreprocessConfig,
): Effect.Effect<
  { staticDir: string; contentDir: string; metaDir: string },
  ContentError,
  FileSystem.FileSystem
> =>
  Effect.gen(function* () {
    const staticDir = path.join(config.baseDir, "public", "static");
    const contentDir = path.join(staticDir, "content");
    const metaDir = path.join(staticDir, "content-meta");

    // Create base directories
    yield* ensureDir(staticDir);
    yield* ensureDir(contentDir);
    yield* ensureDir(metaDir);

    // Create content type directories
    for (const contentType of CONTENT_TYPES) {
      yield* ensureDir(path.join(contentDir, contentType));
      yield* ensureDir(path.join(metaDir, contentType));
    }

    return { staticDir, contentDir, metaDir };
  });

/**
 * Process a single MDX file and return its metadata.
 */
const processMdxFile = (
  filePath: string,
  srcDir: string,
  contentType: ContentType,
  outputBase: string,
): Effect.Effect<
  ContentMeta,
  ContentError | MetadataValidationError,
  FileSystem.FileSystem
> =>
  Effect.gen(function* () {
    // Preprocess the MDX file (resolves code examples)
    const { frontmatter, fullContent } = yield* preprocessMdx(filePath);

    // Get the relative path from the source directory
    const relativePath = path.relative(srcDir, filePath);

    // Get the file name without extension
    const filename = path.basename(filePath, ".mdx");

    // Validate the filename is a valid slug
    yield* validateSlug(filename, filePath);

    // Create a consistent content path object
    const contentPath = createContentPath(contentType, relativePath, filename);

    // Create and validate metadata
    const metadata = yield* createAndValidateMetadata(
      contentType,
      frontmatter,
      contentPath,
      filePath,
    );

    // Create content object that will be saved to JSON
    const contentObject = {
      meta: metadata,
      content: fullContent,
    };

    // Ensure output directory exists
    const outputDir = path.dirname(
      path.join(outputBase, `${contentPath.subpath}.json`),
    );
    yield* ensureDir(outputDir);

    // Write the content file
    const outputPath = path.join(outputBase, `${contentPath.subpath}.json`);
    yield* writeFile(outputPath, JSON.stringify(contentObject));

    return metadata;
  });

/**
 * Process all MDX files for a specific content type.
 */
const processContentType = (
  contentType: ContentType,
  config: PreprocessConfig,
  contentDir: string,
  errorsRef: Ref.Ref<string[]>,
): Effect.Effect<ContentMeta[], never, FileSystem.FileSystem> =>
  Effect.gen(function* () {
    if (config.verbose) {
      yield* Console.log(`Processing ${contentType} content...`);
    }

    const srcDir = path.join(config.baseDir, "content", contentType);
    const outputBase = path.join(contentDir, contentType);

    // Find all MDX files
    const mdxFiles = yield* findMdxFiles(srcDir).pipe(
      Effect.catchAll((error) =>
        Effect.gen(function* () {
          yield* Ref.update(errorsRef, (errors) => [
            ...errors,
            `Error finding MDX files in ${srcDir}: ${error.message}`,
          ]);
          return [] as string[];
        }),
      ),
    );

    if (config.verbose && mdxFiles.length > 0) {
      yield* Console.log(
        `Found ${mdxFiles.length} MDX files for ${contentType}`,
      );
    }

    // Process each MDX file, collecting metadata
    const results = yield* Effect.all(
      mdxFiles.map((filePath) =>
        processMdxFile(filePath, srcDir, contentType, outputBase).pipe(
          Effect.map((metadata) => ({ success: true as const, metadata })),
          Effect.catchAll((error) =>
            Effect.gen(function* () {
              yield* Ref.update(errorsRef, (errors) => [
                ...errors,
                `Error processing ${filePath}: ${error.message}`,
              ]);
              return { success: false as const };
            }),
          ),
        ),
      ),
      { concurrency: "unbounded" },
    );

    // Filter successful results
    return results
      .filter((r): r is { success: true; metadata: ContentMeta } => r.success)
      .map((r) => r.metadata);
  });

/**
 * Write metadata index files for each content type.
 */
const writeMetadataFiles = (
  result: PreprocessResult,
  metaDir: string,
  config: PreprocessConfig,
): Effect.Effect<void, ContentError, FileSystem.FileSystem> =>
  Effect.gen(function* () {
    // Write blog metadata
    if (result.blog.length > 0) {
      yield* writeFile(
        path.join(metaDir, "blog", "index.json"),
        JSON.stringify(result.blog),
      );
      if (config.verbose) {
        yield* Console.log(
          `Created metadata index for blog with ${result.blog.length} items`,
        );
      }
    }

    // Write docs metadata
    if (result.docs.length > 0) {
      yield* writeFile(
        path.join(metaDir, "docs", "index.json"),
        JSON.stringify(result.docs),
      );
      if (config.verbose) {
        yield* Console.log(
          `Created metadata index for docs with ${result.docs.length} items`,
        );
      }
    }

    // Write policy metadata
    if (result.policy.length > 0) {
      yield* writeFile(
        path.join(metaDir, "policy", "index.json"),
        JSON.stringify(result.policy),
      );
      if (config.verbose) {
        yield* Console.log(
          `Created metadata index for policy with ${result.policy.length} items`,
        );
      }
    }

    // Write dev metadata
    if (result.dev.length > 0) {
      yield* writeFile(
        path.join(metaDir, "dev", "index.json"),
        JSON.stringify(result.dev),
      );
      if (config.verbose) {
        yield* Console.log(
          `Created metadata index for dev with ${result.dev.length} items`,
        );
      }
    }

    // Write unified metadata
    const allMetadata = [
      ...result.blog,
      ...result.docs,
      ...result.policy,
      ...result.dev,
    ];

    if (allMetadata.length > 0) {
      yield* writeFile(
        path.join(metaDir, "unified.json"),
        JSON.stringify(allMetadata),
      );
      if (config.verbose) {
        yield* Console.log(
          `Created unified metadata file with ${allMetadata.length} items`,
        );
      }
    }
  });

// =============================================================================
// Main Entry Point
// =============================================================================

/**
 * Process all content types and generate static JSON files.
 * This is the main Effect-based entry point for content preprocessing.
 *
 * @param config - Configuration for preprocessing
 * @returns Effect that yields the preprocessing result
 */
export const processAllContent = (
  config: PreprocessConfig,
): Effect.Effect<PreprocessResult, ContentError, FileSystem.FileSystem> =>
  Effect.gen(function* () {
    if (config.verbose) {
      yield* Console.log("Processing all content...");
    }

    // Initialize directory structure
    const { contentDir, metaDir } = yield* initializeDirectories(config);

    // Create a ref to track errors
    const errorsRef = yield* Ref.make<string[]>([]);

    // Process each content type
    const blogMetadata = yield* processContentType(
      "blog",
      config,
      contentDir,
      errorsRef,
    );
    const docsMetadata = yield* processContentType(
      "docs",
      config,
      contentDir,
      errorsRef,
    );
    const policyMetadata = yield* processContentType(
      "policy",
      config,
      contentDir,
      errorsRef,
    );
    const devMetadata = yield* processContentType(
      "dev",
      config,
      contentDir,
      errorsRef,
    );

    // Sort blog posts by date
    const sortedBlogMetadata = sortBlogPosts(blogMetadata as BlogMeta[]);

    if (config.verbose && sortedBlogMetadata.length > 0) {
      yield* Console.log(
        `Sorted ${sortedBlogMetadata.length} blog posts by date`,
      );
    }

    // Collect result
    const result: PreprocessResult = {
      blog: sortedBlogMetadata,
      docs: docsMetadata as DocMeta[],
      policy: policyMetadata as PolicyMeta[],
      dev: devMetadata,
    };

    // Write metadata files
    yield* writeMetadataFiles(result, metaDir, config);

    // Check for errors
    const errors = yield* Ref.get(errorsRef);
    if (errors.length > 0) {
      yield* Console.error("\n🚨 Content preprocessing failed with errors:");
      for (const error of errors) {
        yield* Console.error(`- ${error}`);
      }
      return yield* Effect.fail(
        new ContentError({
          message: "Content preprocessing failed. See errors above.",
        }),
      );
    }

    if (config.verbose) {
      yield* Console.log("Content preprocessing complete!");
    }

    return result;
  });

/**
 * Legacy function for backwards compatibility.
 * Creates a ContentPreprocessor-like interface using the new Effect-based implementation.
 *
 * @deprecated Use processAllContent instead for new code
 */
export function getMetadataByType(result: PreprocessResult): {
  blog: BlogMeta[];
  docs: DocMeta[];
  policy: PolicyMeta[];
  dev: ContentMeta[];
} {
  return result;
}
