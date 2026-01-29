/**
 * Vite plugin for generating static markdown files
 *
 * Generates static markdown files alongside pre-rendered HTML pages,
 * enabling content negotiation via the `Accept: text/markdown` header.
 *
 * For each content page (docs, blog, policy), this plugin:
 * 1. Loads the MDX source with CodeExample directives expanded
 * 2. Strips frontmatter and extracts the raw markdown content
 * 3. Converts relative links to absolute URLs
 * 4. Writes it as a .md file in the same location as the HTML
 *
 * The Cloudflare Worker (server-entry.ts) handles content negotiation
 * by checking the Accept header and serving the appropriate file.
 *
 * Output structure:
 *   dist/client/docs/learn/llm/calls/index.html  (pre-rendered HTML)
 *   dist/client/docs/learn/llm/calls/index.md    (raw markdown)
 */

import type { Plugin } from "vite";

import fs from "node:fs/promises";
import path from "node:path";

import type ContentProcessor from "../app/lib/content/content-processor";
import type { ContentMeta } from "../app/lib/content/types";

import { preprocessMdx } from "../app/lib/content/mdx-preprocessing";
import { BASE_URL } from "../app/lib/site";

/**
 * Options for the markdown exporter
 */
export interface MarkdownExportOptions {
  /** ContentProcessor instance for accessing content metadata */
  processor: ContentProcessor;
  /** Output directory (typically dist/client) */
  outputDir: string;
  /** Enable verbose logging */
  verbose?: boolean;
}

/**
 * Result of generating markdown files
 */
export interface GenerationResults {
  success: number;
  failed: number;
  errors: Array<{ route: string; error: string }>;
}

/**
 * Generates static markdown files for all content pages.
 *
 * Can be used standalone or within the Vite plugin.
 */
export class MarkdownExporter {
  private readonly processor: ContentProcessor;
  private readonly outputDir: string;
  private readonly verbose: boolean;
  private readonly contentDir: string;

  constructor(options: MarkdownExportOptions) {
    if (!options.processor) {
      throw new Error(
        "[markdown-export] processor option is required and must be a ContentProcessor instance",
      );
    }

    this.processor = options.processor;
    this.outputDir = options.outputDir;
    this.verbose = options.verbose ?? false;
    // Content directory is one level up from cloud/
    this.contentDir = path.resolve(process.cwd(), "../content");
  }

  /**
   * Generate markdown files for all content pages.
   */
  async generate(): Promise<GenerationResults> {
    // Ensure content has been processed
    await this.processor.processAllContent();

    const metadata = this.processor.getMetadata();
    const allContent: ContentMeta[] = [
      ...metadata.docs,
      ...metadata.blog,
      ...metadata.policy,
    ];

    if (allContent.length === 0) {
      console.log("[markdown-export] No content found");
      return { success: 0, failed: 0, errors: [] };
    }

    console.log(
      `[markdown-export] Generating markdown files for ${allContent.length} pages...`,
    );

    const results: GenerationResults = {
      success: 0,
      failed: 0,
      errors: [],
    };

    // Process all content items
    for (const content of allContent) {
      try {
        await this.generateMarkdownFile(content);
        results.success++;
        if (this.verbose) {
          console.log(`[markdown-export] Generated ${content.route}`);
        }
      } catch (error) {
        results.failed++;
        const errorMessage =
          error instanceof Error ? error.message : String(error);
        results.errors.push({ route: content.route, error: errorMessage });
        console.error(
          `[markdown-export] Failed to generate ${content.route}: ${errorMessage}`,
        );
      }
    }

    console.log(
      `[markdown-export] Complete: ${results.success} generated, ${results.failed} failed`,
    );

    return results;
  }

  /**
   * Generate a single markdown file for a content item.
   */
  private async generateMarkdownFile(content: ContentMeta): Promise<void> {
    // Resolve the source MDX file path
    // content.path is like "docs/learn/llm/calls" or "blog/my-post"
    const mdxFilePath = path.join(this.contentDir, `${content.path}.mdx`);

    // Check if the MDX file exists
    try {
      await fs.access(mdxFilePath);
    } catch {
      throw new Error(`MDX file not found: ${mdxFilePath}`);
    }

    // Preprocess the MDX to expand CodeExamples and strip frontmatter
    const preprocessed = await preprocessMdx(mdxFilePath);

    // Build the output path based on the route
    // content.route is like "/docs/learn/llm/calls" or "/blog/my-post"
    // Output as /docs/learn/llm/calls.md (not /docs/learn/llm/calls/index.md)
    const routePath = content.route.replace(/^\//, ""); // Remove leading slash
    const outputPath = path.join(this.outputDir, `${routePath}.md`);

    // Ensure the output directory exists
    await fs.mkdir(path.dirname(outputPath), { recursive: true });

    // Add frontmatter header with title and description for context
    const markdownContent = this.buildMarkdownContent(
      content,
      preprocessed.content,
    );

    // Write the markdown file
    await fs.writeFile(outputPath, markdownContent, "utf-8");
  }

  /**
   * Build the final markdown content with metadata and absolute URLs.
   */
  private buildMarkdownContent(meta: ContentMeta, content: string): string {
    // Convert relative links to absolute URLs
    const absoluteContent = this.convertLinksToAbsolute(content);

    // Add a YAML frontmatter header with metadata
    const frontmatter = [
      "---",
      `title: "${meta.title}"`,
      `description: "${meta.description}"`,
      `url: "${BASE_URL}${meta.route}"`,
      "---",
      "",
    ].join("\n");

    return frontmatter + absoluteContent;
  }

  /**
   * Convert relative links and images to absolute URLs.
   */
  private convertLinksToAbsolute(content: string): string {
    // Convert markdown links: [text](/path) -> [text](https://mirascope.com/path)
    // Match links that start with / but not // (protocol-relative)
    let result = content.replace(
      /\[([^\]]*)\]\(\/([^)]*)\)/g,
      `[$1](${BASE_URL}/$2)`,
    );

