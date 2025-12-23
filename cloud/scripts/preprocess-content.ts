import fs from "fs";
import path from "path";
import { Effect, Console } from "effect";
import { NodeFileSystem } from "@effect/platform-node";
import { FileSystem } from "@effect/platform";
import {
  processAllContent,
  type PreprocessResult,
} from "@/app/lib/content/preprocess";
import type { LLMContent } from "@/app/lib/content/llm-content";
import { getAllRoutes, isHiddenRoute } from "@/app/lib/router-utils";
import type { BlogMeta } from "@/app/lib/content/content";
import llmMeta from "@/content/llms/_llms-meta";
import type { ViteDevServer, HmrContext } from "vite";
import { getSettings } from "@/settings";
import { ContentError } from "@/app/lib/content/errors";

// =============================================================================
// Effect-based Content Preprocessing
// =============================================================================

/**
 * Effect-based preprocessing that uses NodeFileSystem layer.
 * This is the main entry point for content preprocessing.
 */
const runPreprocessContent = (
  verbose = true,
): Effect.Effect<PreprocessResult, ContentError, FileSystem.FileSystem> =>
  Effect.gen(function* () {
    const result = yield* processAllContent({
      baseDir: process.cwd(),
      verbose,
    });

    if (verbose) {
      yield* Console.log("Processing LLM documents...");
    }

    // Write LLM documents
    yield* writeLLMDocuments(llmMeta, verbose);

    // Generate sitemap
    yield* generateSitemap(result.blog, llmMeta);

    return result;
  });

/**
 * Run the Effect-based preprocessing with NodeFileSystem layer.
 */
async function preprocessContent(verbose = true): Promise<PreprocessResult> {
  return Effect.runPromise(
    runPreprocessContent(verbose).pipe(Effect.provide(NodeFileSystem.layer)),
  );
}

// =============================================================================
// LLM Document Processing (Effect-based async)
// =============================================================================

/**
 * Write LLM documents to disk as JSON and TXT files
 */
const writeLLMDocuments = (
  llmDocs: LLMContent[],
  verbose = true,
): Effect.Effect<void, ContentError, FileSystem.FileSystem> =>
  Effect.gen(function* () {
    const fs = yield* FileSystem.FileSystem;
    const publicDir = path.join(process.cwd(), "public");

    for (const doc of llmDocs) {
      const routePath = doc.route!;

      // Write JSON file for viewer consumption at public/static/content/{routePath}.json
      const jsonPath = path.join(
        publicDir,
        "static",
        "content",
        `${routePath}.json`,
      );
      yield* fs.makeDirectory(path.dirname(jsonPath), { recursive: true });
      yield* fs.writeFileString(
        jsonPath,
        JSON.stringify(doc.toJSON(), null, 2),
      );

      // Write TXT file for direct LLM consumption at public/{routePath}.txt
      const txtPath = path.join(publicDir, `${routePath}.txt`);
      yield* fs.makeDirectory(path.dirname(txtPath), { recursive: true });
      yield* fs.writeFileString(txtPath, doc.getContent());

      if (verbose) {
        yield* Console.log(
          `Generated LLM document: ${routePath} (${doc.tokenCount} tokens)`,
        );
      }
    }
  }).pipe(
    Effect.mapError(
      (e) =>
        new ContentError({
          message: `Failed to write LLM documents: ${String(e)}`,
        }),
    ),
  );

// =============================================================================
// Sitemap Generation (Effect-based async)
// =============================================================================

/**
 * Generate sitemap.xml file based on the processed content
 */
