import { cloudflare } from "@cloudflare/vite-plugin";
import tailwindcss from "@tailwindcss/vite";
import tsConfigPaths from "vite-tsconfig-paths";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import viteReact from "@vitejs/plugin-react";
import path from "path";
import { viteMDX } from "./vite-plugins/mdx";
import { viteImages } from "./vite-plugins/images";
import { defineConfig } from "vite";

export default defineConfig(() => {
  return {
    server: {
      port: 3000,
    },
    plugins: [
      tsConfigPaths({
        projects: ["./tsconfig.json"],
      }),
      viteMDX(),
      viteImages({ viteEnvironments: ["client"] }),
      cloudflare({ viteEnvironment: { name: "ssr" } }),
      tanstackStart({
        srcDirectory: "app",
        prerender: {
          enabled: true,
          autoSubfolderIndex: true,
          autoStaticPathsDiscovery: true,
          concurrency: 14,
          retryCount: 2,
          retryDelay: 1000,
          maxRedirects: 5,
          failOnError: true,
          filter: ({ path }) => path.startsWith("/docs"),
          onSuccess: ({ page }) => {
            console.log(`Rendered ${page.path}!`);
          },
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
