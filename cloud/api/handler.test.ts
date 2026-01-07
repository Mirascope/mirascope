import { Effect } from "effect";
import { describe, it, expect } from "@/tests/api";
import { handleRequest } from "@/api/handler";
import type { PublicUser } from "@/db/schema";
import { HandlerError } from "@/errors";

const mockUser: PublicUser = {
  id: "test-user-id",
  email: "test@example.com",
  name: "Test User",
  deletedAt: null,
};

describe("handleRequest", () => {
  it.effect("should return 404 for non-existing routes", () =>
    Effect.gen(function* () {
      const req = new Request(
        "http://localhost/api/v0/this-route-does-not-exist",
        { method: "GET" },
      );

      const { matched, response } = yield* handleRequest(req, {
        user: mockUser,
        environment: "test",
        prefix: "/api/v0",
      });

      expect(response.status).toBe(404);
      expect(matched).toBe(false);
    }),
  );

  it.effect(
    "should return 404 when pathname exactly matches prefix (no route)",
    () =>
      Effect.gen(function* () {
        const req = new Request("http://localhost/api/v0", { method: "GET" });

        const { matched, response } = yield* handleRequest(req, {
          user: mockUser,
          environment: "test",
          prefix: "/api/v0",
        });

        // The path becomes "/" after stripping prefix, which doesn't match any route
        expect(response.status).toBe(404);
        expect(matched).toBe(false);
      }),
  );

  it.effect(
    "should return error for a request that triggers an exception",
    () =>
      Effect.gen(function* () {
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
        }).pipe(Effect.flip);

        expect(error).toBeInstanceOf(HandlerError);
        expect(error.message).toContain(
          "[Effect API] Error handling request: boom",
        );
      }),
  );

  it.effect("should handle POST requests with body", () =>
    Effect.gen(function* () {
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
      });

      expect(matched).toBe(true);
      expect(response.status).toBeGreaterThanOrEqual(400);
    }),
  );

  it.effect("should transform _tag in JSON error responses", () =>
    Effect.gen(function* () {
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
      });

      const body = yield* Effect.promise(() => response.text());

      expect(matched).toBe(true);
      expect(response.status).toBeGreaterThanOrEqual(400);
      // Ensure _tag is transformed to tag in error responses
      expect(body).toContain('"tag"');
      expect(body).not.toContain('"_tag"');
    }),
  );
});
