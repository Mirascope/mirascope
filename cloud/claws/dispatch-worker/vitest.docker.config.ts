import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["tests/integration/*-docker.test.ts"],
    testTimeout: 30_000,
    hookTimeout: 90_000,
  },
});
