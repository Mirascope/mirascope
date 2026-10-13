/**
 * Worker thread for rendering social card images in parallel.
 *
 * Each worker loads assets once, then processes multiple cards.
 * This enables true CPU parallelism for the render pipeline.
 */

import fs from "node:fs/promises";
import path from "node:path";

import { loadAssets, renderSocialCard } from "../app/lib/social-cards/render";

/**
 * Cached assets loaded once per worker thread
 */
let assets: { font: ArrayBuffer; logo: string; background: string } | null =
  null;

/**
 * Task payload passed from main thread
 */
export interface WorkerTask {
  route: string;
  title: string;
  outputDir: string;
  quality: number;
}

/**
 * Result returned to main thread
 */
export type WorkerResult =
  | { status: "success"; route: string; filename: string }
  | { status: "failed"; route: string; error: string };

/**
 * Convert route path to social card filename
 * (duplicated from social-cards.ts to avoid circular imports)
 */
function routeToFilename(route: string): string {
  const cleanRoute = route === "/" ? route : route.replace(/\/+$/, "");
  const filename = cleanRoute.replace(/^\//, "").replace(/\//g, "-") || "index";
  return `${filename}.webp`;
}

/**
 * Render a single social card.
 *
 * This is the default export that piscina calls for each task.
 */
export default async function renderCard(
  task: WorkerTask,
): Promise<WorkerResult> {
  try {
    // Load assets once per worker (cached)
    if (!assets) {
      assets = await loadAssets();
    }

    const filename = routeToFilename(task.route);
    const outputPath = path.join(task.outputDir, filename);

    const webpBuffer = await renderSocialCard(task.title, assets, task.quality);
    await fs.writeFile(outputPath, webpBuffer);

    return { status: "success", route: task.route, filename };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    return { status: "failed", route: task.route, error: errorMessage };
  }
}