const generateSitemap = (
  blogPosts: BlogMeta[],
  llmDocs: LLMContent[],
): Effect.Effect<void, ContentError, FileSystem.FileSystem> =>
  Effect.gen(function* () {
    yield* Console.log("Generating sitemap.xml...");

    const fsService = yield* FileSystem.FileSystem;
    const settings = getSettings();
    const siteUrl = settings.SITE_URL || "http://localhost:3000";

    // Get all routes using our centralized utility
    const uniqueRoutes = getAllRoutes().filter((route) => route !== "/404");

    // Use the blog posts metadata
    const postsList = blogPosts || [];

    // Current date for default lastmod
    const today = new Date().toISOString().split("T")[0];

    // Get the date of the latest blog post for the /blog route
    const latestBlogDate =
      postsList.length > 0
        ? postsList[0].lastUpdated || postsList[0].date
        : today;

    // Generate sitemap XML
    let xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n';

    // Add LLM document URLs to the sitemap
    llmDocs.forEach((llmDoc) => {
      if (!llmDoc.route || isHiddenRoute(llmDoc.route)) {
        return;
      }
      // Add the .txt file
      xml += "  <url>\n";
      xml += `    <loc>${siteUrl}${llmDoc.route}.txt</loc>\n`;
      xml += `    <lastmod>${today}</lastmod>\n`;
      xml += "    <changefreq>daily</changefreq>\n";
      xml += "  </url>\n";
    });

    // Add each URL
    uniqueRoutes.forEach((route) => {
      xml += "  <url>\n";
      xml += `    <loc>${siteUrl}${route}</loc>\n`;

      // Set lastmod based on whether it's a blog post, blog index, or other page
      if (route === "/blog") {
        xml += `    <lastmod>${latestBlogDate}</lastmod>\n`;
        xml += "    <changefreq>daily</changefreq>\n";
      } else if (route.startsWith("/blog/")) {
        // Find the post to get its lastUpdated date
        const postSlug = route.replace("/blog/", "");
        const post = postsList.find((p) => p.slug === postSlug);
        if (post) {
          xml += `    <lastmod>${post.lastUpdated || post.date}</lastmod>\n`;
        } else {
          xml += `    <lastmod>${today}</lastmod>\n`;
        }
        xml += "    <changefreq>weekly</changefreq>\n";
      } else {
        xml += `    <lastmod>${today}</lastmod>\n`;
        xml += "    <changefreq>daily</changefreq>\n";
      }

      xml += "  </url>\n";
    });

    xml += "</urlset>";

    // Write to file
    const outFile = path.join(process.cwd(), "public", "sitemap.xml");
    yield* fsService.writeFileString(outFile, xml);
  }).pipe(
    Effect.mapError(
      (e) =>
        new ContentError({
          message: `Failed to generate sitemap: ${String(e)}`,
        }),
    ),
  );

// =============================================================================
// Vite Plugin
// =============================================================================

// Type alias for Node.js setTimeout function because eslint doesn't know NodeJS
type NodeJsTimeout = ReturnType<typeof setTimeout>;

