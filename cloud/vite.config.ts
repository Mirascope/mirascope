import { cloudflare } from "@cloudflare/vite-plugin";
import tailwindcss from "@tailwindcss/vite";
import tsConfigPaths from "vite-tsconfig-paths";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import viteReact from "@vitejs/plugin-react";
import path from "path";
import { viteMDX } from "./vite-plugins/mdx";
import { viteContent } from "./vite-plugins/content";
import { viteImages } from "./vite-plugins/images";
import { defineConfig } from "vite";

export default defineConfig(() => {
  const contentDir = path.resolve(process.cwd(), "content");
  return {
    server: {
      port: 3000,
    },
    plugins: [
      tsConfigPaths({
        projects: ["./tsconfig.json"],
      }),
      viteContent({ contentDir }),
      viteMDX(),
      viteImages({ viteEnvironments: ["client"] }),
      cloudflare({ viteEnvironment: { name: "ssr" } }),
      tanstackStart({
        srcDirectory: "app",
        prerender: {
          enabled: true,
          crawlLinks: true,
          autoSubfolderIndex: true,
          autoStaticPathsDiscovery: true,
          concurrency: 14,
          // NOTE: Bug in TanStack Start that explicit retries will let 404 errors slip through.
          retryCount: 0,
          retryDelay: 0,
          maxRedirects: 5,
          failOnError: true,
          filter: (page: { path: string }) =>
            page.path.startsWith("/docs") || page.path.startsWith("/blog"),
          // todo(sebastian): Consider post-processing sitemap/pages to set the changefreq.
          // When using autoStaticPathsDiscovery, you can't set the sitemap changefreq or
          // other sitemap options per page—frequency can only be set on a per-page basis if you provide
          // an explicit pages array. For auto-discovered pages, control over frequency is not available.
          onSuccess: ({ page }: { page: { path: string } }) => {
            console.log(`Rendered ${page.path}!`);
            return { sitemap: { changefreq: "daily" } };
          },
        },
        sitemap: {
          enabled: true,
          host: "https://mirascope.com",
        },
      }),
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
