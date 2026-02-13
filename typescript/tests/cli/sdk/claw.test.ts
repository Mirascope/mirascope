/**
 * @fileoverview Tests for ClawApi service against mock HTTP layer.
 */

import { describe, it, expect } from "@effect/vitest";
import { Effect, Layer, Schema } from "effect";

import { ClawApi } from "../../../src/cli/sdk/claw/service.js";
import { ApiError } from "../../../src/cli/sdk/errors.js";
import { MirascopeHttp } from "../../../src/cli/sdk/http/client.js";

// ---------------------------------------------------------------------------
// Mock HTTP helpers
// ---------------------------------------------------------------------------

type MockRoute = {
  method: string;
  path: string | RegExp;
  response: unknown;
  status?: number;
};

const matchPath = (routePath: string | RegExp, reqPath: string): boolean =>
  routePath instanceof RegExp ? routePath.test(reqPath) : routePath === reqPath;

const mockHttp = (routes: MockRoute[]): Layer.Layer<MirascopeHttp> =>
  Layer.succeed(MirascopeHttp, {
    get: (path, schema) => {
      const route = routes.find(
        (r) => r.method === "GET" && matchPath(r.path, path),
      );
      if (!route) {
        return Effect.fail(
          new ApiError({ message: `No mock for GET ${path}`, status: 404 }),
        ) as Effect.Effect<never, ApiError>;
      }
      if (route.status && route.status >= 400) {
        return Effect.fail(
          new ApiError({
            message:
              (route.response as Record<string, string>)?.message ?? "Error",
            status: route.status,
          }),
        ) as Effect.Effect<never, ApiError>;
      }
      return Schema.decodeUnknown(schema)(route.response).pipe(
        Effect.mapError(
          () => new ApiError({ message: "Schema decode failed", status: 500 }),
        ),
      ) as Effect.Effect<never, ApiError>;
    },
    post: (path, _body, schema) => {
      const route = routes.find(
        (r) => r.method === "POST" && matchPath(r.path, path),
      );
      if (!route) {
        return Effect.fail(
          new ApiError({ message: `No mock for POST ${path}`, status: 404 }),
        ) as Effect.Effect<never, ApiError>;
      }
      if (route.status && route.status >= 400) {
        return Effect.fail(
          new ApiError({
            message:
              (route.response as Record<string, string>)?.message ?? "Error",
            status: route.status,
          }),
        ) as Effect.Effect<never, ApiError>;
      }
      return Schema.decodeUnknown(schema)(route.response).pipe(
        Effect.mapError(
          () => new ApiError({ message: "Schema decode failed", status: 500 }),
        ),
      ) as Effect.Effect<never, ApiError>;
    },
    del: (path) => {
      const route = routes.find(
        (r) => r.method === "DELETE" && matchPath(r.path, path),
      );
      if (!route) {
        return Effect.fail(
          new ApiError({ message: `No mock for DELETE ${path}`, status: 404 }),
        );
      }
      if (route.status && route.status >= 400) {
        return Effect.fail(
          new ApiError({
            message:
              (route.response as Record<string, string>)?.message ?? "Error",
            status: route.status,
          }),
        );
      }
      return Effect.void;
    },
  });

// ---------------------------------------------------------------------------
// Test data
// ---------------------------------------------------------------------------

const authMeResponse = {
  user: { id: "user-1", email: "test@example.com", name: "Test" },
  apiKey: {
    id: "key-1",
    organizationId: "org-456",
    environmentId: null,
    projectId: null,
  },
};

const sampleClaw = {
  id: "claw-123",
  organizationId: "org-456",
  slug: "scouty",
  displayName: "Scouty",
  status: "active" as const,
  instanceType: "standard-1",
  createdAt: "2026-02-12T00:00:00Z",
};

const sampleClawDetail = {
  ...sampleClaw,
  lastError: null,
  lastDeployedAt: null,
};

