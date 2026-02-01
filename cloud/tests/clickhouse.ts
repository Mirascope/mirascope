import { describe, expect, it as vitestIt } from "@effect/vitest";
import { Effect, Layer } from "effect";

import { ClickHouse } from "@/db/clickhouse/client";
import { Settings, type SettingsConfig } from "@/settings";
import { getTestClickHouseConfig } from "@/tests/global-setup";
import { createMockSettings } from "@/tests/settings";
import { createCustomIt } from "@/tests/shared";

// Re-export describe and expect for convenience
export { describe, expect };

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
 * Creates test ClickHouse settings from the testcontainers config.
 * Centralizes the TLS configuration used across test layers.
 */
export function createTestClickHouseSettings(): SettingsConfig {
  return createMockSettings({
    clickhouse: {
      url: clickhouseConfig.url,
      user: clickhouseConfig.user,
      password: clickhouseConfig.password,
      database: clickhouseConfig.database,
      tls: {
        enabled: false,
        ca: "",
        skipVerify: true,
        hostnameVerify: false,
        minVersion: "1.2",
      },
    },
  });
}

/**
 * Complete test settings using mock settings with ClickHouse override.
 * Uses connection config from global-setup testcontainers.
 */
const testSettings: SettingsConfig = createTestClickHouseSettings();

/**
 * Settings layer for tests.
 */
const TestSettingsLayer = Layer.succeed(Settings, testSettings);

/**
 * ClickHouse layer for tests.
 * Note: Layer may fail with SqlError during initialization.
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
