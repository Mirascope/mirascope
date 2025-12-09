import { describe, it, expect, TestEnvironmentFixture } from "@/tests/db";
import { Effect } from "effect";
import { DrizzleORM } from "@/db/client";
import {
  Traces,
  convertOTLPValue,
  keyValueArrayToObject,
  normalizeEvents,
  normalizeLinks,
  extractServiceName,
  extractServiceVersion,
  parseUnixNano,
  type OTLPValue,
} from "@/db/traces";
import type { KeyValue } from "@/api/traces.schemas";
import { NotFoundError } from "@/errors";

// =============================================================================
// Helper function tests
// =============================================================================

describe("Traces helper functions", () => {
  describe("convertOTLPValue", () => {
    it("converts stringValue", () => {
      const value: OTLPValue = { stringValue: "hello" };
      expect(convertOTLPValue(value)).toBe("hello");
    });

    it("converts intValue", () => {
      const value: OTLPValue = { intValue: "12345" };
      expect(convertOTLPValue(value)).toBe("12345");
    });

    it("converts doubleValue", () => {
      const value: OTLPValue = { doubleValue: 3.14 };
      expect(convertOTLPValue(value)).toBe(3.14);
    });

    it("converts boolValue true", () => {
      const value: OTLPValue = { boolValue: true };
      expect(convertOTLPValue(value)).toBe(true);
    });

    it("converts boolValue false", () => {
      const value: OTLPValue = { boolValue: false };
      expect(convertOTLPValue(value)).toBe(false);
    });

    it("converts arrayValue recursively", () => {
      const value: OTLPValue = {
        arrayValue: {
          values: [
            { stringValue: "a" },
            { intValue: "1" },
            { doubleValue: 2.5 },
          ],
        },
      };
      expect(convertOTLPValue(value)).toEqual(["a", "1", 2.5]);
    });

    it("converts arrayValue with undefined values", () => {
      const value: OTLPValue = {
        arrayValue: { values: undefined as unknown as readonly unknown[] },
      };
      expect(convertOTLPValue(value)).toEqual([]);
    });

    it("converts arrayValue with primitive items", () => {
      const value: OTLPValue = {
        arrayValue: {
          values: ["primitive" as unknown],
        },
      };
      expect(convertOTLPValue(value)).toEqual(["primitive"]);
    });

    it("converts kvlistValue recursively", () => {
      const value: OTLPValue = {
        kvlistValue: {
          values: [
            { key: "name", value: { stringValue: "test" } },
            { key: "count", value: { intValue: "42" } },
          ],
        },
      };
      expect(convertOTLPValue(value)).toEqual({ name: "test", count: "42" });
    });

    it("converts kvlistValue with undefined values", () => {
      const value: OTLPValue = {
        kvlistValue: {
          values: undefined as unknown as readonly {
            readonly value: unknown;
            readonly key: string;
          }[],
        },
      };
      expect(convertOTLPValue(value)).toEqual({});
    });

    it("converts kvlistValue with non-object values", () => {
      const value: OTLPValue = {
        kvlistValue: {
          values: [{ key: "primitive", value: "raw" as unknown }],
        },
      };
      expect(convertOTLPValue(value)).toEqual({ primitive: "raw" });
    });

    it("returns null for unknown type", () => {
      const value: OTLPValue = {};
      expect(convertOTLPValue(value)).toBeNull();
    });
  });

  describe("keyValueArrayToObject", () => {
    it("returns null for undefined", () => {
      expect(keyValueArrayToObject(undefined)).toBeNull();
    });

    it("returns null for empty array", () => {
      expect(keyValueArrayToObject([])).toBeNull();
    });

    it("converts KeyValue array to object", () => {
      const keyValues: KeyValue[] = [
        { key: "service.name", value: { stringValue: "my-service" } },
        { key: "port", value: { intValue: "8080" } },
      ];
      expect(keyValueArrayToObject(keyValues)).toEqual({
        "service.name": "my-service",
        port: "8080",
      });
    });
  });

  describe("normalizeEvents", () => {
    it("returns null for undefined", () => {
      expect(normalizeEvents(undefined)).toBeNull();
    });

    it("returns null for empty array", () => {
      expect(normalizeEvents([])).toBeNull();
    });

    it("returns primitive values as-is", () => {
      expect(normalizeEvents(["primitive", null])).toEqual(["primitive", null]);
    });

    it("normalizes event objects", () => {
      const events = [
        {
          name: "exception",
          timeUnixNano: 1234567890,
          attributes: [
            { key: "message", value: { stringValue: "Error occurred" } },
          ],
          droppedAttributesCount: 0,
        },
      ];
      expect(normalizeEvents(events)).toEqual([
        {
          name: "exception",
          timeUnixNano: "1234567890",
          attributes: { message: "Error occurred" },
          droppedAttributesCount: 0,
        },
      ]);
    });

    it("normalizes event without attributes", () => {
      const events = [{ name: "simple" }];
      expect(normalizeEvents(events)).toEqual([{ name: "simple" }]);
    });
  });

  describe("normalizeLinks", () => {
    it("returns null for undefined", () => {
      expect(normalizeLinks(undefined)).toBeNull();
    });

    it("returns null for empty array", () => {
      expect(normalizeLinks([])).toBeNull();
    });

    it("returns primitive values as-is", () => {
      expect(normalizeLinks(["primitive", null])).toEqual(["primitive", null]);
    });

    it("normalizes link objects", () => {
      const links = [
        {
          traceId: "abc123",
          spanId: "def456",
          traceState: "state",
          attributes: [{ key: "ref", value: { stringValue: "parent" } }],
          droppedAttributesCount: 1,
        },
      ];
      expect(normalizeLinks(links)).toEqual([
        {
          traceId: "abc123",
          spanId: "def456",
          traceState: "state",
          attributes: { ref: "parent" },
          droppedAttributesCount: 1,
        },
      ]);
    });

    it("normalizes link without attributes", () => {
      const links = [{ traceId: "abc" }];
      expect(normalizeLinks(links)).toEqual([{ traceId: "abc" }]);
    });
  });

  describe("extractServiceName", () => {
    it("extracts service.name attribute", () => {
      const attributes: KeyValue[] = [
        { key: "service.name", value: { stringValue: "my-service" } },
        { key: "other", value: { stringValue: "value" } },
      ];
      expect(extractServiceName(attributes)).toBe("my-service");
    });

    it("returns null when not found", () => {
      const attributes: KeyValue[] = [
        { key: "other", value: { stringValue: "value" } },
      ];
      expect(extractServiceName(attributes)).toBeNull();
    });

    it("returns null for undefined", () => {
      expect(extractServiceName(undefined)).toBeNull();
    });

    it("returns null when value is not stringValue", () => {
      const attributes: KeyValue[] = [
        { key: "service.name", value: { intValue: "123" } },
      ];
      expect(extractServiceName(attributes)).toBeNull();
    });
  });

  describe("extractServiceVersion", () => {
    it("extracts service.version attribute", () => {
      const attributes: KeyValue[] = [
        { key: "service.version", value: { stringValue: "1.0.0" } },
      ];
      expect(extractServiceVersion(attributes)).toBe("1.0.0");
    });

    it("returns null when not found", () => {
      const attributes: KeyValue[] = [];
      expect(extractServiceVersion(attributes)).toBeNull();
    });

    it("returns null for undefined", () => {
      expect(extractServiceVersion(undefined)).toBeNull();
    });
  });

  describe("parseUnixNano", () => {
    it("parses valid nano timestamp", () => {
      expect(parseUnixNano("1234567890123456789")).toBe(
        BigInt("1234567890123456789"),
      );
    });

    it("returns null for invalid value", () => {
      expect(parseUnixNano("not-a-number")).toBeNull();
    });
  });
});

