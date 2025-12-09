/**
 * Effect-native Traces service for OTLP ingestion.
 * Authorization is delegated to project memberships.
 */

import { Effect } from "effect";
import { and, eq } from "drizzle-orm";
import {
  BaseAuthenticatedEffectService,
  type PermissionTable,
} from "@/db/base";
import { DrizzleORM } from "@/db/client";
import { ProjectMemberships } from "@/db/project-memberships";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/errors";
import { traces, type NewTrace } from "@/db/schema/traces";
import { spans, type NewSpan } from "@/db/schema/spans";
import type { ProjectRole } from "@/db/schema";
import type { ResourceSpans, KeyValue } from "@/api/traces.schemas";

export type IngestResult = {
  acceptedSpans: number;
  rejectedSpans: number;
};

export type TraceCreateInput = {
  resourceSpans: readonly ResourceSpans[];
};

export type OTLPValue = KeyValue["value"];

/**
 * Convert an OTLP value to a plain JSON value.
 */
export function convertOTLPValue(value: OTLPValue): unknown {
  if (value.stringValue !== undefined) {
    return value.stringValue;
  }
  if (value.intValue !== undefined) {
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

/** Convert OTLP KeyValue array to a plain JSON object. */
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

/** Normalize OTLP events. */
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

/** Normalize OTLP links. */
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
    if ("droppedLinksCount" in l) {
      normalized.droppedLinksCount = l.droppedLinksCount;
    }

    return normalized;
  });
}

/** Extract service name from resource attributes. */
export function extractServiceName(
  attributes: readonly KeyValue[] | undefined,
): string | null {
  const attr = attributes?.find((a) => a.key === "service.name");
  return attr?.value?.stringValue ?? null;
}

/** Extract service version from resource attributes. */
export function extractServiceVersion(
  attributes: readonly KeyValue[] | undefined,
): string | null {
  const attr = attributes?.find((a) => a.key === "service.version");
  return attr?.value?.stringValue ?? null;
}

/** Parse Unix nano timestamp string to BigInt. */
export function parseUnixNano(value: string): bigint | null {
  try {
    return BigInt(value);
  } catch {
    return null;
  }
}

type TracePath =
  "organizations/:organizationId/projects/:projectId/environments/:environmentId/traces/:traceId";

export class Traces extends BaseAuthenticatedEffectService<
  IngestResult,
  TracePath,
  TraceCreateInput,
  never,
  ProjectRole
