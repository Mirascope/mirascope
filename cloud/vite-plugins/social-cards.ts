/**
 * Vite plugin for generating social card images
 *
 * Generates Open Graph / Twitter card images for all indexed pages in the sitemap.
 * Images are rendered using Satori (JSX to SVG) + resvg (SVG to PNG) + Sharp (PNG to WebP).
 *
 * This plugin runs as the final build step, after the sitemap is generated.
 * It reads URLs from sitemap.xml and titles from content metadata.
 *
 * Output: dist/client/social-cards/*.webp
 *
 * The SocialCardGenerator class can also be used standalone outside of Vite.
 */

import type { Plugin } from "vite";
import fs from "node:fs/promises";
import path from "node:path";

import type { SocialImagesOptions } from "../app/lib/social-cards/types";
import { loadAssets, renderSocialCard } from "../app/lib/social-cards/render";
import {
  parseSitemapForIndexedUrls,
  routeToFilename,
} from "../app/lib/social-cards/sitemap";
import { parseFrontmatter } from "../app/lib/content/frontmatter";
import { glob } from "glob";

/**
 * Default configuration
 */
const DEFAULT_OPTIONS: Required<SocialImagesOptions> = {
  concurrency: 10,
  quality: 85,
  verbose: false,
};

/**
 * Static page titles for non-content pages
 * These pages don't have content metadata, so titles are hardcoded
 */
const DEFAULT_STATIC_TITLES: Record<string, string> = {
  "/home": "Mirascope",
  "/pricing": "Pricing",
  "/docs": "Documentation",
  "/blog": "Blog",
};

/**
 * Result of generating a single social card
 */
export type CardResult =
  | { status: "success"; route: string; filename: string }
  | { status: "skipped"; route: string; reason: string }
  | { status: "failed"; route: string; error: string };

/**
 * Aggregated results from generating all social cards
 */
export interface GenerationResults {
  success: number;
  skipped: number;
  failed: number;
  cards: CardResult[];
}

/**
 * Configuration options for the SocialCardGenerator
 */
export interface SocialCardGeneratorOptions extends SocialImagesOptions {
  /** Directory containing MDX content files (default: "content" relative to cwd) */
  contentDir?: string;
  /** Static page titles for non-content routes */
  staticTitles?: Record<string, string>;
  /** Base directory for resolving paths (default: process.cwd()) */
  baseDir?: string;
}

/**
 * Generates social card images for indexed pages.
 *
 * Can be used standalone or within the Vite plugin.
 *
 * @example
 * ```typescript
 * // Standalone usage
 * const generator = new SocialCardGenerator({ verbose: true });
 * await generator.initialize();
 * const results = await generator.generate("dist/client");
 * console.log(`Generated ${results.success} cards`);
 * ```
 */
export class SocialCardGenerator {
  private readonly config: Required<SocialImagesOptions>;
  private readonly contentDir: string;
  private readonly staticTitles: Record<string, string>;
  private readonly baseDir: string;

  private assets: { font: ArrayBuffer; background: string } | null = null;
  private titleLookup: Map<string, string> | null = null;
  private initialized = false;

  constructor(options?: SocialCardGeneratorOptions) {
    this.config = {
      concurrency: options?.concurrency ?? DEFAULT_OPTIONS.concurrency,
      quality: options?.quality ?? DEFAULT_OPTIONS.quality,
      verbose: options?.verbose ?? DEFAULT_OPTIONS.verbose,
    };
    this.baseDir = options?.baseDir ?? process.cwd();
    this.contentDir =
      options?.contentDir ?? path.resolve(this.baseDir, "content");
    this.staticTitles = options?.staticTitles ?? DEFAULT_STATIC_TITLES;
  }

  /**
   * Initialize the generator by loading assets and building the title lookup.
   * This is called automatically by generate() if not already initialized.
   */
  async initialize(): Promise<void> {
    if (this.initialized) return;

    const [assets, titleLookup] = await Promise.all([
      loadAssets(),
      this.buildTitleLookup(),
    ]);

    this.assets = assets;
    this.titleLookup = titleLookup;
    this.initialized = true;
  }

  /**
   * Generate social cards for all indexed pages in the sitemap.
   *
   * @param clientOutDir - Output directory containing sitemap.xml (e.g., "dist/client")
   * @returns Generation results with counts and individual card outcomes
   */
  async generate(clientOutDir: string): Promise<GenerationResults> {
    const sitemapPath = path.resolve(this.baseDir, clientOutDir, "sitemap.xml");
    const outputDir = path.resolve(this.baseDir, clientOutDir, "social-cards");

    // Check if sitemap exists
    const sitemapExists = await this.fileExists(sitemapPath);
    if (!sitemapExists) {
      console.warn(
        `[social-cards] Sitemap not found at ${sitemapPath}, skipping social card generation`,
      );
      return { success: 0, skipped: 0, failed: 0, cards: [] };
    }

    // Read and parse sitemap
    const sitemapXml = await fs.readFile(sitemapPath, "utf-8");
    const indexedUrls = parseSitemapForIndexedUrls(sitemapXml);

    if (indexedUrls.length === 0) {
      console.log("[social-cards] No indexed URLs found in sitemap");
      return { success: 0, skipped: 0, failed: 0, cards: [] };
    }

    console.log(
      `[social-cards] Generating social cards for ${indexedUrls.length} pages...`,
    );

    // Ensure initialized
    await this.initialize();

    // Create output directory
    await fs.mkdir(outputDir, { recursive: true });

    // Generate images with concurrency limit
    const cards: CardResult[] = [];

    for (let i = 0; i < indexedUrls.length; i += this.config.concurrency) {
      const batch = indexedUrls.slice(i, i + this.config.concurrency);

      const batchResults = await Promise.all(
        batch.map((route) => this.generateCard(route, outputDir)),
      );

      cards.push(...batchResults);
    }

    // Aggregate results
    const results: GenerationResults = {
      success: cards.filter((c) => c.status === "success").length,
      skipped: cards.filter((c) => c.status === "skipped").length,
      failed: cards.filter((c) => c.status === "failed").length,
      cards,
    };

    console.log(
      `[social-cards] Complete: ${results.success} generated, ${results.skipped} skipped, ${results.failed} failed`,
    );

    return results;
  }

