import { describe, it, expect } from "@effect/vitest";
import { Effect } from "effect";
import { TestApiClient, TestClient } from "@/tests/api";

describe("Annotations API", () => {
  it.effect("POST /annotations - requires API key auth", () =>
    Effect.gen(function* () {
      const client = yield* TestApiClient;

      const result = yield* Effect.either(
        client.annotations.create({
          payload: {
            spanId: "test-span-id",
            traceId: "test-trace-id",
            label: "test-label",
          },
        }),
      );

      expect(result._tag).toBe("Left");
    }).pipe(Effect.provide(TestClient.Default)),
  );

  it.effect("GET /annotations - requires API key auth", () =>
    Effect.gen(function* () {
      const client = yield* TestApiClient;

      const result = yield* Effect.either(
        client.annotations.list({ urlParams: { spanId: "test-span-id" } }),
      );

      expect(result._tag).toBe("Left");
    }).pipe(Effect.provide(TestClient.Default)),
  );

  it.effect("GET /annotations/:id - requires API key auth", () =>
    Effect.gen(function* () {
      const client = yield* TestApiClient;

      const result = yield* Effect.either(
        client.annotations.get({ path: { id: "test-id" } }),
      );

      expect(result._tag).toBe("Left");
    }).pipe(Effect.provide(TestClient.Default)),
  );

  it.effect("PUT /annotations/:id - requires API key auth", () =>
    Effect.gen(function* () {
      const client = yield* TestApiClient;

      const result = yield* Effect.either(
        client.annotations.update({
          path: { id: "test-id" },
          payload: { label: "updated-label" },
        }),
      );

      expect(result._tag).toBe("Left");
    }).pipe(Effect.provide(TestClient.Default)),
  );

  it.effect("DELETE /annotations/:id - requires API key auth", () =>
    Effect.gen(function* () {
      const client = yield* TestApiClient;

      const result = yield* Effect.either(
        client.annotations.delete({ path: { id: "test-id" } }),
      );

      expect(result._tag).toBe("Left");
    }).pipe(Effect.provide(TestClient.Default)),
  );
});
