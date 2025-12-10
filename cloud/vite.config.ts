import { cloudflare } from "@cloudflare/vite-plugin";
import tailwindcss from "@tailwindcss/vite";
import tsConfigPaths from "vite-tsconfig-paths";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import viteReact from "@vitejs/plugin-react";
import path from "path";
import { defineConfig } from "vite";

export default defineConfig(() => {
  return {
    server: {
      port: 3000,
      fs: {
        strict: false,
      },
    },
    plugins: [
      tsConfigPaths({
        projects: ["./tsconfig.json"],
      }),
      cloudflare({ viteEnvironment: { name: "ssr" } }),
      tanstackStart(),
      viteReact(),
      tailwindcss(),
      // Note: Website content preprocessing plugins (contentPreprocessPlugin, optimizedImageMiddleware,
      // json404Middleware, pagefindDevPlugin) are designed for static site generation.
      // For SSR with TanStack Start, content should be loaded at request time or pre-built separately.
      // Run `bun run preprocess-content` before build to generate static content.
    ],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./"),
      },
    },
    // Add node-specific configuration for fs and path
    optimizeDeps: {
      esbuildOptions: {
        define: {
          global: "globalThis",
        },
      },
      exclude: ["content"],
    },
    // Keeping the default build configuration
    build: {
      assetsInlineLimit: 4096,
    },
  };
});
