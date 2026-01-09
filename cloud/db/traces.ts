/**
 * @fileoverview Effect-native Traces service for OTLP ingestion.
 *
 * Provides authenticated CRUD operations for traces with role-based access
 * control. Traces belong to environments and inherit authorization from the
 * project's membership system. Traces are ingested via the OTLP (OpenTelemetry
 * Protocol) format and stored with their associated spans.
 *
 * ## Architecture
 *
 * ```
 * Traces (authenticated)
 *   └── authorization via ProjectMemberships.getRole()
 * ```
 *
 * ## Trace Roles
 *
 * Traces use the project's role system:
 * - `ADMIN` - Full trace management (create, read, delete)
 * - `DEVELOPER` - Can create and read traces
 * - `VIEWER` - Read-only access to traces
 * - `ANNOTATOR` - Read-only access to traces
 *
 * Note: Traces are immutable and cannot be updated once created.
 *
 * ## Implicit Access
 *
 * Organization OWNER and ADMIN roles have implicit ADMIN access to all projects
 * (and thus all environments and traces) within their organization.
 *
 * ## OTLP Ingestion
 *
 * The `create` method accepts OTLP ResourceSpans format and:
 * - Upserts traces based on traceId + environmentId
 * - Inserts spans with conflict handling (duplicates are rejected)
 * - Returns ingestion statistics (acceptedSpans, rejectedSpans)
 *
 * @example
 * ```ts
 * const db = yield* Database;
 *
 * // Ingest OTLP traces
 * const result = yield* db.organizations.projects.environments.traces.create({
 *   userId: "user-123",
 *   organizationId: "org-456",
 *   projectId: "proj-789",
 *   environmentId: "env-012",
 *   data: { resourceSpans: [...] },
 * });
 * console.log(`Accepted: ${result.acceptedSpans}, Rejected: ${result.rejectedSpans}`);
 *
 * // List traces in an environment
 * const traces = yield* db.organizations.projects.environments.traces.findAll({
 *   userId: "user-123",
 *   organizationId: "org-456",
 *   projectId: "proj-789",
 *   environmentId: "env-012",
 * });
 * ```
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
  ImmutableResourceError,
} from "@/errors";
import {
  traces,
  type NewTrace,
  type PublicTrace,
  type CreateTraceResponse,
} from "@/db/schema/traces";
import { spans, type NewSpan } from "@/db/schema/spans";
import { spansOutbox } from "@/db/schema/spansOutbox";
import type { ProjectRole } from "@/db/schema";
import type { ResourceSpans, KeyValue } from "@/api/traces.schemas";

export type { PublicTrace, CreateTraceResponse };

/** Input type for trace ingestion via OTLP format. */
export type TraceCreateInput = {
  resourceSpans: readonly ResourceSpans[];
};

/** OTLP value type extracted from KeyValue. */
export type OTLPValue = KeyValue["value"];

// =============================================================================
// OTLP Utilities
// =============================================================================

/**
 * Convert an OTLP value to a plain JSON value.
 */
