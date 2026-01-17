import { describe, it, expect } from "@/tests/clickhouse";
import { Effect, Layer } from "effect";
import { ClickHouse } from "@/clickhouse/client";
import { type ClickHouseConfig } from "@/settings";
import { ClickHouseError } from "@/errors";

describe("ClickHouse", () => {
  describe("ClickHouse.Default", () => {
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
        // Error message contains the original ClickHouse error
        expect(error.message).toContain("non_existent_table_xyz_123");
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

  describe("ClickHouse.layer", () => {
    it("creates a layer with provided configuration", () => {
      const config: ClickHouseConfig = {
        url: "http://localhost:8123",
        user: "default",
        password: "test",
        database: "test_db",
        tls: {
          enabled: false,
          ca: "",
          skipVerify: false,
          hostnameVerify: true,
          minVersion: "1.2",
        },
      };
      const layer = ClickHouse.layer(config);

      expect(layer).toBeDefined();
      expect(Layer.isLayer(layer)).toBe(true);
    });

    it.effect("layer works with unsafeQuery", () =>
      Effect.gen(function* () {
        // Uses the test settings from tests/clickhouse.ts which provides ClickHouse layer
        const client = yield* ClickHouse;
        const result = yield* client.unsafeQuery<{ n: number }>(
          "SELECT 1 as n",
        );

        expect(result).toHaveLength(1);
        expect(result[0]?.n).toBe(1);
      }),
    );
  });

  describe("ClickHouse.Default with Settings", () => {
    it.effect("creates layer from Settings service", () =>
      Effect.gen(function* () {
        // Uses the test settings from tests/clickhouse.ts which provides ClickHouse layer
        const client = yield* ClickHouse;
        const result = yield* client.unsafeQuery<{ n: number }>(
          "SELECT 1 as n",
        );

        expect(result).toHaveLength(1);
        expect(result[0]?.n).toBe(1);
      }),
    );
  });
});
