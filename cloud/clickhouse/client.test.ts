import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { Effect, Layer } from "effect";
import {
  ClickHouseClient,
  ClickHouseClientNodeLive,
  ClickHouseClientWorkersLive,
} from "@/clickhouse/client";
import { SettingsService, type Settings } from "@/settings";
import { ClickHouseError } from "@/errors";

// Mock @clickhouse/client module
vi.mock("@clickhouse/client", () => ({
  createClient: vi.fn(() => ({
    query: vi.fn(),
    insert: vi.fn(),
    command: vi.fn(),
  })),
}));

// Mock fs module
vi.mock("node:fs", () => ({
  default: {
    readFileSync: vi.fn(),
  },
}));

// Helper to create a proper fetch mock
const createFetchMock = (response: Response) => {
  const mockFn = vi.fn().mockResolvedValue(response) as unknown as typeof fetch;
  return mockFn;
};

const createTestSettings = (overrides: Partial<Settings> = {}): Settings => ({
  env: "local",
  CLICKHOUSE_URL: "http://localhost:8123",
  CLICKHOUSE_USER: "default",
  CLICKHOUSE_PASSWORD: "clickhouse",
  CLICKHOUSE_DATABASE: "mirascope_analytics",
  CLICKHOUSE_TLS_ENABLED: false,
  CLICKHOUSE_TLS_HOSTNAME_VERIFY: true,
  ...overrides,
});

const makeTestSettingsLayer = (settings: Settings) =>
  Layer.succeed(SettingsService, settings);

