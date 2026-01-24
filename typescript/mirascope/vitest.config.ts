import { config } from 'dotenv';
import { resolve } from 'path';
import { defineConfig } from 'vitest/config';

// Load .env for e2e tests (no-op if file doesn't exist)
config({ path: resolve(__dirname, '../.env') });

export default defineConfig({
  test: {
    globals: false,
    environment: 'node',
    include: ['src/**/*.test.ts', 'tests/**/*.test.ts'],
    testTimeout: 30000, // 30s for API calls in e2e tests
    coverage: {
      provider: 'v8',
      include: ['src/**/*.ts'],
      exclude: ['src/**/*.test.ts', 'src/**/index.ts'],
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
      '@/tests': resolve(__dirname, './tests'),
      '@': resolve(__dirname, './src'),
    },
  },
});