export function contentPreprocessPlugin(options = { verbose: true }) {
  // Get all content directories (docs includes LLM document templates)
  const contentDirs = ["blog", "docs", "policy", "dev"].map((type) =>
    path.join(process.cwd(), "content", type),
  );

  return {
    name: "content-preprocess-plugin",
    // Only apply during development
    apply: "serve" as const,

    // Handle module resolution to prevent MDX files from being processed by Vite's HMR
    handleHotUpdate({ file }: HmrContext) {
      // If this is an MDX file in content, prevent default HMR
      if (file.endsWith(".mdx") && file.includes("/content/")) {
        // Return empty array to prevent Vite from doing HMR for this file
        // Our watcher will handle it by regenerating JSON and triggering HMR on that
        return [];
      }
      // For other files, let Vite handle them normally
      return undefined;
    },

    configureServer(server: ViteDevServer) {
      const { verbose } = options;

      let hmrDebounceTimer: NodeJsTimeout | null = null;

      const debouncedHMR = () => {
        if (hmrDebounceTimer) {
          clearTimeout(hmrDebounceTimer);
        }

        // Wait 16ms (one frame at 60fps) to batch rapid file system events
        hmrDebounceTimer = setTimeout(() => {
          if (verbose) console.log(`Generated content changed, triggering HMR`);
          server.ws.send({
            type: "full-reload",
            path: "*",
          });
          hmrDebounceTimer = null;
        }, 16);
      };

      // Run preprocessing when the server starts
      server.httpServer?.once("listening", () => {
        if (verbose)
          console.log("Initial content preprocessing for development...");
        void preprocessContent(verbose).catch((error: unknown) => {
          console.error("Error preprocessing content:", error);
        });
      });

      // Create the base content directory if it doesn't exist
      const baseContentDir = path.join(process.cwd(), "content");
      if (!fs.existsSync(baseContentDir)) {
        fs.mkdirSync(baseContentDir, { recursive: true });
      }

      // Always watch the base content directory
      server.watcher.add(baseContentDir);

      // Set up watching on content directories
      contentDirs.forEach((dir) => {
        // Create the directory if it doesn't exist
        if (!fs.existsSync(dir)) {
          fs.mkdirSync(dir, { recursive: true });
        }

        if (verbose) console.log(`Watching directory for changes: ${dir}`);
        server.watcher.add(dir);
      });

      // Also watch the output directory (public/static/content) even though it's in .gitignore
      const publicContentDir = path.join(
        process.cwd(),
        "public",
        "static",
        "content",
      );
      if (fs.existsSync(publicContentDir)) {
        server.watcher.add(publicContentDir);
        if (verbose)
          console.log(
            `Watching output directory for changes: ${publicContentDir}`,
          );
      }

      // React to content changes - these will work for any content directory
      server.watcher.on("change", (filePath: string) => {
        // Handle MDX/TS source file changes - regenerate JSON but don't trigger HMR
        if (
          (filePath.endsWith(".mdx") || filePath.endsWith(".ts")) &&
          filePath.includes("/content/")
        ) {
          if (verbose) console.log(`Content file changed: ${filePath}`);
          void preprocessContent(false).catch((error: unknown) => {
            console.error(
              "Error preprocessing content after file change:",
              error,
            );
          });
        }
        // Handle JSON changes - debounce and trigger HMR once after all files are done
        else if (
          filePath.endsWith(".json") &&
          filePath.includes("public/static/content")
        ) {
          debouncedHMR();
        }
      });

      server.watcher.on("add", (filePath: string) => {
        // Handle new MDX/TS source files - regenerate JSON
        if (
          (filePath.endsWith(".mdx") || filePath.endsWith(".ts")) &&
          filePath.includes("/content/")
        ) {
          if (verbose) console.log(`Content file added: ${filePath}`);
          void preprocessContent(false).catch((error: unknown) => {
            console.error("Error preprocessing content after file add:", error);
          });
        }
        // Handle new JSON files - debounce and trigger HMR
        else if (
          filePath.endsWith(".json") &&
          filePath.includes("public/static/content")
        ) {
          debouncedHMR();
        }
      });

      server.watcher.on("unlink", (filePath: string) => {
        // Handle deleted MDX/TS source files - regenerate JSON
        if (
          (filePath.endsWith(".mdx") || filePath.endsWith(".ts")) &&
          filePath.includes("/content/")
        ) {
          if (verbose) console.log(`Content file deleted: ${filePath}`);
          void preprocessContent(false).catch((error: unknown) => {
            console.error(
              "Error preprocessing content after file delete:",
              error,
            );
          });
        }
        // Handle deleted JSON files - debounce and trigger HMR
        else if (
          filePath.endsWith(".json") &&
          filePath.includes("public/static/content")
        ) {
          debouncedHMR();
        }
      });
    },
  };
}

// =============================================================================
// CLI Entry Point
// =============================================================================

// Run the preprocessing when this script is executed directly
if (import.meta.main) {
  preprocessContent()
    .then(() => {
      console.log("Preprocessing completed successfully.");
    })
    .catch((error) => {
      console.error("Fatal error during preprocessing:", error);
      process.exit(1);
    });
}
