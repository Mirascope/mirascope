import { describe, it, expect } from "@/tests/clickhouse";
import { Effect, Layer } from "effect";
import { ClickHouse, ClickHouseLive } from "@/db/clickhouse/client";
import { SettingsService, type Settings } from "@/settings";
import { ClickHouseError } from "@/errors";
import { vi } from "vitest";

const createTestSettings = (overrides: Partial<Settings> = {}): Settings => ({
  env: "local",
  CLICKHOUSE_URL: process.env.CLICKHOUSE_URL ?? "http://localhost:8123",
  CLICKHOUSE_USER: process.env.CLICKHOUSE_USER ?? "default",
  CLICKHOUSE_PASSWORD: process.env.CLICKHOUSE_PASSWORD ?? "clickhouse",
  CLICKHOUSE_DATABASE: process.env.CLICKHOUSE_DATABASE ?? "mirascope_analytics",
  CLICKHOUSE_TLS_ENABLED: false,
  CLICKHOUSE_TLS_HOSTNAME_VERIFY: true,
  ...overrides,
});

const makeTestSettingsLayer = (settings: Settings) =>
  Layer.succeed(SettingsService, settings);

const createClickHouseLayer = (settings: Settings) =>
  ClickHouseLive.pipe(Layer.provide(makeTestSettingsLayer(settings)));

describe("ClickHouse", () => {
  describe("ClickHouseLive", () => {
    it.effect("creates a Layer successfully", () =>
      Effect.gen(function* () {
        const client = yield* ClickHouse;
        expect(client).toBeDefined();
        expect(client.unsafeQuery).toBeDefined();
        expect(client.insert).toBeDefined();
        expect(client.command).toBeDefined();
      }),
    );

    it.effect("executes unsafeQuery successfully", () =>
      Effect.gen(function* () {
        const client = yield* ClickHouse;

        const result = yield* client.unsafeQuery<{ n: number }>(
          "SELECT 1 as n",
        );

        expect(result).toHaveLength(1);
        expect(result[0]?.n).toBe(1);
      }),
    );

    it.effect("handles unsafeQuery errors with ClickHouseError", () =>
      Effect.gen(function* () {
        const client = yield* ClickHouse;

        const error = yield* client
          .unsafeQuery("SELECT * FROM non_existent_table_xyz_123")
          .pipe(Effect.flip);

        expect(error).toBeInstanceOf(ClickHouseError);
        expect(error.message).toContain("ClickHouse operation failed");
      }),
    );

    it.effect("executes command successfully", () =>
      Effect.gen(function* () {
        const client = yield* ClickHouse;
        yield* client.command("SELECT 1");
      }),
    );

    it.effect("skips insert for empty rows", () =>
      Effect.gen(function* () {
        const client = yield* ClickHouse;
        yield* client.insert("any_table", []);
      }),
    );
  });

  describe("TLS configuration validation", () => {
    it("throws error when TLS_SKIP_VERIFY is true", async () => {
      const settings = createTestSettings({
        CLICKHOUSE_TLS_ENABLED: true,
        CLICKHOUSE_TLS_SKIP_VERIFY: true,
      });

      const program = Effect.gen(function* () {
        yield* ClickHouse;
      });

      await expect(
        Effect.runPromise(
          program.pipe(Effect.provide(createClickHouseLayer(settings))),
        ),
      ).rejects.toThrow("CLICKHOUSE_TLS_SKIP_VERIFY=true is not supported");
    });

    it("throws error when TLS_HOSTNAME_VERIFY is false", async () => {
      const settings = createTestSettings({
        CLICKHOUSE_TLS_ENABLED: true,
        CLICKHOUSE_TLS_HOSTNAME_VERIFY: false,
      });

      const program = Effect.gen(function* () {
        yield* ClickHouse;
      });

      await expect(
        Effect.runPromise(
          program.pipe(Effect.provide(createClickHouseLayer(settings))),
        ),
      ).rejects.toThrow(
        "CLICKHOUSE_TLS_HOSTNAME_VERIFY=false is not supported",
      );
    });

    it("throws error when TLS_CA is provided", async () => {
      const settings = createTestSettings({
        CLICKHOUSE_TLS_ENABLED: true,
        CLICKHOUSE_TLS_CA: "/nonexistent/ca.pem",
      });

      const program = Effect.gen(function* () {
        yield* ClickHouse;
      });

      await expect(
        Effect.runPromise(
          program.pipe(Effect.provide(createClickHouseLayer(settings))),
        ),
      ).rejects.toThrow("CLICKHOUSE_TLS_CA is not supported");
    });

    it("logs warning when TLS_MIN_VERSION is non-default", async () => {
      const consoleSpy = vi.spyOn(console, "warn").mockImplementation(() => {});

      const settings = createTestSettings({
        CLICKHOUSE_TLS_ENABLED: true,
        CLICKHOUSE_TLS_MIN_VERSION: "TLSv1.3",
      });

      const program = Effect.gen(function* () {
        yield* ClickHouse;
      });

      await expect(
        Effect.runPromise(
          program.pipe(Effect.provide(createClickHouseLayer(settings))),
        ),
      ).rejects.toThrow();

      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining("CLICKHOUSE_TLS_MIN_VERSION=TLSv1.3"),
      );

      consoleSpy.mockRestore();
    });
  });

  describe("ClickHouse.layer", () => {
    it("creates a layer with provided configuration", () => {
      const layer = ClickHouse.layer({
        url: "http://localhost:8123",
        user: "default",
        password: "test",
        database: "test_db",
      });

      expect(layer).toBeDefined();
      expect(Layer.isLayer(layer)).toBe(true);
    });

    it("layer works with unsafeQuery", async () => {
      const program = Effect.gen(function* () {
        const client = yield* ClickHouse;
        return yield* client.unsafeQuery<{ n: number }>("SELECT 1 as n");
      });

      const result = await Effect.runPromise(
        program.pipe(
          Effect.provide(
            ClickHouse.layer({
              url: process.env.CLICKHOUSE_URL ?? "http://localhost:8123",
              user: process.env.CLICKHOUSE_USER ?? "default",
              password: process.env.CLICKHOUSE_PASSWORD ?? "clickhouse",
              database:
                process.env.CLICKHOUSE_DATABASE ?? "mirascope_analytics",
            }),
          ),
        ),
      );

      expect(result).toHaveLength(1);
      expect(result[0]?.n).toBe(1);
    });
  });

  describe("ClickHouseLive in production", () => {
    it("validates https in production", async () => {
      const settings = createTestSettings({
        env: "production",
        CLICKHOUSE_URL: "http://clickhouse.example.com",
      });

      const program = Effect.gen(function* () {
        yield* ClickHouse;
      });

      await expect(
        Effect.runPromise(
          program.pipe(Effect.provide(createClickHouseLayer(settings))),
        ),
      ).rejects.toThrow("must use https://");
    });
  });
});
