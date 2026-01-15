import path from "path";
import { coverageConfigDefaults, defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: false,
    environment: "node",
    globalSetup: "./tests/global-setup.ts",
    pool: "forks",
    maxWorkers: 1,
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      include: [
        "analytics",
        "api",
        "auth",
        "db",
        "emails",
        "payments",
        "workers",
      ],
      exclude: [
        "**/index.ts",
        "db/migrations/**",
        "db/schema/**",
        "tests/**",
        "workers/clickhouseCron.ts", // TODO: remove this when we switch to ClickHouse + Durable Objects
        "workers/outboxProcessor.ts", // TODO: remove this when we switch to ClickHouse + Durable Objects
        ...coverageConfigDefaults.exclude,
      ],
      thresholds: {
        lines: 100,
        functions: 100,
        branches: 100,
        statements: 100,
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