  /**
   * Generate a single social card for a route.
   */
  private async generateCard(
    route: string,
    outputDir: string,
  ): Promise<CardResult> {
    try {
      const title = this.getTitle(route);

      if (!title) {
        if (this.config.verbose) {
          console.log(`[social-cards] Skipping ${route} (no title found)`);
        }
        return { status: "skipped", route, reason: "no title found" };
      }

      const filename = routeToFilename(route);
      const outputPath = path.join(outputDir, filename);

      const webpBuffer = await renderSocialCard(
        title,
        this.assets!,
        this.config.quality,
      );
      await fs.writeFile(outputPath, webpBuffer);

      if (this.config.verbose) {
        console.log(`[social-cards] Generated ${filename}`);
      }

      return { status: "success", route, filename };
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : String(error);
      console.error(
        `[social-cards] Failed to generate card for ${route}:`,
        errorMessage,
      );
      return { status: "failed", route, error: errorMessage };
    }
  }

  /**
   * Get the title for a route, checking content metadata first, then static titles.
   */
  private getTitle(route: string): string | null {
    // Check content metadata first
    const contentTitle = this.titleLookup?.get(route);
    if (contentTitle) return contentTitle;

    // Check static titles
    if (this.staticTitles[route]) {
      return this.staticTitles[route];
    }

    // Generate title from route path for unknown pages
    // e.g., "/docs/v1/learn" -> "Docs V1 Learn"
    const parts = route.split("/").filter(Boolean);
    if (parts.length === 0) return "Mirascope";

    return parts
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join(" ");
  }

  /**
   * Build a lookup map of route -> title from content metadata.
   */
  private async buildTitleLookup(): Promise<Map<string, string>> {
    const lookup = new Map<string, string>();

    // Scan all MDX files in content directory
    const mdxFiles = await glob(path.join(this.contentDir, "**/*.mdx"));

    for (const filePath of mdxFiles) {
      try {
        const content = await fs.readFile(filePath, "utf-8");
        const { frontmatter } = parseFrontmatter(content);

        if (!frontmatter.title) continue;

        // Derive route from file path
        const route = this.filePathToRoute(filePath);
        if (route) {
          lookup.set(route, frontmatter.title);
        }
      } catch {
        // Skip files that can't be parsed
      }
    }

    return lookup;
  }

  /**
   * Convert a file path to a route.
   * This is a simplified version - the actual routing is more complex.
   */
  private filePathToRoute(filePath: string): string | null {
    const relativePath = path.relative(this.contentDir, filePath);
    const parts = relativePath.replace(/\.mdx$/, "").split(path.sep);

    if (parts.length === 0) return null;

    const contentType = parts[0];
    const rest = parts.slice(1);

    switch (contentType) {
      case "blog":
        // blog/my-post.mdx -> /blog/my-post
        return `/blog/${rest.join("/")}`;

      case "docs":
        // docs/v1/learn/intro.mdx -> /docs/v1/learn/intro
        // Handle index files
        if (rest[rest.length - 1] === "index") {
          rest.pop();
        }
        return `/docs/${rest.join("/")}`;

      case "policy":
        // policy/terms/service.mdx -> /terms/service
        // policy/privacy.mdx -> /privacy
        return `/${rest.join("/")}`;

      default:
        return null;
    }
  }

  /**
   * Check if a file exists.
   */
  private async fileExists(filePath: string): Promise<boolean> {
    try {
      await fs.access(filePath);
      return true;
    } catch {
      return false;
    }
  }
}

/**
 * Create the social cards Vite plugin.
 *
 * @example
 * ```typescript
 * // In vite.config.ts
 * import { viteSocialCards } from "./vite-plugins/social-cards";
 *
 * export default defineConfig({
 *   plugins: [
 *     viteSocialCards({ verbose: true }),
 *   ],
 * });
 * ```
 */
export function viteSocialCards(options?: SocialImagesOptions): Plugin {
  const generator = new SocialCardGenerator(options);

  return {
    name: "vite-plugin-social-cards",
    enforce: "post",

    buildApp: {
      order: "post",
      handler: async (builder) => {
        const clientOutDir =
          builder.environments["client"]?.config.build.outDir ??
          builder.config.build.outDir;

        await generator.generate(clientOutDir);
      },
    },
  };
}
