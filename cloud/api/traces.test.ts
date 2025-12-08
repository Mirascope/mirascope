import { describe, it, expect } from "vitest";
import { Effect } from "effect";
import { withTestClient } from "@/tests/api";

describe(
  "Traces API",
  withTestClient(async (client) => {
    it("POST /traces", async () => {
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

      const result = await Effect.runPromise(client.traces.create({ payload }));
      expect(result).toMatchObject({
        partialSuccess: expect.any(Object),
      });
    });

    it("POST /traces - missing service.name and spans", async () => {
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

      const result = await Effect.runPromise(client.traces.create({ payload }));
      expect(result).toMatchObject({
        partialSuccess: expect.any(Object),
      });
    });
  }),
);
