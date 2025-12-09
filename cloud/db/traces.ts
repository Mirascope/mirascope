import { Effect } from "effect";
import { eq } from "drizzle-orm";
import { DrizzleORM } from "@/db/client";
import { DatabaseError, NotFoundError } from "@/errors";
import { traces, type NewTrace } from "@/db/schema/traces";
import { spans, type NewSpan } from "@/db/schema/spans";
import { environments } from "@/db/schema/environments";
import { projects } from "@/db/schema/projects";
import type { ResourceSpans, KeyValue } from "@/api/traces.schemas";

export type EnvironmentContext = {
  environmentId: string;
  projectId: string;
  organizationId: string;
};

export type IngestResult = {
  acceptedSpans: number;
  rejectedSpans: number;
};

/** @internal Exported for testing */
export type OTLPValue = KeyValue["value"];

/**
 * Recursively convert an OTLP value to a plain JSON value.
 * - stringValue -> string
 * - intValue -> string (preserves precision for BigInt)
 * - doubleValue -> number
 * - boolValue -> boolean
 * - arrayValue -> recursively converted array
 * - kvlistValue -> recursively converted object
 *
 * @internal Exported for testing
 */
export function convertOTLPValue(value: OTLPValue): unknown {
  if (value.stringValue !== undefined) {
    return value.stringValue;
  }
  if (value.intValue !== undefined) {
    // Keep as string to preserve precision for BigInt values
    return value.intValue;
  }
  if (value.doubleValue !== undefined) {
    return value.doubleValue;
  }
  if (value.boolValue !== undefined) {
    return value.boolValue;
  }
  if (value.arrayValue !== undefined) {
    const values = value.arrayValue.values ?? [];
    return values.map((item: unknown) => {
      // Array items in OTLP are also AnyValue types
      if (typeof item === "object" && item !== null) {
        return convertOTLPValue(item as OTLPValue);
      }
      return item;
    });
  }
  if (value.kvlistValue !== undefined) {
    const result: Record<string, unknown> = {};
    const values = value.kvlistValue.values ?? [];
    for (const kv of values) {
      if (typeof kv.value === "object" && kv.value !== null) {
        result[kv.key] = convertOTLPValue(kv.value as OTLPValue);
      } else {
        result[kv.key] = kv.value;
      }
    }
    return result;
  }
  return null;
}

/**
 * Convert OTLP KeyValue array to a plain JSON object with recursive normalization
 *
 * @internal Exported for testing
 */
export function keyValueArrayToObject(
  keyValues: readonly KeyValue[] | undefined,
): Record<string, unknown> | null {
  if (!keyValues || keyValues.length === 0) {
    return null;
  }

  const result: Record<string, unknown> = {};
  for (const kv of keyValues) {
    result[kv.key] = convertOTLPValue(kv.value);
  }
  return result;
}

/**
 * Recursively normalize OTLP events array
 *
 * @internal Exported for testing
 */
export function normalizeEvents(
  events: readonly unknown[] | undefined,
): unknown[] | null {
  if (!events || events.length === 0) {
    return null;
  }

  return events.map((event) => {
    if (typeof event !== "object" || event === null) {
      return event;
    }
    const e = event as Record<string, unknown>;
    const normalized: Record<string, unknown> = {};

    if ("name" in e) normalized.name = e.name;
    if ("timeUnixNano" in e) normalized.timeUnixNano = String(e.timeUnixNano);
    if ("attributes" in e && Array.isArray(e.attributes)) {
      normalized.attributes = keyValueArrayToObject(
        e.attributes as readonly KeyValue[],
      );
    }
    if ("droppedAttributesCount" in e) {
      normalized.droppedAttributesCount = e.droppedAttributesCount;
    }

    return normalized;
  });
}

/**
 * Recursively normalize OTLP links array
 *
 * @internal Exported for testing
 */
export function normalizeLinks(
  links: readonly unknown[] | undefined,
): unknown[] | null {
  if (!links || links.length === 0) {
    return null;
  }

  return links.map((link) => {
    if (typeof link !== "object" || link === null) {
      return link;
    }
    const l = link as Record<string, unknown>;
    const normalized: Record<string, unknown> = {};

    if ("traceId" in l) normalized.traceId = l.traceId;
    if ("spanId" in l) normalized.spanId = l.spanId;
    if ("traceState" in l) normalized.traceState = l.traceState;
    if ("attributes" in l && Array.isArray(l.attributes)) {
      normalized.attributes = keyValueArrayToObject(
        l.attributes as readonly KeyValue[],
      );
    }
    if ("droppedAttributesCount" in l) {
      normalized.droppedAttributesCount = l.droppedAttributesCount;
    }

    return normalized;
  });
}

/**
 * Extract service name from resource attributes
 *
 * @internal Exported for testing
 */
export function extractServiceName(
  attributes: readonly KeyValue[] | undefined,
): string | null {
  const attr = attributes?.find((a) => a.key === "service.name");
  return attr?.value?.stringValue ?? null;
}

