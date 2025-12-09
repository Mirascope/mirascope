import path from "path";
import { coverageConfigDefaults, defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: false,
    environment: "node",
    // globalSetup: "./tests/db/global.ts",
    // setupFiles: "./tests/db/setup.ts",
    pool: "forks",
    poolOptions: {
      forks: {
        singleFork: true,
      },
    },
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      include: [
        "api",
        // "auth", // TODO: Add auth to coverage requirements
        "db",
      ],
      exclude: ["**/index.ts", ...coverageConfigDefaults.exclude],
      thresholds: {
        global: {
          branches: 100,
          functions: 100,
          lines: 100,
          statements: 100,
        },
      },
    },
    exclude: ["**/node_modules/**", "dist", ".git", ".cache"],
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./"),
    },
  },
});
