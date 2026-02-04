import { cloudflare } from "@cloudflare/vite-plugin";
import tailwindcss from "@tailwindcss/vite";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import viteReact from "@vitejs/plugin-react";
import os from "os";
import path from "path";
import { defineConfig } from "vite";

import ContentProcessor from "./app/lib/content/content-processor";
import { viteContent } from "./vite-plugins/content";
import { viteImages } from "./vite-plugins/images";
import { viteMarkdownExport } from "./vite-plugins/markdown-export";
import { viteMDX } from "./vite-plugins/mdx";
import { pagefindDev } from "./vite-plugins/pagefind-dev";
import { viteRobots } from "./vite-plugins/robots";
import { viteSocialCards } from "./vite-plugins/social-cards";

// Init shared content processor instance
const processor = new ContentProcessor({
  contentDir: path.resolve(process.cwd(), "../content"),
  verbose: true,
});
// Pre-run content processing at startup
await processor.processAllContent();

// Filter pages to include in prerendering and robots.txt
const filterPages = (page: { path: string }) => {
  return (
    !page.path.startsWith("/cloud") &&
    !page.path.startsWith("/dev") &&
    !page.path.startsWith("/discord-invite")
  );
};

/**
 * Prerender concurrency based on available CPU cores.
 *
 * Uses CPU count as a proxy for machine size since prerendering is I/O bound
 * (Miniflare connection pool) rather than CPU bound. The 2x multiplier with
 * cap of 20 balances throughput vs connection exhaustion:
 *
 * - CI (2 cores): 4 concurrent (safely under the ~14 threshold that caused failures)
 * - Local (10 cores): 20 concurrent (capped, tested stable up to 100)
 */
const prerenderConcurrency = Math.min(
  (os.availableParallelism?.() ?? os.cpus().length) * 2,
  20,
);
console.log(`[prerender] Prerender concurrency: ${prerenderConcurrency}`);

export default defineConfig(() => {
  return {
    server: {
      port: 3000,
    },
    plugins: [
      viteContent({ processor }),
      viteMDX(),
      viteImages({
        viteEnvironments: ["client"],
        skipPatterns: [/\/social-cards\//],
      }),
      cloudflare({ viteEnvironment: { name: "ssr" } }),
      tanstackStart({
        srcDirectory: "app",
        pages: processor.getPages(filterPages),
        prerender: {
          enabled: true,
          crawlLinks: true,
          autoStaticPathsDiscovery: true,
          autoSubfolderIndex: false,
          concurrency: prerenderConcurrency,
          // NOTE: Bug in TanStack Start that explicit retries will let 404 errors slip through.
          retryCount: 0,
          retryDelay: 0,
          maxRedirects: 5,
          failOnError: true,
          // for now, pages not included in prerendering will be disallowed in robots.txt
          filter: filterPages,
          // Setting changefreq per-page is supported
          onSuccess: ({ page }: { page: { path: string } }) => {
            console.log(`[prerender] Rendered ${page.path}!`);
            let changefreq = "daily";
            if (page.path.startsWith("/blog/")) {
              changefreq = "weekly";
            }
            return { sitemap: { changefreq } };
          },
        },
        sitemap: {
          enabled: true,
          host: "https://mirascope.com",
        },
      }),
      viteRobots(), // Generate robots disallow paths from sitemap (must be after tanstackStart)
      viteSocialCards({ processor }), // Generate social card images from sitemap (must be after tanstackStart)
      viteMarkdownExport({ processor }), // Generate markdown files for content negotiation (must be after tanstackStart)
      pagefindDev(),
      viteReact(),
      tailwindcss(),
    ],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./"),
      },
    },
  };
});
