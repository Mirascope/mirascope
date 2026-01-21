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
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

import Piscina from "piscina";

import type { SocialImagesOptions } from "../app/lib/social-cards/types";
import ContentProcessor from "../app/lib/content/content-processor";
import type { WorkerTask, WorkerResult } from "./social-cards-worker";
import {
  getStaticRouteTitle,
  getStaticRoutes,
} from "../app/lib/seo/static-route-head";

/**
 * Default concurrency based on available CPU cores.
 * Leaves 1 core for the main thread.
 */
const DEFAULT_CONCURRENCY = Math.max(
  (os.availableParallelism?.() ?? os.cpus().length) - 1,
  1,
);

/**
 * Default configuration
 */
const DEFAULT_OPTIONS: Required<SocialImagesOptions> = {
  concurrency: DEFAULT_CONCURRENCY,
  quality: 85,
  verbose: false,
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
  private readonly outputDir: string;

  private titleLookup: Map<string, string> | null = null;
  private initialized = false;

  constructor(options: SocialCardGeneratorOptions) {
    if (!options.processor) {
      throw new Error(
        "[social-cards] processor option is required and must be a ContentProcessor instance",
      );
    }

    this.config = {
      concurrency: Math.max(
        options.concurrency ?? DEFAULT_OPTIONS.concurrency,
        1,
      ),
      quality: options.quality ?? DEFAULT_OPTIONS.quality,
      verbose: options.verbose ?? DEFAULT_OPTIONS.verbose,
    };
    this.processor = options.processor;
    this.outputDir = options.outputDir;
  }

  /**
   * Initialize the generator by building the title lookup.
   * This is called automatically by generate() if not already initialized.
   */
  async initialize(): Promise<void> {
    if (this.initialized) return;

    // Process content if not already processed/validated (no-op if already done)
    await this.processor.processAllContent();

    this.titleLookup = this.processor.getRouteToTitleMap();
    this.initialized = true;
  }

  /**
   * Generate social cards for all content pages.
   *
   * Uses a worker thread pool for true CPU parallelism.
   *
   * @returns Generation results with counts and individual card outcomes
   */
  async generate(): Promise<GenerationResults> {
    const outputDir = path.resolve(this.outputDir, "social-cards");

    // Ensure initialized (builds title lookup from processor)
    await this.initialize();

    // Get all routes from processor content and static route registry
    const contentRoutes = Array.from(this.titleLookup!.keys());
    const staticRoutes = getStaticRoutes();
    const allRoutes = [...new Set([...contentRoutes, ...staticRoutes])];

    if (allRoutes.length === 0) {
      console.log("[social-cards] No routes found");
      return { success: 0, skipped: 0, failed: 0, cards: [] };
    }

    console.log(
      `[social-cards] Generating social cards for ${allRoutes.length} pages (${this.config.concurrency} workers)...`,
    );

    // Create output directory
    await fs.mkdir(outputDir, { recursive: true });

    // Create worker pool for parallel rendering
    // Uses tsx loader so workers can run TypeScript directly
    const workerPath = fileURLToPath(
      new URL("./social-cards-worker.ts", import.meta.url),
    );
    const pool = new Piscina({
      filename: workerPath,
      maxThreads: this.config.concurrency,
      execArgv: ["--import", "tsx"],
    });

    // Track progress for real-time logging
    let completed = 0;
    const total = allRoutes.length;

    // Build tasks, handling skipped routes in main thread
    // Each task logs on completion for real-time progress
    const taskPromises = allRoutes.map((route): Promise<CardResult> => {
      const title = this.getTitle(route);

      if (!title) {
        completed++;
        if (this.config.verbose) {
          console.log(
            `[social-cards] [${completed}/${total}] Skipped ${route} (no title)`,
          );
        }
        return Promise.resolve({
          status: "skipped",
          route,
          reason: "no title found",
        });
      }

      const task: WorkerTask = {
        route,
        title,
        outputDir,
        quality: this.config.quality,
      };

      // Run task and log on completion
      return (pool.run(task) as Promise<WorkerResult>).then((result) => {
        completed++;
        if (result.status === "failed") {
          console.error(
            `[social-cards] Failed to generate card for ${route}:`,
            result.error,
          );
        }
        if (this.config.verbose) {
          if (result.status === "success") {
            console.log(
              `[social-cards] [${completed}/${total}] Generated ${result.filename}`,
            );
          }
        }
        return result;
      });
    });

    // Wait for all tasks to complete
    const cards = await Promise.all(taskPromises);

    // Cleanup worker pool
    await pool.destroy();

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
   * Get the title for a route, checking content metadata first, then static routes.
   */
  private getTitle(route: string): string | null {
    // Check content metadata first
    const contentTitle = this.titleLookup?.get(route);
    if (contentTitle) {
      return contentTitle;
    }

    // Check static route registry (logs warning if not found)
    const staticTitle = getStaticRouteTitle(route);
    if (staticTitle) {
      return staticTitle;
    }

    console.warn(`[social-cards] No title specified for route: ${route}`);

    // Fallback: generate title from route path for unknown pages
    // e.g., "/docs/v1/learn" -> "Docs V1 Learn"
    const parts = route.split("/").filter(Boolean);
    if (parts.length === 0) return "Mirascope";

    return parts
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join(" ");
  }
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
        };
        await new SocialCardGenerator(options).generate();
      },
    },
  };
}