> {
  private readonly projectMemberships: ProjectMemberships;

  constructor(projectMemberships: ProjectMemberships) {
    super();
    this.projectMemberships = projectMemberships;
  }

  protected getResourceName(): string {
    return "trace";
  }

  protected getPermissionTable(): PermissionTable<ProjectRole> {
    return {
      create: ["ADMIN", "DEVELOPER"],
      read: ["ADMIN", "DEVELOPER", "VIEWER", "ANNOTATOR"],
      update: ["ADMIN", "DEVELOPER"],
      delete: ["ADMIN"],
    };
  }

  getRole({
    userId,
    organizationId,
    projectId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId?: string;
    traceId?: string;
  }): Effect.Effect<
    ProjectRole,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return this.projectMemberships.getRole({
      userId,
      organizationId,
      projectId,
    });
  }

  create({
    userId,
    organizationId,
    projectId,
    environmentId,
    data,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    data: TraceCreateInput;
  }): Effect.Effect<
    IngestResult,
    AlreadyExistsError | NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({
        userId,
        action: "create",
        organizationId,
        projectId,
        environmentId,
        traceId: "",
      });

      return yield* this.ingest({
        environmentId,
        projectId,
        organizationId,
        resourceSpans: data.resourceSpans,
      });
    });
  }

  findAll({
    userId,
    organizationId,
    projectId,
    environmentId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
  }): Effect.Effect<
    IngestResult[],
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        traceId: "",
      });

      return yield* Effect.fail(
        new PermissionDeniedError({
          message: "Trace listing is not supported. Use a query service.",
          resource: "trace",
        }),
      );
    });
  }

  findById({
    userId,
    organizationId,
    projectId,
    environmentId,
    traceId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    traceId: string;
  }): Effect.Effect<
    IngestResult,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        traceId,
      });

      return yield* Effect.fail(
        new PermissionDeniedError({
          message: "Trace retrieval is not supported. Use a query service.",
          resource: "trace",
        }),
      );
    });
  }

  update({
    userId,
    organizationId,
    projectId,
    environmentId,
    traceId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    traceId: string;
    data: never;
  }): Effect.Effect<
    IngestResult,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({
        userId,
        action: "update",
        organizationId,
        projectId,
        environmentId,
        traceId,
      });

      return yield* Effect.fail(
        new PermissionDeniedError({
          message: "Traces are immutable and cannot be updated.",
          resource: "trace",
        }),
      );
    });
  }

  delete({
    userId,
    organizationId,
    projectId,
    environmentId,
    traceId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    traceId: string;
  }): Effect.Effect<
    void,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({
        userId,
        action: "delete",
        organizationId,
        projectId,
        environmentId,
        traceId,
      });

      const client = yield* DrizzleORM;

      yield* client
        .delete(spans)
        .where(
          and(
            eq(spans.traceId, traceId),
            eq(spans.environmentId, environmentId),
          ),
        )
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to delete spans",
                cause: e,
              }),
          ),
        );

      const result: { id: string }[] = yield* client
        .delete(traces)
        .where(
          and(
            eq(traces.traceId, traceId),
            eq(traces.environmentId, environmentId),
          ),
        )
        .returning({ id: traces.id })
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to delete trace",
                cause: e,
              }),
          ),
        );

      const [row] = result;
      if (!row) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Trace ${traceId} not found`,
            resource: "trace",
          }),
        );
      }
    });
  }

  private ingest({
    organizationId,
    projectId,
    environmentId,
    resourceSpans,
  }: {
    organizationId: string;
    projectId: string;
    environmentId: string;
    resourceSpans: readonly ResourceSpans[];
  }): Effect.Effect<IngestResult, DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      let acceptedSpans = 0;
      let rejectedSpans = 0;

      for (const rs of resourceSpans) {
        const serviceName = extractServiceName(rs.resource?.attributes);
        const serviceVersion = extractServiceVersion(rs.resource?.attributes);
        const resourceAttributes = keyValueArrayToObject(
          rs.resource?.attributes,
        );

        for (const scopeSpan of rs.scopeSpans) {
          for (const span of scopeSpan.spans) {
            const result = yield* Effect.gen(function* () {
              const traceData: NewTrace = {
                traceId: span.traceId,
                environmentId,
                projectId,
                organizationId,
                serviceName,
                serviceVersion,
                resourceAttributes,
              };

              const [upsertedTrace] = yield* client
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
                .returning({ id: traces.id })
                .pipe(
                  Effect.mapError(
                    /* v8 ignore next 6 -- error is caught by Effect.catchAll */
                    (e) =>
                      new DatabaseError({
                        message: "Failed to upsert trace",
                        cause: e,
                      }),
                  ),
                );

              const spanData: NewSpan = {
                traceDbId: upsertedTrace.id,
                traceId: span.traceId,
                spanId: span.spanId,
                parentSpanId: span.parentSpanId ?? null,
                environmentId,
                projectId,
                organizationId,
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

              const insertedSpans: { id: string }[] = yield* client
                .insert(spans)
                .values(spanData)
                .onConflictDoNothing({
                  target: [spans.spanId, spans.traceId, spans.environmentId],
                })
                .returning({ id: spans.id })
                .pipe(
                  Effect.mapError(
                    /* v8 ignore next 6 -- error is caught by Effect.catchAll */
                    (e) =>
                      new DatabaseError({
                        message: "Failed to insert span",
                        cause: e,
                      }),
                  ),
                );

              return insertedSpans.length > 0;
            }).pipe(Effect.catchAll(() => Effect.succeed(false)));

            if (result) {
              acceptedSpans++;
            } else {
              rejectedSpans++;
            }
          }
        }
      }

      return { acceptedSpans, rejectedSpans };
    });
  }
}
