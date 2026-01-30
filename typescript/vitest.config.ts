import { config } from "dotenv";
import { resolve } from "path";
import { defineConfig } from "vitest/config";

import { mirascope } from "./src/transform/plugins/vite";

// Load .env for e2e tests (no-op if file doesn't exist)
config({ path: resolve(__dirname, ".env") });

export default defineConfig({
  plugins: [mirascope()],
  test: {
    globals: false,
    environment: "node",
    include: ["src/**/*.test.ts", "tests/**/*.test.ts"],
    testTimeout: 30000, // 30s for API calls in e2e tests
    coverage: {
      provider: "v8",
      include: ["src/**/*.ts"],
      exclude: [
        "src/**/*.test.ts",
        "src/**/index.ts",
        "src/bun.ts",
        // compile-time transformer runs in build plugins, difficult to unit test
        "src/transform/transformer.ts",
        // type files with nothing to cover
        "src/transform/plugins/types.ts",
        "src/llm/models/params.ts",
        "src/llm/models/thinking-config.ts",
        "src/llm/providers/model-id.ts",
        "src/llm/types/jsonable.ts",
        "src/llm/types/vars.ts",
        "src/llm/formatting/partial.ts",
        "src/llm/content/text.ts",
        "src/llm/content/thought.ts",
        "src/llm/content/tool-call.ts",
      ],
      thresholds: {
        lines: 100,
        functions: 100,
        branches: 100,
        statements: 100,
      },
    },
  },
  resolve: {
    alias: {
      "@/tests": resolve(__dirname, "./tests"),
      "@": resolve(__dirname, "./src"),
    },
  },
});
