import { cloudflare } from "@cloudflare/vite-plugin";
import tailwindcss from "@tailwindcss/vite";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import viteReact from "@vitejs/plugin-react";
import path from "path";
import { viteMDX } from "./vite-plugins/mdx";
import { viteContent } from "./vite-plugins/content";
import { viteImages } from "./vite-plugins/images";
import { viteRobots } from "./vite-plugins/robots";
import { viteSocialCards } from "./vite-plugins/social-cards";
import { pagefindDev } from "./vite-plugins/pagefind-dev";
import { defineConfig } from "vite";
import ContentProcessor from "./app/lib/content/content-processor";

// Init shared content processor instance
const processor = new ContentProcessor({
  contentDir: path.resolve(process.cwd(), "content"),
  verbose: true,
});
// Pre-run content processing at startup
await processor.processAllContent();

// Filter pages to include in prerendering and robots.txt
const filterPages = (page: { path: string }) => {
  return (
    !page.path.startsWith("/cloud") && !page.path.startsWith("/discord-invite")
  );
};

export default defineConfig(() => {
  return {
    server: {
      port: 3000,
    },
    plugins: [
      viteContent({ processor }),
      viteMDX(),
      viteImages({ viteEnvironments: ["client"] }),
      cloudflare({ viteEnvironment: { name: "ssr" } }),
      tanstackStart({
        srcDirectory: "app",
        pages: processor.getPages(filterPages),
        prerender: {
          enabled: true,
          crawlLinks: true,
          autoStaticPathsDiscovery: true,
          autoSubfolderIndex: false,
          concurrency: 14,
          // NOTE: Bug in TanStack Start that explicit retries will let 404 errors slip through.
          retryCount: 0,
          retryDelay: 0,
          maxRedirects: 5,
          failOnError: true,
          // for now, pages not included in prerendering will be disallowed in robots.txt
          filter: filterPages,
          // Setting changefreq per-page is supported
          onSuccess: ({ page }: { page: { path: string } }) => {
            console.log(`Rendered ${page.path}!`);
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