function convertOTLPValue(value: OTLPValue): unknown {
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
    return value.arrayValue.values.map((item: unknown) => {
      if (typeof item === "object" && item !== null) {
        return convertOTLPValue(item as OTLPValue);
      }
      return item;
    });
  }
  if (value.kvlistValue !== undefined) {
    const result: Record<string, unknown> = {};
    for (const kv of value.kvlistValue.values) {
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
 * Convert an OTLP KeyValue array to a plain JSON object.
 */
function keyValueArrayToObject(
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
 * Extract service name from resource attributes.
 */
function extractServiceName(
  attributes: readonly KeyValue[] | undefined,
): string | null {
  const attr = attributes?.find((a) => a.key === "service.name");
  return attr?.value?.stringValue ?? null;
}

/**
 * Extract service version from resource attributes.
 */
function extractServiceVersion(
  attributes: readonly KeyValue[] | undefined,
): string | null {
  const attr = attributes?.find((a) => a.key === "service.version");
  return attr?.value?.stringValue ?? null;
}

// =============================================================================
// Traces Service
// =============================================================================

type TracePath =
  "organizations/:organizationId/projects/:projectId/environments/:environmentId/traces/:traceId";

/**
 * Effect-native Traces service.
 *
 * Provides CRUD operations with role-based access control for traces.
 * Authorization is inherited from project membership via ProjectMemberships.getRole().
 *
 * ## Permission Matrix
 *
 * | Action   | ADMIN | DEVELOPER | VIEWER | ANNOTATOR |
 * |----------|-------|-----------|--------|-----------|
 * | create   | ✓     | ✓         | ✗      | ✗         |
 * | read     | ✓     | ✓         | ✓      | ✓         |
 * | update   | ✗     | ✗         | ✗      | ✗         |
 * | delete   | ✓     | ✗         | ✗      | ✗         |
 *
 * Note: Traces are immutable - update always fails with PermissionDeniedError.
 *
 * ## Security Model
 *
 * - Org OWNER/ADMIN have implicit project ADMIN access (and thus trace access)
 * - Non-members cannot see that an environment/trace exists (returns NotFoundError)
 * - Traces are ingested via OTLP format with upsert semantics
 * - Spans are inserted with conflict handling (duplicates are rejected)
 */
export class Traces extends BaseAuthenticatedEffectService<
  PublicTrace,
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

  // ---------------------------------------------------------------------------
  // Base Implementation
  // ---------------------------------------------------------------------------

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

  // ---------------------------------------------------------------------------
  // Role Resolution
  // ---------------------------------------------------------------------------

  /**
   * Determines the user's effective role for a trace.
   *
   * Delegates to `ProjectMemberships.getRole` which handles:
   * - Org OWNER → treated as project ADMIN
   * - Org ADMIN → treated as project ADMIN
   * - Explicit project membership role
   * - No access → NotFoundError (hides trace existence)
   */
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

  // ---------------------------------------------------------------------------
  // CRUD Operations
  // ---------------------------------------------------------------------------

  /**
   * Ingests OTLP traces and spans into the database.
   *
   * Requires ADMIN or DEVELOPER role on the project.
   * Traces are upserted based on traceId + environmentId.
   * Spans are inserted with conflict handling - duplicates are rejected.
   *
   * @param args.userId - The user ingesting the traces
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment to ingest traces into
   * @param args.data - OTLP ResourceSpans data
   * @returns Trace info with ingestion statistics (acceptedSpans, rejectedSpans)
   * @throws PermissionDeniedError - If user lacks create permission
   * @throws NotFoundError - If the environment doesn't exist or user lacks access
   * @throws DatabaseError - If the database operation fails
   */
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
    CreateTraceResponse,
    AlreadyExistsError | NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "create",
        organizationId,
        projectId,
        environmentId,
        traceId: "", // Not used for create
      });

      // Process OTLP resource spans
      let acceptedSpans = 0;
      let rejectedSpans = 0;
      let firstTrace: PublicTrace | null = null;

      for (const rs of data.resourceSpans) {
        const serviceName = extractServiceName(rs.resource?.attributes);
        const serviceVersion = extractServiceVersion(rs.resource?.attributes);
        const resourceAttributes = keyValueArrayToObject(
          rs.resource?.attributes,
        );

        for (const scopeSpan of rs.scopeSpans) {
          for (const span of scopeSpan.spans) {
            const result = yield* Effect.gen(function* () {
              const traceData: NewTrace = {
                otelTraceId: span.traceId,
                environmentId,
                projectId,
                organizationId,
                serviceName,
                serviceVersion,
                resourceAttributes,
              };

              // Upsert the trace
              const [upsertedTrace] = yield* client
                .insert(traces)
                .values(traceData)
                .onConflictDoUpdate({
                  target: [traces.otelTraceId, traces.environmentId],
                  set: {
                    serviceName: traceData.serviceName,
                    serviceVersion: traceData.serviceVersion,
                    resourceAttributes: traceData.resourceAttributes,
                  },
                })
                .returning()
                .pipe(
                  Effect.mapError(
                    (e) =>
                      new DatabaseError({
                        message: "Failed to upsert trace",
                        cause: e,
                      }),
                  ),
                );

              if (!firstTrace && upsertedTrace) {
                firstTrace = upsertedTrace;
              }

              const spanData: NewSpan = {
                traceId: upsertedTrace.id,
                otelTraceId: span.traceId,
                otelSpanId: span.spanId,
                parentSpanId: span.parentSpanId,
                environmentId,
                projectId,
                organizationId,
                name: span.name,
                kind: span.kind,
                startTimeUnixNano: span.startTimeUnixNano
                  ? BigInt(span.startTimeUnixNano)
                  : null,
                endTimeUnixNano: span.endTimeUnixNano
                  ? BigInt(span.endTimeUnixNano)
                  : null,
                attributes: keyValueArrayToObject(span.attributes),
                status: span.status,
                events: span.events,
                links: span.links,
                droppedAttributesCount: span.droppedAttributesCount,
                droppedEventsCount: span.droppedEventsCount,
                droppedLinksCount: span.droppedLinksCount,
              };

              // Insert the span
              const insertedSpans = yield* client
                .insert(spans)
                .values(spanData)
                .onConflictDoNothing({
                  target: [
                    spans.otelSpanId,
                    spans.otelTraceId,
                    spans.environmentId,
                  ],
                })
                .returning({ id: spans.id })
                .pipe(
                  Effect.mapError(
                    (e) =>
                      new DatabaseError({
                        message: "Failed to insert span",
                        cause: e,
                      }),
                  ),
                );

              // Write to outbox for ClickHouse sync (all inserted spans).
              // This is intentionally not wrapped in a transaction so that
              // a failed outbox write does not roll back the span insert.
              // If the outbox insert fails we mark the span as rejected below.
              if (insertedSpans.length > 0) {
                const outboxRows = insertedSpans.map((s) => ({
                  spanId: s.id,
                  operation: "INSERT" as const,
                }));
                yield* client
                  .insert(spansOutbox)
                  .values(outboxRows)
                  .onConflictDoNothing({
                    target: [spansOutbox.spanId, spansOutbox.operation],
                  })
                  .pipe(
                    Effect.mapError(
                      (e) =>
                        new DatabaseError({
                          message: "Failed to write to outbox",
                          cause: e,
                        }),
                    ),
                  );
              }

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

      // Return first trace info with ingestion stats
      const traceInfo: PublicTrace = firstTrace ?? {
        id: "",
        otelTraceId: "",
        environmentId,
        projectId,
        organizationId,
        serviceName: null,
        serviceVersion: null,
        resourceAttributes: null,
        createdAt: null,
      };

      return {
        ...traceInfo,
        acceptedSpans,
        rejectedSpans,
      };
    });
  }

  /**
   * Retrieves all traces in an environment.
   *
   * Requires any role on the project (ADMIN, DEVELOPER, VIEWER, or ANNOTATOR).
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment to list traces for
   * @returns Array of traces in the environment
   * @throws NotFoundError - If the environment doesn't exist or user lacks access
   * @throws PermissionDeniedError - If the user lacks read permission
   * @throws DatabaseError - If the database query fails
   */
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
    PublicTrace[],
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        traceId: "",
      });

      return yield* client
        .select()
        .from(traces)
        .where(eq(traces.environmentId, environmentId))
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to list traces",
                cause: e,
              }),
          ),
        );
    });
  }

  /**
   * Retrieves a trace by ID.
   *
   * Requires any role on the project (ADMIN, DEVELOPER, VIEWER, or ANNOTATOR).
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment containing the trace
   * @param args.traceId - The trace to retrieve
   * @returns The trace
   * @throws NotFoundError - If the trace doesn't exist or user lacks access
   * @throws PermissionDeniedError - If the user lacks read permission
   * @throws DatabaseError - If the database query fails
   */
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
    PublicTrace,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        traceId,
      });

      const [row] = yield* client
        .select()
        .from(traces)
        .where(
          and(
            eq(traces.otelTraceId, traceId),
            eq(traces.environmentId, environmentId),
          ),
        )
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to get trace",
                cause: e,
              }),
          ),
        );

      if (!row) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Trace ${traceId} not found`,
          }),
        );
      }

      return row;
    });
  }

  /**
   * Updates a trace (not supported - traces are immutable).
   *
   * Always fails with PermissionDeniedError because traces cannot be modified
   * after creation.
   *
   * @throws PermissionDeniedError - Always (traces are immutable)
   */
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
    PublicTrace,
    | NotFoundError
    | PermissionDeniedError
    | ImmutableResourceError
    | DatabaseError,
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
        new ImmutableResourceError({
          message: "Traces are immutable and cannot be updated.",
          resource: "traces",
        }),
      );
    });
  }

  /**
   * Deletes a trace and all associated spans.
   *
   * Requires ADMIN role on the project.
   * Deletion is performed atomically in a transaction.
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment containing the trace
   * @param args.traceId - The trace to delete
   * @throws NotFoundError - If the trace doesn't exist
   * @throws PermissionDeniedError - If the user lacks delete permission
   * @throws DatabaseError - If the database operation fails
   */
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
      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "delete",
        organizationId,
        projectId,
        environmentId,
        traceId,
      });

      // Use transaction to ensure spans and trace are deleted atomically
      yield* client.withTransaction(
        Effect.gen(function* () {
          // Delete spans first (foreign key constraint)
          yield* client
            .delete(spans)
            .where(
              and(
                eq(spans.otelTraceId, traceId),
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

          // Delete the trace
          const [row] = yield* client
            .delete(traces)
            .where(
              and(
                eq(traces.otelTraceId, traceId),
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

          if (!row) {
            return yield* Effect.fail(
              new NotFoundError({
                message: `Trace ${traceId} not found`,
                resource: "trace",
              }),
            );
          }
        }),
      );
    });
  }
}
