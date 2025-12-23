import { cloudflare } from "@cloudflare/vite-plugin";
import tailwindcss from "@tailwindcss/vite";
import tsConfigPaths from "vite-tsconfig-paths";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import viteReact from "@vitejs/plugin-react";
import path from "path";
import { optimizedImageMiddleware } from "./vite/optimized-image-middleware";
import { defineConfig } from "vite";
// import { contentPreprocessPlugin } from "./scripts/preprocess-content";

export default defineConfig(() => {
  return {
    server: {
      port: 3000,
    },
    plugins: [
      tsConfigPaths({
        projects: ["./tsconfig.json"],
      }),
      cloudflare({ viteEnvironment: { name: "ssr" } }),
      tanstackStart({
        srcDirectory: "app",
      }),
      viteReact(),
      tailwindcss(),
      // contentPreprocessPlugin(),
      optimizedImageMiddleware(),
    ],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./"),
      },
    },
  };
});
