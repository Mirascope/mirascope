import { describe, it, expect } from "@effect/vitest";
import { Effect } from "effect";
import { TestApiClient, TestClient } from "@/tests/api";

describe("Functions API", () => {
  it.effect("POST /functions - requires API key auth", () =>
    Effect.gen(function* () {
      const client = yield* TestApiClient;

      const result = yield* Effect.either(
        client.functions.register({
          payload: {
            code: "def foo(): pass",
            hash: "test-hash",
            signature: "def foo()",
            signatureHash: "sig-hash",
            name: "foo",
          },
        }),
      );

      expect(result._tag).toBe("Left");
    }).pipe(Effect.provide(TestClient.Default)),
  );

  it.effect("GET /functions - requires API key auth", () =>
    Effect.gen(function* () {
      const client = yield* TestApiClient;

      const result = yield* Effect.either(
        client.functions.list({ urlParams: {} }),
      );

      expect(result._tag).toBe("Left");
    }).pipe(Effect.provide(TestClient.Default)),
  );

  it.effect("GET /functions/:id - requires API key auth", () =>
    Effect.gen(function* () {
      const client = yield* TestApiClient;

      const result = yield* Effect.either(
        client.functions.get({ path: { id: "test-id" } }),
      );

      expect(result._tag).toBe("Left");
    }).pipe(Effect.provide(TestClient.Default)),
  );

  it.effect("GET /functions/by-hash/:hash - requires API key auth", () =>
    Effect.gen(function* () {
      const client = yield* TestApiClient;

      const result = yield* Effect.either(
        client.functions.getByHash({ path: { hash: "test-hash" } }),
      );

      expect(result._tag).toBe("Left");
    }).pipe(Effect.provide(TestClient.Default)),
  );
});