/** Standard routes that include auth/me + claw endpoints */
const standardRoutes = (extra: MockRoute[] = []): MockRoute[] => [
  { method: "GET", path: "/v1/auth/me", response: authMeResponse },
  ...extra,
];

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("ClawApi.Live", () => {
  it.effect("list returns claws", () =>
    Effect.gen(function* () {
      const api = yield* ClawApi;
      const claws = yield* api.list();
      expect(claws).toHaveLength(1);
      expect(claws[0]!.slug).toBe("scouty");
    }).pipe(
      Effect.provide(
        ClawApi.Live.pipe(
          Layer.provide(
            mockHttp(
              standardRoutes([
                {
                  method: "GET",
                  path: /\/v2\/organizations\/org-456\/claws$/,
                  response: [sampleClaw],
                },
              ]),
            ),
          ),
        ),
      ),
    ),
  );

  it.effect("list returns empty array", () =>
    Effect.gen(function* () {
      const api = yield* ClawApi;
      const claws = yield* api.list();
      expect(claws).toHaveLength(0);
    }).pipe(
      Effect.provide(
        ClawApi.Live.pipe(
          Layer.provide(
            mockHttp(
              standardRoutes([
                {
                  method: "GET",
                  path: /\/v2\/organizations\/org-456\/claws$/,
                  response: [],
                },
              ]),
            ),
          ),
        ),
      ),
    ),
  );

  it.effect("create returns new claw", () =>
    Effect.gen(function* () {
      const api = yield* ClawApi;
      const claw = yield* api.create("", "new-claw");
      expect(claw.slug).toBe("scouty");
      expect(claw.status).toBe("active");
    }).pipe(
      Effect.provide(
        ClawApi.Live.pipe(
          Layer.provide(
            mockHttp(
              standardRoutes([
                {
                  method: "POST",
                  path: /\/v2\/organizations\/org-456\/claws$/,
                  response: sampleClaw,
                },
              ]),
            ),
          ),
        ),
      ),
    ),
  );

  it.effect("get returns claw by id", () =>
    Effect.gen(function* () {
      const api = yield* ClawApi;
      const claw = yield* api.get("claw-123");
      expect(claw.id).toBe("claw-123");
    }).pipe(
      Effect.provide(
        ClawApi.Live.pipe(
          Layer.provide(
            mockHttp(
              standardRoutes([
                {
                  method: "GET",
                  path: /\/v2\/organizations\/org-456\/claws\/claw-123$/,
                  response: sampleClaw,
                },
              ]),
            ),
          ),
        ),
      ),
    ),
  );

  it.effect("get maps 404 to NotFoundError", () =>
    Effect.gen(function* () {
      const api = yield* ClawApi;
      const error = yield* api.get("nonexistent").pipe(Effect.flip);
      expect(error._tag).toBe("NotFoundError");
    }).pipe(
      Effect.provide(
        ClawApi.Live.pipe(
          Layer.provide(
            mockHttp(
              standardRoutes([
                {
                  method: "GET",
                  path: /\/v2\/organizations\/org-456\/claws\/nonexistent$/,
                  response: { message: "Not found" },
                  status: 404,
                },
              ]),
            ),
          ),
        ),
      ),
    ),
  );

  it.effect("status returns detail", () =>
    Effect.gen(function* () {
      const api = yield* ClawApi;
      const detail = yield* api.status("claw-123");
      expect(detail.slug).toBe("scouty");
      expect(detail.lastError).toBeNull();
    }).pipe(
      Effect.provide(
        ClawApi.Live.pipe(
          Layer.provide(
            mockHttp(
              standardRoutes([
                {
                  method: "GET",
                  path: /\/v2\/organizations\/org-456\/claws\/claw-123$/,
                  response: sampleClawDetail,
                },
              ]),
            ),
          ),
        ),
      ),
    ),
  );

  it.effect("delete succeeds", () =>
    Effect.gen(function* () {
      const api = yield* ClawApi;
      yield* api.delete("claw-123");
    }).pipe(
      Effect.provide(
        ClawApi.Live.pipe(
          Layer.provide(
            mockHttp(
              standardRoutes([
                {
                  method: "DELETE",
                  path: /\/v2\/organizations\/org-456\/claws\/claw-123$/,
                  response: null,
                },
              ]),
            ),
          ),
        ),
      ),
    ),
  );

  it.effect("delete maps 404 to NotFoundError", () =>
    Effect.gen(function* () {
      const api = yield* ClawApi;
      const error = yield* api.delete("nonexistent").pipe(Effect.flip);
      expect(error._tag).toBe("NotFoundError");
    }).pipe(
      Effect.provide(
        ClawApi.Live.pipe(
          Layer.provide(
            mockHttp(
              standardRoutes([
                {
                  method: "DELETE",
                  path: /\/v2\/organizations\/org-456\/claws\/nonexistent$/,
                  response: { message: "Not found" },
                  status: 404,
                },
              ]),
            ),
          ),
        ),
      ),
    ),
  );
});

describe("ClawApi.Mock", () => {
  const testClaws = [sampleClaw];

  it.effect("list returns mock claws", () =>
    Effect.gen(function* () {
      const api = yield* ClawApi;
      const claws = yield* api.list();
      expect(claws).toHaveLength(1);
    }).pipe(Effect.provide(ClawApi.Mock(testClaws))),
  );

  it.effect("get returns mock claw by id", () =>
    Effect.gen(function* () {
      const api = yield* ClawApi;
      const claw = yield* api.get("claw-123");
      expect(claw.slug).toBe("scouty");
    }).pipe(Effect.provide(ClawApi.Mock(testClaws))),
  );

  it.effect("get fails for unknown id", () =>
    Effect.gen(function* () {
      const api = yield* ClawApi;
      const error = yield* api.get("unknown").pipe(Effect.flip);
      expect(error._tag).toBe("NotFoundError");
    }).pipe(Effect.provide(ClawApi.Mock(testClaws))),
  );
});
