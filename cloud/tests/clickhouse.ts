import { Effect, Layer } from "effect";
import { describe, expect, it as vitestIt } from "@effect/vitest";
import { createCustomIt } from "@/tests/shared";
import { ClickHouse } from "@/clickhouse/client";
import { SettingsService, type Settings } from "@/settings";
import { CLICKHOUSE_CONNECTION_FILE } from "@/tests/global-setup";
import fs from "fs";

// Re-export describe and expect for convenience
export { describe, expect };

type ClickHouseConnectionFile = {
  url: string;
  user: string;
  password: string;
  database: string;
  nativePort: number;
};

function getTestClickHouseConfig(): ClickHouseConnectionFile {
  try {
    const raw = fs.readFileSync(CLICKHOUSE_CONNECTION_FILE, "utf-8");
    return JSON.parse(raw) as ClickHouseConnectionFile;
  } catch {
    throw new Error(
      "TEST_CLICKHOUSE_URL not set. Ensure global-setup.ts ran successfully.",
    );
  }
}

const clickhouseConfig = getTestClickHouseConfig();

export const checkClickHouseAvailable = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${clickhouseConfig.url}/ping`, {
      method: "GET",
      signal: AbortSignal.timeout(2000),
    });
    return response.ok;
  } catch {
    return false;
  }
};

export const clickHouseAvailable = await checkClickHouseAvailable();

/**
 * Test settings for ClickHouse.
 */
const testSettings: Settings = {
  env: "local",
  CLICKHOUSE_URL: clickhouseConfig.url,
  CLICKHOUSE_USER: clickhouseConfig.user,
  CLICKHOUSE_PASSWORD: clickhouseConfig.password,
  CLICKHOUSE_DATABASE: clickhouseConfig.database,
  CLICKHOUSE_TLS_ENABLED: false,
};

/**
 * Settings layer for tests.
 */
const TestSettingsLayer = Layer.succeed(SettingsService, testSettings);

/**
 * ClickHouse layer for tests.
 * Note: Layer may fail with SqlError | ConfigError during initialization.
 */
export const TestClickHouse = ClickHouse.Default.pipe(
  Layer.provide(TestSettingsLayer),
);

/**
 * Services that are automatically provided to all `it.effect` tests.
 */
export type TestServices = ClickHouse;

/**
 * Wraps a test function to automatically provide TestClickHouse.
 */
const wrapEffectTest =
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (original: any) =>
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (name: any, fn: any, timeout?: any) => {
      // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
      const runner = clickHouseAvailable ? original : vitestIt.effect.skip;
      // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-return
      return runner(
        name,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-return, @typescript-eslint/no-unnecessary-type-assertion
        () => (fn() as any).pipe(Effect.provide(TestClickHouse)),
        timeout,
      );
    };

/**
 * Type-safe `it` with `it.effect` that automatically provides TestClickHouse.
 *
 * Use this instead of importing directly from @effect/vitest.
 */
export const it = createCustomIt<TestServices>(wrapEffectTest);
