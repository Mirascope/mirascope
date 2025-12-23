import fs from "fs";
import path from "path";
import { ContentPreprocessor } from "@/app/lib/content/preprocess";
import type { LLMContent } from "@/app/lib/content/llm-content";
import { getAllRoutes, isHiddenRoute } from "@/app/lib/router-utils";
import type { BlogMeta } from "@/app/lib/content/content";
import llmMeta from "@/content/llms/_llms-meta";
import type { ViteDevServer, HmrContext } from "vite";
import { getSettings } from "@/settings";

/**
 * Main processing function that generates static JSON files for all MDX content,
 * processes template files, and creates a sitemap.xml file
 */
async function preprocessContent(verbose = true): Promise<void> {
  try {
    const preprocessor = new ContentPreprocessor(process.cwd(), verbose);
    await preprocessor.processAllContent();

    if (verbose) console.log("Processing LLM documents...");
    await writeLLMDocuments(llmMeta, verbose);

    await generateSitemap(preprocessor.getMetadataByType().blog, llmMeta);
    return;
  } catch (error) {
    console.error("Error during preprocessing:", error);
    throw error; // Let the caller handle the error
  }
}

/**
 * Write LLM documents to disk as JSON and TXT files
 */
async function writeLLMDocuments(
  llmDocs: LLMContent[],
  verbose = true,
): Promise<void> {
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
    fs.mkdirSync(path.dirname(jsonPath), { recursive: true });
    fs.writeFileSync(jsonPath, JSON.stringify(doc.toJSON(), null, 2));

    // Write TXT file for direct LLM consumption at public/{routePath}.txt
    const txtPath = path.join(publicDir, `${routePath}.txt`);
    fs.mkdirSync(path.dirname(txtPath), { recursive: true });
    fs.writeFileSync(txtPath, doc.getContent());

    if (verbose) {
      console.log(
        `Generated LLM document: ${routePath} (${doc.tokenCount} tokens)`,
      );
    }
  }
}

/**
 * Generate sitemap.xml file based on the processed content
 */
async function generateSitemap(
  blogPosts: BlogMeta[],
  llmDocs: LLMContent[],
): Promise<void> {
  console.log("Generating sitemap.xml...");

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
  fs.writeFileSync(outFile, xml);
}

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

      let hmrDebounceTimer: NodeJS.Timeout | null = null;

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
      server.httpServer?.once("listening", async () => {
        if (verbose)
          console.log("Initial content preprocessing for development...");
        await preprocessContent(verbose).catch((error) => {
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
      server.watcher.on("change", async (filePath: string) => {
        // Handle MDX/TS source file changes - regenerate JSON but don't trigger HMR
        if (
          (filePath.endsWith(".mdx") || filePath.endsWith(".ts")) &&
          filePath.includes("/content/")
        ) {
          if (verbose) console.log(`Content file changed: ${filePath}`);
          await preprocessContent(false).catch((error) => {
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

      server.watcher.on("add", async (filePath: string) => {
        // Handle new MDX/TS source files - regenerate JSON
        if (
          (filePath.endsWith(".mdx") || filePath.endsWith(".ts")) &&
          filePath.includes("/content/")
        ) {
          if (verbose) console.log(`Content file added: ${filePath}`);
          await preprocessContent(false).catch((error) => {
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

      server.watcher.on("unlink", async (filePath: string) => {
        // Handle deleted MDX/TS source files - regenerate JSON
        if (
          (filePath.endsWith(".mdx") || filePath.endsWith(".ts")) &&
          filePath.includes("/content/")
        ) {
          if (verbose) console.log(`Content file deleted: ${filePath}`);
          await preprocessContent(false).catch((error) => {
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

// Run the preprocessing when this script is executed directly
if (import.meta.main) {
  preprocessContent().catch((error) => {
    console.error("Fatal error during preprocessing:", error);
    process.exit(1);
  });
}
