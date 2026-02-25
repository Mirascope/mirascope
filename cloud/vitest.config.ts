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
        "api",
        "auth",
        "db",
        "emails",
        "payments",
        "rate-limiting",
        "workers",
      ],
      exclude: [
        "app", // Currently manual testing only. We should cover this at some point
        "**.md",
        "**/index.ts",
        "api/api.ts", // Barrel file - re-exports and HttpApi.make() class definition
        "auth/errors.ts", // Data.TaggedError declarations - no executable code per v8
        "auth/oauth.ts", // OAuth flow with external network requests - tested via integration tests
        "workers/config.ts", // Type-only interfaces and type exports
        "db/migrations/**",
        "db/clickhouse/**",
        "db/schema/**",
        "tests/**",
        ".build-cache",
        ...coverageConfigDefaults.exclude,
      ],
      thresholds: {
        lines: 100,
        functions: 100,
        branches: 100,
        statements: 100,
      },
    },
    exclude: [
      "**/node_modules/**",
      "dist",
      ".git",
      ".cache",
      ".build-cache/**",
    ],
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./"),
      "cloudflare:workers": path.resolve(
        __dirname,
        "./tests/mocks/cloudflare-workers.ts",
      ),
    },
  },
});
