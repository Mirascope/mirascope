/**
 * Vite plugin for generating social card images
 *
 * Generates Open Graph / Twitter card images for all content pages.
 * Images are rendered using Satori (JSX to SVG) + resvg (SVG to PNG) + Sharp (PNG to WebP).
 *
 * Routes and titles are sourced from ContentProcessor, which processes all MDX content.
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
import ContentProcessor from "../app/lib/content/content-processor";

/**
 * Default configuration
 */
const DEFAULT_OPTIONS: Required<SocialImagesOptions> = {
  concurrency: 100,
  quality: 85,
  verbose: false,
};

/**
 * Static page titles for non-content pages
 * These pages don't have content metadata, so titles are hardcoded
 */
const DEFAULT_STATIC_TITLES: Record<string, string> = {
  // todo(sebastian): manage this upstream in a tanstack router type-safe way
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
  /** ContentProcessor instance to use for route -> title mapping */
  processor: ContentProcessor;
  /** Static page titles for non-content routes */
  staticTitles?: Record<string, string>;
  /** Output directory for social cards */
  outputDir: string;
}

/**
 * Generates social card images for content pages.
 *
 * Can be used standalone or within the Vite plugin.
 *
 * @example
 * ```typescript
 * // Standalone usage
 * const processor = new ContentProcessor({ contentDir: "...", verbose: true });
 * const generator = new SocialCardGenerator({ processor, outputDir: "dist/client", verbose: true });
 * const results = await generator.generate();
 * console.log(`Generated ${results.success} cards`);
 * ```
 */
export class SocialCardGenerator {
  private readonly config: Required<SocialImagesOptions>;
  private readonly processor: ContentProcessor;
  private readonly staticTitles: Record<string, string>;
  private readonly outputDir: string;

  private assets: { font: ArrayBuffer; background: string } | null = null;
  private titleLookup: Map<string, string> | null = null;
  private initialized = false;

  constructor(options: SocialCardGeneratorOptions) {
    if (!options.processor) {
      throw new Error(
        "[social-cards] processor option is required and must be a ContentProcessor instance",
      );
    }

    this.config = {
      concurrency: options.concurrency ?? DEFAULT_OPTIONS.concurrency,
      quality: options.quality ?? DEFAULT_OPTIONS.quality,
      verbose: options.verbose ?? DEFAULT_OPTIONS.verbose,
    };
    this.processor = options.processor;
    this.outputDir = options.outputDir;
    this.staticTitles = options.staticTitles ?? DEFAULT_STATIC_TITLES;
  }

  /**
   * Initialize the generator by loading assets and building the title lookup.
   * This is called automatically by generate() if not already initialized.
   */
  async initialize(): Promise<void> {
    if (this.initialized) return;

    // Process content if not already processed/validated (no-op if already done)
    await this.processor.processAllContent();

    this.assets = await loadAssets();
    this.titleLookup = this.processor.getRouteToTitleMap();
    this.initialized = true;
  }

  /**
   * Generate social cards for all content pages.
   *
   * @returns Generation results with counts and individual card outcomes
   */
  async generate(): Promise<GenerationResults> {
    const outputDir = path.resolve(this.outputDir, "social-cards");

    // Ensure initialized (loads assets and builds title lookup from processor)
    await this.initialize();

    // Get all routes from processor content and static titles
    const contentRoutes = Array.from(this.titleLookup!.keys());
    const staticRoutes = Object.keys(this.staticTitles);
    const allRoutes = [...new Set([...contentRoutes, ...staticRoutes])];

    if (allRoutes.length === 0) {
      console.log("[social-cards] No routes found");
      return { success: 0, skipped: 0, failed: 0, cards: [] };
    }

    console.log(
      `[social-cards] Generating social cards for ${allRoutes.length} pages...`,
    );

    // Create output directory
    await fs.mkdir(outputDir, { recursive: true });

    // Generate images with throughput-optimized sliding window concurrency
    const cards = new Array<CardResult>(allRoutes.length);
    const executing = new Set<Promise<void>>();

    for (let i = 0; i < allRoutes.length; i++) {
      const route = allRoutes[i];
      const index = i;

      const task = this.generateCard(route, outputDir).then((result) => {
        cards[index] = result;
      });

      const wrapped = task.finally(() => executing.delete(wrapped));
      executing.add(wrapped);

      if (executing.size >= this.config.concurrency) {
        await Promise.race(executing);
      }
    }

    await Promise.all(executing);

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
    if (contentTitle) {
      return contentTitle;
    }

    // Check static titles
    if (this.staticTitles[route]) {
      return this.staticTitles[route];
    }

    // todo(sebastian): perhaps a generic title as fallback is better?
    // Generate title from route path for unknown pages
    // e.g., "/docs/v1/learn" -> "Docs V1 Learn"
    const parts = route.split("/").filter(Boolean);
    if (parts.length === 0) return "Mirascope";

    return parts
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join(" ");
  }
}

// Route path -> social card filename (see app/lib/seo/head.ts)
function routeToFilename(route: string): string {
  // Canonicalize path (remove trailing slashes except for root)
  const cleanRoute = route === "/" ? route : route.replace(/\/+$/, "");
  // Remove leading slash and replace remaining slashes with dashes
  const filename = cleanRoute.replace(/^\//, "").replace(/\//g, "-") || "index";
  return `${filename}.webp`;
}

/**
 * Create the social cards Vite plugin.
 *
 * @example
 * ```typescript
 * // In vite.config.ts
 * import { viteSocialCards } from "./vite-plugins/social-cards";
 * import ContentProcessor from "./app/lib/content/content-processor";
 *
 * const processor = new ContentProcessor({ contentDir: "...", verbose: true });
 * export default defineConfig({
 *   plugins: [
 *     viteSocialCards({ processor, verbose: true }),
 *   ],
 * });
 * ```
 */
export function viteSocialCards({
  processor,
}: {
  processor: ContentProcessor;
}): Plugin {
  return {
    name: "vite-plugin-social-cards",
    enforce: "post",

    buildApp: {
      order: "post",
      handler: async (builder) => {
        const outputDir =
          builder.environments["client"]?.config.build.outDir ??
          builder.config.build.outDir;

        const options: SocialCardGeneratorOptions = {
          processor,
          outputDir,
          verbose: true,
        };
        await new SocialCardGenerator(options).generate();
      },
    },
  };
}
