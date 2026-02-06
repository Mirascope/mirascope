import { Effect, Layer } from "effect";

import type { PublicUser } from "@/db/schema";

import { Analytics } from "@/analytics";
import { handleRequest } from "@/api/handler";
import { ClickHouse } from "@/db/clickhouse/client";
import { ClickHouseSearch } from "@/db/clickhouse/search";
import { DrizzleORM } from "@/db/client";
import { Emails } from "@/emails";
import { HandlerError } from "@/errors";
import { Settings, type SettingsConfig } from "@/settings";
import { describe, it, expect } from "@/tests/api";
import { getTestClickHouseConfig } from "@/tests/global-setup";
import { MockDrizzleORMLayer } from "@/tests/mock-drizzle";
import { createMockSettings } from "@/tests/settings";
import { RealtimeSpans } from "@/workers/realtimeSpans";
import { SpansIngestQueue } from "@/workers/spanIngestQueue";

const mockUser: PublicUser = {
  id: "test-user-id",
  email: "test@example.com",
  name: "Test User",
  accountType: "user",
  deletedAt: null,
};

const clickhouseConfig = getTestClickHouseConfig();
const settings: SettingsConfig = createMockSettings({
  env: "test",
  clickhouse: {
    url: clickhouseConfig.url,
    user: clickhouseConfig.user,
    password: clickhouseConfig.password,
    database: clickhouseConfig.database,
    tls: {
      enabled: false,
      ca: "",
      skipVerify: false,
      hostnameVerify: true,
      minVersion: "1.2",
    },
  },
});
const SettingsLayer = Layer.succeed(Settings, settings);
const ClickHouseSearchLayer = ClickHouseSearch.Default.pipe(
  Layer.provide(ClickHouse.Default),
  Layer.provide(SettingsLayer),
);
const MockSpansIngestQueue = Layer.succeed(SpansIngestQueue, {
  send: () => Effect.void,
});
const MockRealtimeSpans = Layer.succeed(RealtimeSpans, {
  upsert: () => Effect.void,
  search: () => Effect.succeed({ spans: [], total: 0, hasMore: false }),
  getTraceDetail: () =>
    Effect.succeed({
      traceId: "",
      spans: [],
      rootSpanId: null,
      totalDurationMs: null,
    }),
  exists: () => Effect.succeed(false),
});
const MockAnalytics = Layer.succeed(Analytics, {
  googleAnalytics: null as never,
  postHog: null as never,
  trackEvent: () => Effect.void,
  trackPageView: () => Effect.void,
  identify: () => Effect.void,
  initialize: () => Effect.void,
});
const MockEmails = Layer.succeed(Emails, {
  send: () => Effect.succeed({ id: "mock-email-id" }),
  audience: { add: () => Effect.succeed({ id: "mock-contact-id" }) },
});

/**
 * Combined mock layer for all app services used in handler tests.
 */
const MockAppServicesLayer = Layer.mergeAll(
  MockDrizzleORMLayer,
  ClickHouseSearchLayer,
  MockSpansIngestQueue,
  MockRealtimeSpans,
  MockAnalytics,
  MockEmails,
);