// =============================================================================
// Traces class tests
// =============================================================================

describe("Traces", () => {
  const traces = new Traces();

  describe("getEnvironmentContext", () => {
    it.effect("returns context for valid environmentId", () =>
      Effect.gen(function* () {
        const { environment, project, org } = yield* TestEnvironmentFixture;

        const context = yield* traces
          .getEnvironmentContext(environment.id)
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        expect(context).toEqual({
          environmentId: environment.id,
          projectId: project.id,
          organizationId: org.id,
        });
      }),
    );

    it.effect("returns NotFoundError when environment not found", () =>
      Effect.gen(function* () {
        const result = yield* traces
          .getEnvironmentContext("00000000-0000-0000-0000-000000000000")
          .pipe(
            Effect.provide(yield* Effect.context<DrizzleORM>()),
            Effect.flip,
          );

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toContain("not found");
      }),
    );
  });

  describe("ingest", () => {
    it.effect("ingests single span", () =>
      Effect.gen(function* () {
        const { environment, project, org } = yield* TestEnvironmentFixture;
        const context = {
          environmentId: environment.id,
          projectId: project.id,
          organizationId: org.id,
        };

        const resourceSpans = [
          {
            resource: {
              attributes: [
                { key: "service.name", value: { stringValue: "test-service" } },
                { key: "service.version", value: { stringValue: "1.0.0" } },
              ],
            },
            scopeSpans: [
              {
                scope: { name: "test" },
                spans: [
                  {
                    traceId: "abc123",
                    spanId: "span001",
                    name: "test-span",
                    startTimeUnixNano: "1234567890000000000",
                    endTimeUnixNano: "1234567891000000000",
                  },
                ],
              },
            ],
          },
        ];

        const result = yield* traces
          .ingest(resourceSpans, context)
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        expect(result).toEqual({
          acceptedSpans: 1,
          rejectedSpans: 0,
        });
      }),
    );

    it.effect("ingests multiple spans", () =>
      Effect.gen(function* () {
        const { environment, project, org } = yield* TestEnvironmentFixture;
        const context = {
          environmentId: environment.id,
          projectId: project.id,
          organizationId: org.id,
        };

        const resourceSpans = [
          {
            resource: {
              attributes: [
                { key: "service.name", value: { stringValue: "test-service" } },
              ],
            },
            scopeSpans: [
              {
                scope: { name: "test" },
                spans: [
                  {
                    traceId: "trace001",
                    spanId: "span001",
                    name: "span-1",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                  {
                    traceId: "trace001",
                    spanId: "span002",
                    parentSpanId: "span001",
                    name: "span-2",
                    startTimeUnixNano: "1100000000",
                    endTimeUnixNano: "1900000000",
                  },
                ],
              },
            ],
          },
        ];

        const result = yield* traces
          .ingest(resourceSpans, context)
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        expect(result).toEqual({
          acceptedSpans: 2,
          rejectedSpans: 0,
        });
      }),
    );

    it.effect("upserts trace on conflict", () =>
      Effect.gen(function* () {
        const { environment, project, org } = yield* TestEnvironmentFixture;
        const context = {
          environmentId: environment.id,
          projectId: project.id,
          organizationId: org.id,
        };

        const makeResourceSpans = (spanId: string, serviceName: string) => [
          {
            resource: {
              attributes: [
                { key: "service.name", value: { stringValue: serviceName } },
              ],
            },
            scopeSpans: [
              {
                scope: { name: "test" },
                spans: [
                  {
                    traceId: "same-trace-id",
                    spanId,
                    name: "span",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                ],
              },
            ],
          },
        ];

        // First ingest
        const result1 = yield* traces
          .ingest(makeResourceSpans("span-a", "service-v1"), context)
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        expect(result1.acceptedSpans).toBe(1);

        // Second ingest with same trace but different span
        const result2 = yield* traces
          .ingest(makeResourceSpans("span-b", "service-v2"), context)
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        expect(result2.acceptedSpans).toBe(1);
      }),
    );

    it.effect("rejects duplicate spans", () =>
      Effect.gen(function* () {
        const { environment, project, org } = yield* TestEnvironmentFixture;
        const context = {
          environmentId: environment.id,
          projectId: project.id,
          organizationId: org.id,
        };

        const resourceSpans = [
          {
            resource: { attributes: [] },
            scopeSpans: [
              {
                scope: { name: "test" },
                spans: [
                  {
                    traceId: "trace-dup",
                    spanId: "span-dup",
                    name: "duplicate-span",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                ],
              },
            ],
          },
        ];

        // First ingest
        const result1 = yield* traces
          .ingest(resourceSpans, context)
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        expect(result1).toEqual({ acceptedSpans: 1, rejectedSpans: 0 });

        // Second ingest with same span (duplicate)
        const result2 = yield* traces
          .ingest(resourceSpans, context)
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        expect(result2).toEqual({ acceptedSpans: 0, rejectedSpans: 1 });
      }),
    );

    it.effect("handles span with null/optional fields", () =>
      Effect.gen(function* () {
        const { environment, project, org } = yield* TestEnvironmentFixture;
        const context = {
          environmentId: environment.id,
          projectId: project.id,
          organizationId: org.id,
        };

        const resourceSpans = [
          {
            resource: {},
            scopeSpans: [
              {
                scope: { name: "test" },
                spans: [
                  {
                    traceId: "trace-null",
                    spanId: "span-null",
                    name: "minimal-span",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                    // All optional fields are missing
                  },
                ],
              },
            ],
          },
        ];

        const result = yield* traces
          .ingest(resourceSpans, context)
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        expect(result.acceptedSpans).toBe(1);
      }),
    );

    it.effect("handles span with events and links", () =>
      Effect.gen(function* () {
        const { environment, project, org } = yield* TestEnvironmentFixture;
        const context = {
          environmentId: environment.id,
          projectId: project.id,
          organizationId: org.id,
        };

        const resourceSpans = [
          {
            resource: {
              attributes: [
                { key: "service.name", value: { stringValue: "test" } },
              ],
            },
            scopeSpans: [
              {
                scope: { name: "test" },
                spans: [
                  {
                    traceId: "trace-events",
                    spanId: "span-events",
                    name: "span-with-events",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                    kind: 1,
                    status: { code: 1, message: "OK" },
                    attributes: [
                      { key: "attr1", value: { stringValue: "val1" } },
                    ],
                    events: [
                      {
                        name: "event1",
                        timeUnixNano: "1500000000",
                        attributes: [
                          { key: "level", value: { stringValue: "info" } },
                        ],
                      },
                    ],
                    links: [
                      {
                        traceId: "linked-trace",
                        spanId: "linked-span",
                      },
                    ],
                    droppedAttributesCount: 0,
                    droppedEventsCount: 0,
                    droppedLinksCount: 0,
                  },
                ],
              },
            ],
          },
        ];

        const result = yield* traces
          .ingest(resourceSpans, context)
          .pipe(Effect.provide(yield* Effect.context<DrizzleORM>()));

        expect(result.acceptedSpans).toBe(1);
      }),
    );
  });
});