/**
 * Extract service version from resource attributes
 *
 * @internal Exported for testing
 */
export function extractServiceVersion(
  attributes: readonly KeyValue[] | undefined,
): string | null {
  const attr = attributes?.find((a) => a.key === "service.version");
  return attr?.value?.stringValue ?? null;
}

/**
 * Parse Unix nano timestamp string to BigInt
 *
 * @internal Exported for testing
 */
export function parseUnixNano(value: string): bigint | null {
  try {
    return BigInt(value);
  } catch {
    return null;
  }
}

/**
 * Traces service for OTLP trace ingestion.
 *
 * Uses Effect-native DrizzleORM dependency injection.
 */
export class Traces {
  /**
   * Get environment context (environment -> project -> organization)
   */
  getEnvironmentContext(
    environmentId: string,
  ): Effect.Effect<
    EnvironmentContext,
    NotFoundError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const result = yield* Effect.tryPromise({
        try: async () => {
          return await client
            .select({
              environmentId: environments.id,
              projectId: projects.id,
              organizationId: projects.organizationId,
            })
            .from(environments)
            .innerJoin(projects, eq(environments.projectId, projects.id))
            .where(eq(environments.id, environmentId))
            .limit(1);
        },
        catch: (error) =>
          new DatabaseError({
            message: `Failed to query environment: ${error instanceof Error ? error.message : "Unknown error"}`,
          }),
      });

      const row = result[0];
      if (!row) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Environment ${environmentId} not found`,
            resource: "environment",
          }),
        );
      }

      return {
        environmentId: row.environmentId,
        projectId: row.projectId,
        organizationId: row.organizationId,
      };
    });
  }

  /**
   * Ingest OTLP resource spans into the database
   */
  ingest(
    resourceSpans: readonly ResourceSpans[],
    context: EnvironmentContext,
  ): Effect.Effect<IngestResult, DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      return yield* Effect.tryPromise({
        try: async () => {
          let acceptedSpans = 0;
          let rejectedSpans = 0;

          for (const rs of resourceSpans) {
            const serviceName = extractServiceName(rs.resource?.attributes);
            const serviceVersion = extractServiceVersion(
              rs.resource?.attributes,
            );
            const resourceAttributes = keyValueArrayToObject(
              rs.resource?.attributes,
            );

            for (const scopeSpan of rs.scopeSpans) {
              for (const span of scopeSpan.spans) {
                try {
                  // Upsert trace
                  const traceData: NewTrace = {
                    traceId: span.traceId,
                    environmentId: context.environmentId,
                    projectId: context.projectId,
                    organizationId: context.organizationId,
                    serviceName,
                    serviceVersion,
                    resourceAttributes,
                  };

                  const [upsertedTrace] = await client
                    .insert(traces)
                    .values(traceData)
                    .onConflictDoUpdate({
                      target: [traces.traceId, traces.environmentId],
                      set: {
                        serviceName: traceData.serviceName,
                        serviceVersion: traceData.serviceVersion,
                        resourceAttributes: traceData.resourceAttributes,
                      },
                    })
                    .returning({ id: traces.id });

                  // Insert span with returning to check if actually inserted
                  const spanData: NewSpan = {
                    traceDbId: upsertedTrace.id,
                    traceId: span.traceId,
                    spanId: span.spanId,
                    parentSpanId: span.parentSpanId ?? null,
                    environmentId: context.environmentId,
                    projectId: context.projectId,
                    organizationId: context.organizationId,
                    name: span.name,
                    kind: span.kind ?? null,
                    startTimeUnixNano: parseUnixNano(span.startTimeUnixNano),
                    endTimeUnixNano: parseUnixNano(span.endTimeUnixNano),
                    attributes: keyValueArrayToObject(span.attributes),
                    status: span.status ?? null,
                    events: normalizeEvents(span.events),
                    links: normalizeLinks(span.links),
                    droppedAttributesCount: span.droppedAttributesCount ?? null,
                    droppedEventsCount: span.droppedEventsCount ?? null,
                    droppedLinksCount: span.droppedLinksCount ?? null,
                  };

                  const insertedSpans = await client
                    .insert(spans)
                    .values(spanData)
                    .onConflictDoNothing({
                      target: [
                        spans.spanId,
                        spans.traceId,
                        spans.environmentId,
                      ],
                    })
                    .returning({ id: spans.id });

                  // Only count as accepted if span was actually inserted
                  if (insertedSpans.length > 0) {
                    acceptedSpans++;
                  } else {
                    // Span was a duplicate (conflict)
                    rejectedSpans++;
                  }
                } catch {
                  rejectedSpans++;
                }
              }
            }
          }

          return { acceptedSpans, rejectedSpans };
        },
        catch: (error) =>
          new DatabaseError({
            message: `Failed to ingest traces: ${error instanceof Error ? error.message : "Unknown error"}`,
          }),
      });
    });
  }
}
