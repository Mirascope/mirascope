import { Effect, Layer } from "effect";
import { describe, it, expect } from "@/tests/api";
import { handleRequest } from "@/api/handler";
import type { PublicUser } from "@/db/schema";
import { HandlerError } from "@/errors";
import { ClickHouse } from "@/db/clickhouse/client";
import { ClickHouseSearch } from "@/db/clickhouse/search";
import { SettingsService, getSettings } from "@/settings";
import { SpansMeteringQueueService } from "@/workers/spansMeteringQueue";
import { CLICKHOUSE_CONNECTION_FILE } from "@/tests/global-setup";
import fs from "fs";

const mockUser: PublicUser = {
  id: "test-user-id",
  email: "test@example.com",
  name: "Test User",
  deletedAt: null,
};

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
const settings = getSettings();
const settingsLayer = Layer.succeed(SettingsService, {
  ...settings,
  env: "test",
  CLICKHOUSE_URL: clickhouseConfig.url,
  CLICKHOUSE_USER: clickhouseConfig.user,
  CLICKHOUSE_PASSWORD: clickhouseConfig.password,
  CLICKHOUSE_DATABASE: clickhouseConfig.database,
});
const clickHouseSearchLayer = ClickHouseSearch.Default.pipe(
  Layer.provide(ClickHouse.Default),
  Layer.provide(settingsLayer),
);

const mockSpansMeteringQueueLayer = Layer.succeed(SpansMeteringQueueService, {
  send: () => Effect.void,
});

const testLayer = Layer.mergeAll(
  clickHouseSearchLayer,
  mockSpansMeteringQueueLayer,
);

describe("handleRequest", () => {
  it.effect("should return 404 for non-existing routes", () =>
    Effect.gen(function* () {
      const clickHouseSearch = yield* ClickHouseSearch;
      const req = new Request(
        "http://localhost/api/v0/this-route-does-not-exist",
        { method: "GET" },
      );

      const { matched, response } = yield* handleRequest(req, {
        user: mockUser,
        environment: "test",
        prefix: "/api/v0",
        clickHouseSearch,
      });

      expect(response.status).toBe(404);
      expect(matched).toBe(false);
    }).pipe(Effect.provide(testLayer)),
  );

  it.effect(
    "should return 404 when pathname exactly matches prefix (no route)",
    () =>
      Effect.gen(function* () {
        const clickHouseSearch = yield* ClickHouseSearch;
        const req = new Request("http://localhost/api/v0", { method: "GET" });

        const { matched, response } = yield* handleRequest(req, {
          user: mockUser,
          environment: "test",
          prefix: "/api/v0",
          clickHouseSearch,
        });

        // The path becomes "/" after stripping prefix, which doesn't match any route
        expect(response.status).toBe(404);
        expect(matched).toBe(false);
      }).pipe(Effect.provide(testLayer)),
  );

  it.effect(
    "should return error for a request that triggers an exception",
    () =>
      Effect.gen(function* () {
        const clickHouseSearch = yield* ClickHouseSearch;
        const faultyRequest = new Proxy(
          {},
          {
            get() {
              throw new Error("boom");
            },
          },
        ) as Request;

        const error = yield* handleRequest(faultyRequest, {
          user: mockUser,
          environment: "test",
          clickHouseSearch,
        }).pipe(Effect.flip);

        expect(error).toBeInstanceOf(HandlerError);
        expect(error.message).toContain(
          "[Effect API] Error handling request: boom",
        );
      }).pipe(Effect.provide(testLayer)),
  );

  it.effect("should handle POST requests with body", () =>
    Effect.gen(function* () {
      const clickHouseSearch = yield* ClickHouseSearch;
      // POST request with body to trigger duplex: "half"
      const req = new Request(
        "http://localhost/api/v0/organizations/00000000-0000-0000-0000-000000000099/projects",
        {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ name: "Test", slug: "test" }),
        },
      );

      const { matched, response } = yield* handleRequest(req, {
        user: mockUser,
        environment: "test",
        prefix: "/api/v0",
        clickHouseSearch,
      });

      expect(matched).toBe(true);
      expect(response.status).toBeGreaterThanOrEqual(400);
    }).pipe(Effect.provide(testLayer)),
  );

  it.effect("should transform _tag in JSON error responses", () =>
    Effect.gen(function* () {
      const clickHouseSearch = yield* ClickHouseSearch;
      // Trigger a NotFoundError by trying to get a non-existent organization
      const req = new Request(
        "http://localhost/api/v0/organizations/00000000-0000-0000-0000-000000000099",
        {
          method: "GET",
        },
      );

      const { matched, response } = yield* handleRequest(req, {
        user: mockUser,
        environment: "test",
        prefix: "/api/v0",
        clickHouseSearch,
      });

      const body = yield* Effect.promise(() => response.text());

      expect(matched).toBe(true);
      expect(response.status).toBeGreaterThanOrEqual(400);
      // Ensure _tag is transformed to tag in error responses
      expect(body).toContain('"tag"');
      expect(body).not.toContain('"_tag"');
    }).pipe(Effect.provide(testLayer)),
  );
});