describe("handleRequest", () => {
  it.effect("should return 404 for unknown route", () =>
    Effect.gen(function* () {
      const clickHouseSearch = yield* ClickHouseSearch;
      const req = new Request(
        "http://localhost/api/v2/this-route-does-not-exist",
        { method: "GET" },
      );

      const { matched, response } = yield* handleRequest(req, {
        user: mockUser,
        settings,
        prefix: "/api/v2",
        drizzle: yield* DrizzleORM,
        analytics: yield* Analytics,
        emails: yield* Emails,
        clickHouseSearch,
        realtimeSpans: yield* RealtimeSpans,
        spansIngestQueue: yield* SpansIngestQueue,
      });

      expect(response.status).toBe(404);
      expect(matched).toBe(false);
    }).pipe(Effect.provide(MockAppServicesLayer)),
  );

  it.effect("should return 404 for non-existing routes", () =>
    Effect.gen(function* () {
      const clickHouseSearch = yield* ClickHouseSearch;
      const req = new Request(
        "http://localhost/api/v2/this-route-does-not-exist",
        { method: "GET" },
      );

      const { matched, response } = yield* handleRequest(req, {
        user: mockUser,
        settings,
        prefix: "/api/v2",
        drizzle: yield* DrizzleORM,
        analytics: yield* Analytics,
        emails: yield* Emails,
        clickHouseSearch,
        realtimeSpans: yield* RealtimeSpans,
        spansIngestQueue: yield* SpansIngestQueue,
      });

      expect(response.status).toBe(404);
      expect(matched).toBe(false);
    }).pipe(Effect.provide(MockAppServicesLayer)),
  );

  it.effect(
    "should return 404 when pathname exactly matches prefix (no route)",
    () =>
      Effect.gen(function* () {
        const clickHouseSearch = yield* ClickHouseSearch;
        const req = new Request("http://localhost/api/v2", { method: "GET" });

        const { matched, response } = yield* handleRequest(req, {
          user: mockUser,
          settings,
          prefix: "/api/v2",
          drizzle: yield* DrizzleORM,
          analytics: yield* Analytics,
          emails: yield* Emails,
          clickHouseSearch,
          realtimeSpans: yield* RealtimeSpans,
          spansIngestQueue: yield* SpansIngestQueue,
        });

        // The path becomes "/" after stripping prefix, which doesn't match any route
        expect(response.status).toBe(404);
        expect(matched).toBe(false);
      }).pipe(Effect.provide(MockAppServicesLayer)),
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
          settings,
          drizzle: yield* DrizzleORM,
          analytics: yield* Analytics,
          emails: yield* Emails,
          clickHouseSearch,
          realtimeSpans: yield* RealtimeSpans,
          spansIngestQueue: yield* SpansIngestQueue,
        }).pipe(Effect.flip);

        expect(error).toBeInstanceOf(HandlerError);
        expect(error.message).toContain(
          "[Effect API] Error handling request: boom",
        );
      }).pipe(Effect.provide(MockAppServicesLayer)),
  );

  it.effect("should handle POST requests with body", () =>
    Effect.gen(function* () {
      const clickHouseSearch = yield* ClickHouseSearch;
      // POST request with body to trigger duplex: "half"
      const req = new Request(
        "http://localhost/api/v2/organizations/00000000-0000-0000-0000-000000000099/projects",
        {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ name: "Test", slug: "test" }),
        },
      );

      const { matched, response } = yield* handleRequest(req, {
        user: mockUser,
        settings,
        prefix: "/api/v2",
        drizzle: yield* DrizzleORM,
        analytics: yield* Analytics,
        emails: yield* Emails,
        clickHouseSearch,
        realtimeSpans: yield* RealtimeSpans,
        spansIngestQueue: yield* SpansIngestQueue,
      });

      expect(matched).toBe(true);
      expect(response.status).toBeGreaterThanOrEqual(400);
    }).pipe(Effect.provide(MockAppServicesLayer)),
  );

  it.effect("should transform _tag in JSON error responses", () =>
    Effect.gen(function* () {
      const clickHouseSearch = yield* ClickHouseSearch;
      // Trigger a NotFoundError by trying to get a non-existent organization
      const req = new Request(
        "http://localhost/api/v2/organizations/00000000-0000-0000-0000-000000000099",
        {
          method: "GET",
        },
      );

      const { matched, response } = yield* handleRequest(req, {
        user: mockUser,
        settings,
        prefix: "/api/v2",
        drizzle: yield* DrizzleORM,
        analytics: yield* Analytics,
        emails: yield* Emails,
        clickHouseSearch,
        realtimeSpans: yield* RealtimeSpans,
        spansIngestQueue: yield* SpansIngestQueue,
      });

      const body = yield* Effect.promise(() => response.text());

      expect(matched).toBe(true);
      expect(response.status).toBeGreaterThanOrEqual(400);
      // Ensure _tag is transformed to tag in error responses
      expect(body).toContain('"tag"');
      expect(body).not.toContain('"_tag"');
    }).pipe(Effect.provide(MockAppServicesLayer)),
  );
});