describe("ClickHouseClient", () => {
  describe("ClickHouseClientNodeLive", () => {
    beforeEach(() => {
      vi.clearAllMocks();
    });

    it("creates a Layer successfully", async () => {
      const { createClient } = await import("@clickhouse/client");
      const mockClient = {
        query: vi.fn().mockResolvedValue({
          json: vi.fn().mockResolvedValue([{ id: "1" }, { id: "2" }]),
        }),
        insert: vi.fn().mockResolvedValue(undefined),
        command: vi.fn().mockResolvedValue(undefined),
      };
      vi.mocked(createClient).mockReturnValue(mockClient as never);

      const settings = createTestSettings();
      const testLayer = ClickHouseClientNodeLive.pipe(
        Layer.provide(makeTestSettingsLayer(settings))
      );

      const program = Effect.gen(function* () {
        const client = yield* ClickHouseClient;
        return client;
      });

      const result = await Effect.runPromise(
        program.pipe(Effect.provide(testLayer))
      );

      expect(result).toBeDefined();
      expect(result.query).toBeDefined();
      expect(result.insert).toBeDefined();
      expect(result.command).toBeDefined();
    });

    it("executes query successfully", async () => {
      const { createClient } = await import("@clickhouse/client");
      const mockRows = [{ id: "1", name: "test1" }, { id: "2", name: "test2" }];
      const mockClient = {
        query: vi.fn().mockResolvedValue({
          json: vi.fn().mockResolvedValue(mockRows),
        }),
        insert: vi.fn(),
        command: vi.fn(),
      };
      vi.mocked(createClient).mockReturnValue(mockClient as never);

      const settings = createTestSettings();
      const testLayer = ClickHouseClientNodeLive.pipe(
        Layer.provide(makeTestSettingsLayer(settings))
      );

      const program = Effect.gen(function* () {
        const client = yield* ClickHouseClient;
        return yield* client.query<{ id: string; name: string }>(
          "SELECT * FROM test"
        );
      });

      const result = await Effect.runPromise(
        program.pipe(Effect.provide(testLayer))
      );

      expect(result).toEqual(mockRows);
      expect(mockClient.query).toHaveBeenCalledWith({
        query: "SELECT * FROM test",
        query_params: undefined,
        format: "JSONEachRow",
      });
    });

    it("handles query errors", async () => {
      const { createClient } = await import("@clickhouse/client");
      const mockClient = {
        query: vi.fn().mockRejectedValue(new Error("Query failed")),
        insert: vi.fn(),
        command: vi.fn(),
      };
      vi.mocked(createClient).mockReturnValue(mockClient as never);

      const settings = createTestSettings();
      const testLayer = ClickHouseClientNodeLive.pipe(
        Layer.provide(makeTestSettingsLayer(settings))
      );

      const program = Effect.gen(function* () {
        const client = yield* ClickHouseClient;
        return yield* client.query("SELECT * FROM test");
      });

      const result = await Effect.runPromise(
        program.pipe(
          Effect.provide(testLayer),
          Effect.either
        )
      );

      expect(result._tag).toBe("Left");
      if (result._tag === "Left") {
        expect(result.left).toBeInstanceOf(ClickHouseError);
        expect(result.left.message).toContain("Query failed");
      }
    });

    it("inserts rows successfully", async () => {
      const { createClient } = await import("@clickhouse/client");
      const mockClient = {
        query: vi.fn(),
        insert: vi.fn().mockResolvedValue(undefined),
        command: vi.fn(),
      };
      vi.mocked(createClient).mockReturnValue(mockClient as never);

      const settings = createTestSettings();
      const testLayer = ClickHouseClientNodeLive.pipe(
        Layer.provide(makeTestSettingsLayer(settings))
      );

      const rows = [
        { id: "1", name: "test1" },
        { id: "2", name: "test2" },
      ];

      const program = Effect.gen(function* () {
        const client = yield* ClickHouseClient;
        return yield* client.insert("test_table", rows);
      });

      await Effect.runPromise(program.pipe(Effect.provide(testLayer)));

      expect(mockClient.insert).toHaveBeenCalledWith({
        table: "test_table",
        values: rows,
        format: "JSONEachRow",
      });
    });

    it("skips insert for empty rows", async () => {
      const { createClient } = await import("@clickhouse/client");
      const mockClient = {
        query: vi.fn(),
        insert: vi.fn().mockResolvedValue(undefined),
        command: vi.fn(),
      };
      vi.mocked(createClient).mockReturnValue(mockClient as never);

      const settings = createTestSettings();
      const testLayer = ClickHouseClientNodeLive.pipe(
        Layer.provide(makeTestSettingsLayer(settings))
      );

      const program = Effect.gen(function* () {
        const client = yield* ClickHouseClient;
        return yield* client.insert("test_table", []);
      });

      await Effect.runPromise(program.pipe(Effect.provide(testLayer)));

      expect(mockClient.insert).not.toHaveBeenCalled();
    });

    it("executes command successfully", async () => {
      const { createClient } = await import("@clickhouse/client");
      const mockClient = {
        query: vi.fn(),
        insert: vi.fn(),
        command: vi.fn().mockResolvedValue(undefined),
      };
      vi.mocked(createClient).mockReturnValue(mockClient as never);

      const settings = createTestSettings();
      const testLayer = ClickHouseClientNodeLive.pipe(
        Layer.provide(makeTestSettingsLayer(settings))
      );

      const program = Effect.gen(function* () {
        const client = yield* ClickHouseClient;
        return yield* client.command("CREATE TABLE test (id String)");
      });

      await Effect.runPromise(program.pipe(Effect.provide(testLayer)));

      expect(mockClient.command).toHaveBeenCalledWith({
        query: "CREATE TABLE test (id String)",
      });
    });
  });

  describe("ClickHouseClientWorkersLive", () => {
    const originalFetch = globalThis.fetch;

    beforeEach(() => {
      vi.clearAllMocks();
    });

    afterEach(() => {
      globalThis.fetch = originalFetch;
    });

    it("executes query via HTTP API", async () => {
      const mockResponse = '{"id":"1"}\n{"id":"2"}';
      globalThis.fetch = createFetchMock(
        new Response(mockResponse, { status: 200 })
      );

      const settings = createTestSettings();
      const testLayer = ClickHouseClientWorkersLive.pipe(
        Layer.provide(makeTestSettingsLayer(settings))
      );

      const program = Effect.gen(function* () {
        const client = yield* ClickHouseClient;
        return yield* client.query<{ id: string }>("SELECT * FROM test");
      });

      const result = await Effect.runPromise(
        program.pipe(Effect.provide(testLayer))
      );

      expect(result).toEqual([{ id: "1" }, { id: "2" }]);
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining("default_format=JSONEachRow"),
        expect.objectContaining({ method: "POST" })
      );
    });

    it("handles empty response", async () => {
      globalThis.fetch = createFetchMock(
        new Response("", { status: 200 })
      );

      const settings = createTestSettings();
      const testLayer = ClickHouseClientWorkersLive.pipe(
        Layer.provide(makeTestSettingsLayer(settings))
      );

      const program = Effect.gen(function* () {
        const client = yield* ClickHouseClient;
        return yield* client.query<{ id: string }>("SELECT * FROM test");
      });

      const result = await Effect.runPromise(
        program.pipe(Effect.provide(testLayer))
      );

      expect(result).toEqual([]);
    });

    it("handles HTTP errors from ClickHouse", async () => {
      globalThis.fetch = createFetchMock(
        new Response("Code: 60. DB::Exception", { status: 500 })
      );

      const settings = createTestSettings();
      const testLayer = ClickHouseClientWorkersLive.pipe(
        Layer.provide(makeTestSettingsLayer(settings))
      );

      const program = Effect.gen(function* () {
        const client = yield* ClickHouseClient;
        return yield* client.query("SELECT * FROM test");
      });

      const result = await Effect.runPromise(
        program.pipe(
          Effect.provide(testLayer),
          Effect.either
        )
      );

      expect(result._tag).toBe("Left");
      if (result._tag === "Left") {
        expect(result.left).toBeInstanceOf(ClickHouseError);
        expect(result.left.message).toContain("500");
      }
    });

    it("validates https in production", async () => {
      const settings = createTestSettings({
        env: "production",
        CLICKHOUSE_URL: "http://clickhouse.example.com", // HTTP instead of HTTPS
      });
      const testLayer = ClickHouseClientWorkersLive.pipe(
        Layer.provide(makeTestSettingsLayer(settings))
      );

      const program = Effect.gen(function* () {
        yield* ClickHouseClient;
      });

      await expect(
        Effect.runPromise(program.pipe(Effect.provide(testLayer)))
      ).rejects.toThrow("must use https://");
    });

    it("inserts rows via HTTP API", async () => {
      globalThis.fetch = createFetchMock(
        new Response("", { status: 200 })
      );

      const settings = createTestSettings();
      const testLayer = ClickHouseClientWorkersLive.pipe(
        Layer.provide(makeTestSettingsLayer(settings))
      );

      const rows = [{ id: "1" }, { id: "2" }];

      const program = Effect.gen(function* () {
        const client = yield* ClickHouseClient;
        return yield* client.insert("test_table", rows);
      });

      await Effect.runPromise(program.pipe(Effect.provide(testLayer)));

      // URL is encoded, so check for the encoded form
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining("test_table"),
        expect.objectContaining({
          method: "POST",
          body: '{"id":"1"}\n{"id":"2"}',
        })
      );
    });

    it("skips insert for empty rows (Workers)", async () => {
      globalThis.fetch = createFetchMock(new Response("", { status: 200 }));

      const settings = createTestSettings();
      const testLayer = ClickHouseClientWorkersLive.pipe(
        Layer.provide(makeTestSettingsLayer(settings))
      );

      const program = Effect.gen(function* () {
        const client = yield* ClickHouseClient;
        return yield* client.insert("test_table", []);
      });

      await Effect.runPromise(program.pipe(Effect.provide(testLayer)));

      expect(globalThis.fetch).not.toHaveBeenCalled();
    });

    it("executes command via HTTP API", async () => {
      globalThis.fetch = createFetchMock(
        new Response("", { status: 200 })
      );

      const settings = createTestSettings();
      const testLayer = ClickHouseClientWorkersLive.pipe(
        Layer.provide(makeTestSettingsLayer(settings))
      );

      const program = Effect.gen(function* () {
        const client = yield* ClickHouseClient;
        return yield* client.command("CREATE TABLE test (id String)");
      });

      await Effect.runPromise(program.pipe(Effect.provide(testLayer)));

      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining("localhost:8123"),
        expect.objectContaining({
          method: "POST",
          body: "CREATE TABLE test (id String)",
        })
      );
    });
  });
});