    // Convert markdown images: ![alt](/path) -> ![alt](https://mirascope.com/path)
    result = result.replace(
      /!\[([^\]]*)\]\(\/([^)]*)\)/g,
      `![$1](${BASE_URL}/$2)`,
    );

    return result;
  }
}

/**
 * Options for the Vite plugin
 */
export interface ViteMarkdownExportOptions {
  /** ContentProcessor instance for accessing content metadata */
  processor: ContentProcessor;
  /** Enable verbose logging */
  verbose?: boolean;
}

/**
 * Create the markdown export Vite plugin.
 *
 * This plugin:
 * - In dev mode: serves .md files dynamically via middleware
 * - In build mode: generates .md files alongside HTML after the build
 *
 * @example
 * ```typescript
 * // In vite.config.ts
 * import { viteMarkdownExport } from "./vite-plugins/markdown-export";
 * import ContentProcessor from "./app/lib/content/content-processor";
 *
 * const processor = new ContentProcessor({ contentDir: "...", verbose: true });
 * export default defineConfig({
 *   plugins: [
 *     viteMarkdownExport({ processor }),
 *   ],
 * });
 * ```
 */
export function viteMarkdownExport(options: ViteMarkdownExportOptions): Plugin {
  const processor = options.processor;
  // Content directory is one level up from cloud/
  const contentDir = path.resolve(process.cwd(), "../content");

  /**
   * Generate markdown content for a given route path.
   * Returns null if no content found for the route.
   */
  async function generateMarkdownForRoute(
    routePath: string,
  ): Promise<string | null> {
    // Find content metadata for this route
    const metadata = processor.getMetadata();
    const allContent = [...metadata.docs, ...metadata.blog, ...metadata.policy];

    const content = allContent.find((c) => c.route === routePath);
    if (!content) {
      return null;
    }

    // Resolve the source MDX file path
    const mdxFilePath = path.join(contentDir, `${content.path}.mdx`);

    try {
      await fs.access(mdxFilePath);
    } catch {
      console.error(`[markdown-export] MDX file not found: ${mdxFilePath}`);
      return null;
    }

    // Preprocess the MDX to expand CodeExamples and strip frontmatter
    const preprocessed = await preprocessMdx(mdxFilePath);

    // Build the final markdown content with metadata and absolute URLs
    const absoluteContent = convertLinksToAbsolute(preprocessed.content);
    const frontmatter = [
      "---",
      `title: "${content.title}"`,
      `description: "${content.description}"`,
      `url: "${BASE_URL}${content.route}"`,
      "---",
      "",
    ].join("\n");

    return frontmatter + absoluteContent;
  }

  /**
   * Convert relative links and images to absolute URLs.
   */
  function convertLinksToAbsolute(content: string): string {
    // Convert markdown links: [text](/path) -> [text](https://mirascope.com/path)
    let result = content.replace(
      /\[([^\]]*)\]\(\/([^)]*)\)/g,
      `[$1](${BASE_URL}/$2)`,
    );

    // Convert markdown images: ![alt](/path) -> ![alt](https://mirascope.com/path)
    result = result.replace(
      /!\[([^\]]*)\]\(\/([^)]*)\)/g,
      `![$1](${BASE_URL}/$2)`,
    );

    return result;
  }

  return {
    name: "vite-plugin-markdown-export",
    enforce: "post",

    // Dev server: serve markdown files dynamically
    configureServer(server) {
      server.middlewares.use(async (req, res, next) => {
        // Only handle requests ending in .md
        if (!req.url?.endsWith(".md")) {
          return next();
        }

        // Parse the URL to extract the route path
        // URL format: /docs/learn/llm/calls.md -> route: /docs/learn/llm/calls
        const url = new URL(req.url, `http://${req.headers.host}`);
        const routePath = url.pathname.replace(/\.md$/, "");

        if (options.verbose) {
          console.log(`[markdown-export] Serving markdown for: ${routePath}`);
        }

        try {
          const markdown = await generateMarkdownForRoute(routePath);

          if (!markdown) {
            // No content found, let other middleware handle it
            return next();
          }

          res.setHeader("Content-Type", "text/markdown; charset=utf-8");
          res.setHeader("Cache-Control", "no-cache");
          res.statusCode = 200;
          res.end(markdown);
        } catch (error) {
          console.error(
            `[markdown-export] Error generating markdown for ${routePath}:`,
            error,
          );
          next(error);
        }
      });
    },

    // Build mode: generate static .md files after the build
    buildApp: {
      order: "post",
      handler: async (builder) => {
        const outputDir =
          builder.environments["client"]?.config.build.outDir ??
          builder.config.build.outDir;

        const generatorOptions: MarkdownExportOptions = {
          processor: options.processor,
          outputDir,
          verbose: options.verbose,
        };

        await new MarkdownExporter(generatorOptions).generate();
      },
    },
  };
}
