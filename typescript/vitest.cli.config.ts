import { resolve } from "path";
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: false,
    environment: "node",
    include: ["tests/cli/**/*.test.ts"],
    testTimeout: 10000,
  },
  resolve: {
    alias: {
      "@/tests": resolve(__dirname, "./tests"),
      "@": resolve(__dirname, "./src"),
    },
  },
});
