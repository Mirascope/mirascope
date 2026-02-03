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
    setupFiles: ["./tests/setup.ts"],
    testTimeout: 30000, // 30s for API calls in e2e tests
    coverage: {
      provider: "v8",
      include: ["src/**/*.ts"],
      exclude: [
        "src/**/*.test.ts",
        "src/**/__fixtures__/**",
        "src/**/index.ts",
        "src/bun.ts",
        "src/ops/_internal/types.ts",
        // generated Fern code
        "src/api/_generated",
        "src/globals.d.ts",
        // compile-time transformer and closure collector run in build plugins, difficult to unit test
        "src/transform/transformer.ts",
        "src/ops/_internal/closure.ts",
        "src/ops/_internal/closure-collector.ts",
        // MCP transports use dynamic imports and are tested via e2e with stdio
        // SSE and HTTP transports follow same pattern but are flaky (like Python)
        "src/llm/mcp/transports.ts",
        // type files with nothing to cover
        "src/llm/mcp/types.ts",
        "src/llm/models/params.ts",
        "src/llm/models/thinking-config.ts",
        "src/llm/providers/model-id.ts",
        "src/llm/types/jsonable.ts",
        "src/llm/types/vars.ts",
        "src/llm/formatting/partial.ts",
        "src/llm/content/text.ts",
        "src/llm/content/thought.ts",
        "src/llm/content/tool-call.ts",
        "src/ops/_internal/instrumentation/providers/types.d.ts",
        "src/transform/plugins/types.ts",
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
