import { describe, it, expect } from "@effect/vitest";
import { Effect } from "effect";

import { TestApiClient, TestClient } from "@/tests/api";

describe("Health API", () => {
  it.effect("GET /health", () =>
    Effect.gen(function* () {
      const client = yield* TestApiClient;
      const result = yield* client.health.check();
      expect(result).toMatchObject({
        status: "ok",
        timestamp: expect.any(String) as unknown,
        environment: "test",
      });
    }).pipe(Effect.provide(TestClient.Default)),
  );
});
