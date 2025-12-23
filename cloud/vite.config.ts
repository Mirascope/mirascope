import { cloudflare } from "@cloudflare/vite-plugin";
import tailwindcss from "@tailwindcss/vite";
import tsConfigPaths from "vite-tsconfig-paths";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import viteReact from "@vitejs/plugin-react";
import path from "path";
// import { contentPreprocessPlugin } from "./scripts/preprocess-content";
import { optimizedImageMiddleware } from "./scripts/optimized-image-middleware";
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
      cloudflare({ viteEnvironment: { name: "ssr" } }),
      tanstackStart({
        srcDirectory: "app",
      }),
      viteReact(),
      // todo(sebastian): why does this stumble over the @/ aliases but works in website?
      // contentPreprocessPlugin(),
      tailwindcss(),
      optimizedImageMiddleware(),
    ],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./"),
      },
    },
  };
});
