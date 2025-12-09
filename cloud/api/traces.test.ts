import { describe, it, expect } from "@effect/vitest";
import { Effect } from "effect";
import { TestApiClient, TestClient } from "@/tests/api";

describe("Traces API", () => {
  it.effect("POST /traces - requires API key auth", () =>
    Effect.gen(function* () {
      const client = yield* TestApiClient;
      const payload = {
        resourceSpans: [
          {
            resource: {
              attributes: [
                {
                  key: "service.name",
                  value: {
                    stringValue: "test-service",
                  },
                },
              ],
            },
            scopeSpans: [
              {
                scope: {
                  name: "test-scope",
                  version: "1.0.0",
                },
                spans: [
                  {
                    traceId: "test-trace-id",
                    spanId: "test-span-id",
                    name: "test-span",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                ],
              },
            ],
          },
        ],
      };

      const result = yield* Effect.either(client.traces.create({ payload }));
      expect(result._tag).toBe("Left");
    }).pipe(Effect.provide(TestClient.Default)),
  );
});
