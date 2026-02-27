import { describe, it, expect } from "@effect/vitest";
import { Effect, Either } from "effect";
import { vi, beforeEach, afterEach, assert } from "vitest";

import { SettingsValidationError } from "@/errors";
import {
  validateSettings,
  validateSettingsFromEnvironment,
  type CloudflareEnvironment,
} from "@/settings";
import { createMockEnv } from "@/tests/settings";

describe("settings", () => {
  describe("validateSettings", () => {
    const originalEnv = process.env;

    beforeEach(() => {
      vi.resetModules();
      process.env = { ...originalEnv };
    });

    afterEach(() => {
      process.env = originalEnv;
    });

    it.effect(
      "fails with SettingsValidationError when required variables are missing",
      () => {
        // Clear all env vars
        process.env = {};

        return Effect.gen(function* () {
          const result = yield* validateSettings().pipe(Effect.either);
          assert(Either.isLeft(result));
          expect(result.left).toBeInstanceOf(SettingsValidationError);
          expect(result.left.missingVariables).toContain("ENVIRONMENT");
          expect(result.left.missingVariables).toContain("DATABASE_URL");
        });
      },
    );

    it.effect("succeeds with all required variables set", () => {
      // Set all required env vars
      const mockEnv = createMockEnv();
      for (const [key, value] of Object.entries(mockEnv)) {
        process.env[key] = value;
      }

      return Effect.gen(function* () {
        const result = yield* validateSettings().pipe(Effect.either);
        assert(Either.isRight(result));
        expect(result.right.env).toBe("test");
        expect(result.right.databaseUrl).toBe(
          "postgres://test:test@localhost:5432/test",
        );
      });
    });

    it.effect("parses boolean TLS settings correctly", () => {
      const mockEnv = createMockEnv({
        CLICKHOUSE_TLS_ENABLED: "false",
        CLICKHOUSE_TLS_SKIP_VERIFY: "false",
        CLICKHOUSE_TLS_HOSTNAME_VERIFY: "true",
      });
      for (const [key, value] of Object.entries(mockEnv)) {
        process.env[key] = value;
      }

      return Effect.gen(function* () {
        const result = yield* validateSettings().pipe(Effect.either);
        assert(Either.isRight(result));
        expect(result.right.clickhouse.tls.enabled).toBe(false);
        expect(result.right.clickhouse.tls.skipVerify).toBe(false);
        expect(result.right.clickhouse.tls.hostnameVerify).toBe(true);
      });
    });

    it.effect("fails in production when CLICKHOUSE_URL is not https", () => {
      const mockEnv = createMockEnv({
        ENVIRONMENT: "production",
        CLICKHOUSE_URL: "http://clickhouse.example.com",
        CLICKHOUSE_TLS_ENABLED: "true",
        CLICKHOUSE_TLS_SKIP_VERIFY: "false",
        CLICKHOUSE_TLS_HOSTNAME_VERIFY: "true",
        CLICKHOUSE_TLS_CA: "", // Must be empty - CA not supported by web client
        CLICKHOUSE_TLS_MIN_VERSION: "1.2",
      });
      for (const [key, value] of Object.entries(mockEnv)) {
        process.env[key] = value;
      }

      return Effect.gen(function* () {
        const result = yield* validateSettings().pipe(Effect.either);
        assert(Either.isLeft(result));
        expect(result.left).toBeInstanceOf(SettingsValidationError);
        expect(result.left.message).toContain("must use https://");
      });
    });

    it.effect(
      "fails when TLS_SKIP_VERIFY is true (not supported by web client)",
      () => {
        const mockEnv = createMockEnv({
          CLICKHOUSE_TLS_ENABLED: "true",
          CLICKHOUSE_TLS_SKIP_VERIFY: "true",
          CLICKHOUSE_TLS_HOSTNAME_VERIFY: "true",
          CLICKHOUSE_TLS_CA: "", // Must be empty - CA not supported by web client
          CLICKHOUSE_TLS_MIN_VERSION: "1.2",
        });
        for (const [key, value] of Object.entries(mockEnv)) {
          process.env[key] = value;
        }

        return Effect.gen(function* () {
          const result = yield* validateSettings().pipe(Effect.either);
          assert(Either.isLeft(result));
          expect(result.left).toBeInstanceOf(SettingsValidationError);
          expect(result.left.message).toContain(
            "CLICKHOUSE_TLS_SKIP_VERIFY=true",
          );
        });
      },
    );

    it.effect(
      "fails when TLS_HOSTNAME_VERIFY is false (not supported by web client)",
      () => {
        const mockEnv = createMockEnv({
          CLICKHOUSE_TLS_ENABLED: "true",
          CLICKHOUSE_TLS_SKIP_VERIFY: "false",
          CLICKHOUSE_TLS_HOSTNAME_VERIFY: "false",
          CLICKHOUSE_TLS_CA: "", // Must be empty - CA not supported by web client
          CLICKHOUSE_TLS_MIN_VERSION: "1.2",
        });
        for (const [key, value] of Object.entries(mockEnv)) {
          process.env[key] = value;
        }

        return Effect.gen(function* () {
          const result = yield* validateSettings().pipe(Effect.either);
          assert(Either.isLeft(result));
          expect(result.left).toBeInstanceOf(SettingsValidationError);
          expect(result.left.message).toContain(
            "CLICKHOUSE_TLS_HOSTNAME_VERIFY=false",
          );
        });
      },
    );
  });

  describe("validateSettingsFromEnvironment", () => {
    it.effect("fails when HYPERDRIVE binding is missing", () => {
      const env: CloudflareEnvironment = {};

      return Effect.gen(function* () {
        const result = yield* validateSettingsFromEnvironment(env).pipe(
          Effect.either,
        );
        assert(Either.isLeft(result));
        expect(result.left).toBeInstanceOf(SettingsValidationError);
        expect(result.left.missingVariables).toContain("HYPERDRIVE");
        expect(result.left.message).toContain(
          "HYPERDRIVE binding not configured",
        );
      });
    });

    it.effect(
      "fails when required env vars are missing (after HYPERDRIVE)",
      () => {
        const env: CloudflareEnvironment = {
          HYPERDRIVE: {
            connectionString: "postgres://test:test@localhost:5432/test",
          },
        };

        return Effect.gen(function* () {
          const result = yield* validateSettingsFromEnvironment(env).pipe(
            Effect.either,
          );
          assert(Either.isLeft(result));
          expect(result.left).toBeInstanceOf(SettingsValidationError);
          expect(result.left.missingVariables).toContain("ENVIRONMENT");
        });
      },
    );

    it.effect("succeeds with all required env bindings", () => {
      const env: CloudflareEnvironment = {
        ...createMockEnv(),
        HYPERDRIVE: {
          connectionString: "postgres://test:test@localhost:5432/test",
        },
      };

      return Effect.gen(function* () {
        const result = yield* validateSettingsFromEnvironment(env).pipe(
          Effect.either,
        );
        assert(Either.isRight(result));
        expect(result.right.env).toBe("test");
        expect(result.right.clickhouse.url).toBe("http://localhost:8123");
        expect(result.right.clickhouse.user).toBe("default");
        expect(result.right.clickhouse.database).toBe("test_db");
      });
    });

    it.effect("maps all ClickHouse settings from env", () => {
      const env: CloudflareEnvironment = {
        ...createMockEnv(),
        HYPERDRIVE: {
          connectionString: "postgres://test:test@localhost:5432/test",
        },
        CLICKHOUSE_URL: "https://ch.example.com",
        CLICKHOUSE_USER: "user",
        CLICKHOUSE_PASSWORD: "pass",
        CLICKHOUSE_DATABASE: "analytics",
      };

      return Effect.gen(function* () {
        const result = yield* validateSettingsFromEnvironment(env).pipe(
          Effect.either,
        );
        assert(Either.isRight(result));
        expect(result.right.clickhouse.url).toBe("https://ch.example.com");
        expect(result.right.clickhouse.user).toBe("user");
        expect(result.right.clickhouse.password).toBe("pass");
        expect(result.right.clickhouse.database).toBe("analytics");
      });
    });

    it.effect("maps TLS settings from env", () => {
      const env: CloudflareEnvironment = {
        ...createMockEnv(),
        HYPERDRIVE: {
          connectionString: "postgres://test:test@localhost:5432/test",
        },
        CLICKHOUSE_TLS_ENABLED: "false",
        CLICKHOUSE_TLS_CA: "test-ca",
        CLICKHOUSE_TLS_SKIP_VERIFY: "false",
        CLICKHOUSE_TLS_HOSTNAME_VERIFY: "true",
        CLICKHOUSE_TLS_MIN_VERSION: "1.2",
      };

      return Effect.gen(function* () {
        const result = yield* validateSettingsFromEnvironment(env).pipe(
          Effect.either,
        );
        assert(Either.isRight(result));
        expect(result.right.clickhouse.tls.enabled).toBe(false);
        expect(result.right.clickhouse.tls.ca).toBe("test-ca");
        expect(result.right.clickhouse.tls.skipVerify).toBe(false);
        expect(result.right.clickhouse.tls.hostnameVerify).toBe(true);
      });
    });
  });
});
