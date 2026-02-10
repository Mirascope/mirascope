/**
 * Vitest config for Miniflare-based integration tests.
 *
 * These tests spin up real Cloudflare Workers via Miniflare to test
 * service binding calls, Hono routing, and other runtime behavior
 * that can't be covered by unit tests with mocks.
 *
 * Note: We use Miniflare programmatically (not @cloudflare/vitest-pool-workers)
 * because that package requires vitest 2.x–3.2.x, and this project uses vitest 4.x.
 */
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["src/**/*.integration.test.ts"],
    // Integration tests need more time for Miniflare startup
    testTimeout: 30_000,
    hookTimeout: 30_000,
  },
});
