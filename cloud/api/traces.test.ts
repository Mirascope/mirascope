import { describe, it, expect } from "@effect/vitest";
import { Effect } from "effect";
import { TestApiClient, TestClient } from "@/tests/api";

describe("Traces API", () => {
  it.effect("POST /traces", () =>
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

      const result = yield* client.traces.create({ payload });
      expect(result).toMatchObject({
        partialSuccess: expect.any(Object) as unknown,
      });
    }).pipe(Effect.provide(TestClient.Default)),
  );

  it.effect("POST /traces - missing service.name and spans", () =>
    Effect.gen(function* () {
      const client = yield* TestApiClient;
      const payload = {
        resourceSpans: [
          {
            resource: {
              attributes: [
                {
                  key: "other.attribute",
                  value: {
                    stringValue: "other-value",
                  },
                },
              ],
            },
            scopeSpans: [
              {
                scope: {
                  name: "test-scope",
                },
                spans: [],
              },
            ],
          },
        ],
      };

      const result = yield* client.traces.create({ payload });
      expect(result).toMatchObject({
        partialSuccess: expect.any(Object) as unknown,
      });
    }).pipe(Effect.provide(TestClient.Default)),
  );
});
