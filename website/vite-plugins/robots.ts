/**
 * Vite plugin for generating robots.txt from sitemap
 *
 * Generates a production robots.txt from the sitemap, disallowing low-priority URLs.
 * The sitemap is generated during prerendering and only included entries have a
 * changefreq. Entries without changefreq will be disallowed.
 *
 * This plugin reads the generated sitemap.xml after build and extracts URLs that
 * don't have a changefreq tag at all, then generates a static robots.txt file in
 * dist/client/ that disallows those URLs.
 *
 * In development, public/robots.txt is served (allow all).
 * In production, dist/client/robots.txt (generated) is served.
 */

import type { Plugin } from "vite";

import fs from "node:fs/promises";
import path from "node:path";

import {
  parseSitemapForUrlsWithoutChangefreq,
  generateRobotsTxt,
} from "../app/lib/robots";
import { BASE_URL } from "../app/lib/site";

const SITEMAP_URL = `${BASE_URL}/sitemap.xml`;

export function viteRobots(): Plugin {
  return {
    name: "vite-plugin-robots",
    enforce: "post",

    buildApp: {
      order: "post",
      handler: async (builder) => {
        const clientOutDir =
          builder.environments["client"]?.config.build.outDir ??
          builder.config.build.outDir;
        const sitemapPath = path.resolve(
          process.cwd(),
          clientOutDir,
          "sitemap.xml",
        );
        const outputPath = path.resolve(
          process.cwd(),
          clientOutDir,
          "robots.txt",
        );

        // Fail if sitemap does not exist
        try {
          await fs.access(sitemapPath);
        } catch {
          throw new Error(`[robots] Sitemap not found at ${sitemapPath}`);
        }

        const sitemapXml = await fs.readFile(sitemapPath, "utf-8");
        const disallowPaths = parseSitemapForUrlsWithoutChangefreq(sitemapXml);
        const robotsContent = generateRobotsTxt(
          disallowPaths,
          BASE_URL,
          SITEMAP_URL,
        );

        await fs.writeFile(outputPath, robotsContent);
        console.log(
          `[robots] Generated robots.txt with ${disallowPaths.length} disallow paths`,
        );
      },
    },
  };
}
