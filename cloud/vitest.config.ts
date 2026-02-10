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
        "cloudflare",
        "db",
        "claws",
        "emails",
        "payments",
        "rate-limiting",
        "workers",
      ],
      exclude: [
        "app", // Currently manual testing only. We should cover this at some point
        "**.md",
        "**/index.ts",
        // dispatch-worker has its own package.json and own tests
        "cloud/claws/dispatch-worker/**",
        "db/migrations/**",
        "db/clickhouse/**",
        "db/schema/**",
        "api/api.ts", // Declarative API composition, no logic to test
        "workers/config.ts", // Type declarations only, no executable code
        "auth/errors.ts", // Pure error class definitions
        "auth/oauth.ts", // OAuth flows (external network deps, v8-ignored)
        "cloudflare/containers/service.ts", // Service interface (Context.Tag only)
        "cloudflare/containers/types.ts", // Pure type definitions
        "cloudflare/r2/service.ts", // Service interface (Context.Tag only)
        "cloudflare/r2/types.ts", // Pure type definitions
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
      "claws/dispatch-worker/**",
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
