import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["tests/integration/**/*.integration.test.ts"],
    // Integration tests spin up Miniflare instances which need more time
    testTimeout: 30_000,
    hookTimeout: 30_000,
  },
});
