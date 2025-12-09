import { describe, it, expect, TestEnvironmentFixture } from "@/tests/db";
import { Effect } from "effect";
import { Database } from "@/db";
import {
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
import { NotFoundError, PermissionDeniedError } from "@/errors";

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
            { stringValue: "item1" },
            { intValue: "42" },
            { boolValue: true },
          ],
        },
      };
      expect(convertOTLPValue(value)).toEqual(["item1", "42", true]);
    });

    it("handles empty arrayValue", () => {
      const value: OTLPValue = { arrayValue: { values: [] } };
      expect(convertOTLPValue(value)).toEqual([]);
    });

    it("handles arrayValue with undefined values", () => {
      const value = { arrayValue: {} } as unknown as OTLPValue;
      expect(convertOTLPValue(value)).toEqual([]);
    });

    it("converts kvlistValue recursively", () => {
      const value: OTLPValue = {
        kvlistValue: {
          values: [
            { key: "name", value: { stringValue: "test" } },
            { key: "count", value: { intValue: "5" } },
          ],
        },
      };
      expect(convertOTLPValue(value)).toEqual({
        name: "test",
        count: "5",
      });
    });

    it("handles empty kvlistValue", () => {
      const value: OTLPValue = { kvlistValue: { values: [] } };
      expect(convertOTLPValue(value)).toEqual({});
    });

    it("handles kvlistValue with undefined values", () => {
      const value = { kvlistValue: {} } as unknown as OTLPValue;
      expect(convertOTLPValue(value)).toEqual({});
    });

    it("handles nested structures", () => {
      const value: OTLPValue = {
        kvlistValue: {
          values: [
            {
              key: "nested",
              value: {
                arrayValue: {
                  values: [{ stringValue: "a" }, { stringValue: "b" }],
                },
              },
            },
          ],
        },
      };
      expect(convertOTLPValue(value)).toEqual({
        nested: ["a", "b"],
      });
    });

    it("returns null for unknown type", () => {
      const value = {} as OTLPValue;
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
        { key: "service.name", value: { stringValue: "test-service" } },
        { key: "count", value: { intValue: "42" } },
      ];
      expect(keyValueArrayToObject(keyValues)).toEqual({
        "service.name": "test-service",
        count: "42",
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

    it("normalizes event objects", () => {
      const events = [
        {
          name: "event1",
          timeUnixNano: "1234567890",
          attributes: [
            { key: "level", value: { stringValue: "info" } },
          ] as KeyValue[],
          droppedAttributesCount: 0,
        },
      ];
      const result = normalizeEvents(events);
      expect(result).toEqual([
        {
          name: "event1",
          timeUnixNano: "1234567890",
          attributes: { level: "info" },
          droppedAttributesCount: 0,
        },
      ]);
    });

    it("handles non-object events", () => {
      const events = ["string", 123, null];
      expect(normalizeEvents(events)).toEqual(["string", 123, null]);
    });
  });

  describe("normalizeLinks", () => {
    it("returns null for undefined", () => {
      expect(normalizeLinks(undefined)).toBeNull();
    });

    it("returns null for empty array", () => {
      expect(normalizeLinks([])).toBeNull();
    });

    it("normalizes link objects", () => {
      const links = [
        {
          traceId: "trace123",
          spanId: "span456",
          traceState: "state1",
          attributes: [
            { key: "attr", value: { stringValue: "val" } },
          ] as KeyValue[],
          droppedLinksCount: 0,
        },
      ];
      const result = normalizeLinks(links);
      expect(result).toEqual([
        {
          traceId: "trace123",
          spanId: "span456",
          traceState: "state1",
          attributes: { attr: "val" },
          droppedLinksCount: 0,
        },
      ]);
    });

    it("handles non-object links", () => {
      const links = ["string", 123, null];
      expect(normalizeLinks(links)).toEqual(["string", 123, null]);
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
        { key: "other", value: { stringValue: "value" } },
      ];
      expect(extractServiceVersion(attributes)).toBe("1.0.0");
    });

    it("returns null when not found", () => {
      const attributes: KeyValue[] = [
        { key: "other", value: { stringValue: "value" } },
      ];
      expect(extractServiceVersion(attributes)).toBeNull();
    });

    it("returns null for undefined", () => {
      expect(extractServiceVersion(undefined)).toBeNull();
    });
  });

  describe("parseUnixNano", () => {
    it("parses valid timestamp", () => {
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
  describe("create", () => {
    it.effect("creates single span", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

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

        const result = yield* db.traces.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: { resourceSpans },
        });

        expect(result).toEqual({
          acceptedSpans: 1,
          rejectedSpans: 0,
        });
      }),
    );

    it.effect("creates multiple spans", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

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

        const result = yield* db.traces.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: { resourceSpans },
        });

        expect(result).toEqual({
          acceptedSpans: 2,
          rejectedSpans: 0,
        });
      }),
    );

    it.effect("upserts trace on conflict", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

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

        // First create
        const result1 = yield* db.traces.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: { resourceSpans: makeResourceSpans("span-a", "service-v1") },
        });

        expect(result1.acceptedSpans).toBe(1);

        // Second create with same trace but different span
        const result2 = yield* db.traces.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: { resourceSpans: makeResourceSpans("span-b", "service-v2") },
        });

        expect(result2.acceptedSpans).toBe(1);
      }),
    );

    it.effect("rejects duplicate spans", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

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

        // First create
        const result1 = yield* db.traces.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: { resourceSpans },
        });

        expect(result1).toEqual({ acceptedSpans: 1, rejectedSpans: 0 });

        // Second create with same span (duplicate)
        const result2 = yield* db.traces.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: { resourceSpans },
        });

        expect(result2).toEqual({ acceptedSpans: 0, rejectedSpans: 1 });
      }),
    );

    it.effect("handles span with null/optional fields", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

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

        const result = yield* db.traces.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: { resourceSpans },
        });

        expect(result.acceptedSpans).toBe(1);
      }),
    );

    it.effect("handles span with events and links", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

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

        const result = yield* db.traces.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: { resourceSpans },
        });

        expect(result.acceptedSpans).toBe(1);
      }),
    );

    it.effect("returns PermissionDeniedError for VIEWER role", () =>
      Effect.gen(function* () {
        const { environment, project, org, projectViewer } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const resourceSpans = [
          {
            resource: { attributes: [] },
            scopeSpans: [
              {
                scope: { name: "test" },
                spans: [
                  {
                    traceId: "trace-perm",
                    spanId: "span-perm",
                    name: "test-span",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                ],
              },
            ],
          },
        ];

        const result = yield* db.traces
          .create({
            userId: projectViewer.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { resourceSpans },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
        expect(result.message).toContain("permission");
      }),
    );

    it.effect("returns PermissionDeniedError for ANNOTATOR role", () =>
      Effect.gen(function* () {
        const { environment, project, org, projectAnnotator } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const resourceSpans = [
          {
            resource: { attributes: [] },
            scopeSpans: [
              {
                scope: { name: "test" },
                spans: [
                  {
                    traceId: "trace-perm2",
                    spanId: "span-perm2",
                    name: "test-span",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                ],
              },
            ],
          },
        ];

        const result = yield* db.traces
          .create({
            userId: projectAnnotator.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            data: { resourceSpans },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
        expect(result.message).toContain("permission");
      }),
    );
  });

  describe("findAll", () => {
    it.effect("returns PermissionDeniedError (not supported)", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result = yield* db.traces
          .findAll({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
        expect(result.message).toContain("not supported");
      }),
    );
  });

  describe("findById", () => {
    it.effect("returns PermissionDeniedError (not supported)", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result = yield* db.traces
          .findById({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            traceId: "some-trace-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
        expect(result.message).toContain("not supported");
      }),
    );
  });

  describe("update", () => {
    it.effect("returns PermissionDeniedError (traces are immutable)", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result = yield* db.traces
          .update({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            traceId: "some-trace-id",
            data: undefined as never,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
        expect(result.message).toContain("immutable");
      }),
    );
  });

  describe("delete", () => {
    it.effect("deletes trace and associated spans", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        // First create a trace
        const resourceSpans = [
          {
            resource: {
              attributes: [
                { key: "service.name", value: { stringValue: "del-service" } },
              ],
            },
            scopeSpans: [
              {
                scope: { name: "test" },
                spans: [
                  {
                    traceId: "trace-to-delete",
                    spanId: "span-to-delete",
                    name: "test-span",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                ],
              },
            ],
          },
        ];

        yield* db.traces.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: { resourceSpans },
        });

        // Delete the trace
        yield* db.traces.delete({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          traceId: "trace-to-delete",
        });

        // Verify deletion by trying to create the same span again
        const result = yield* db.traces.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: { resourceSpans },
        });

        // Should succeed since the trace was deleted
        expect(result.acceptedSpans).toBe(1);
      }),
    );

    it.effect("returns NotFoundError when trace not found", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        const result = yield* db.traces
          .delete({
            userId: owner.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            traceId: "non-existent-trace-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect("returns PermissionDeniedError for DEVELOPER role", () =>
      Effect.gen(function* () {
        const { environment, project, org, owner, projectDeveloper } =
          yield* TestEnvironmentFixture;
        const db = yield* Database;

        // First create a trace as owner
        const resourceSpans = [
          {
            resource: { attributes: [] },
            scopeSpans: [
              {
                scope: { name: "test" },
                spans: [
                  {
                    traceId: "trace-no-delete",
                    spanId: "span-no-delete",
                    name: "test-span",
                    startTimeUnixNano: "1000000000",
                    endTimeUnixNano: "2000000000",
                  },
                ],
              },
            ],
          },
        ];

        yield* db.traces.create({
          userId: owner.id,
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
          data: { resourceSpans },
        });

        // Developer should not be able to delete
        const result = yield* db.traces
          .delete({
            userId: projectDeveloper.id,
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
            traceId: "trace-no-delete",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
        expect(result.message).toContain("delete");
      }),
    );
  });
});
