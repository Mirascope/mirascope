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
        authenticatedUser: mockUser,
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
          authenticatedUser: mockUser,
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
          authenticatedUser: mockUser,
          environment: "test",
        }).pipe(Effect.flip);

        expect(error).toBeInstanceOf(HandlerError);
        expect(error.message).toContain(
          "[Effect API] Error handling request: boom",
        );
      }),
  );
});
