/**
 * @fileoverview Effect-native Traces service for OTLP ingestion.
 *
 * Provides authenticated CRUD operations for traces with role-based access
 * control. Traces belong to environments and inherit authorization from the
 * project's membership system. Traces are ingested via the OTLP
 * (OpenTelemetry Protocol) format and ingested into ClickHouse via a durable
 * queue.
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
 * - Enqueues spans for ClickHouse ingestion
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

import { Effect, Option } from "effect";
import { and, desc, eq } from "drizzle-orm";
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
  type CreateTraceResponse,
  type PublicTrace,
} from "@/db/schema/traces";
import { spans } from "@/db/schema/spans";
import { organizations, type ProjectRole } from "@/db/schema";
import {
  SpansIngestQueue,
  type SpansIngestMessage,
} from "@/workers/spanIngestQueue";
import {
  SpansMeteringQueueService,
  type SpanMeteringMessage,
} from "@/workers/spansMeteringQueue";
import type { ResourceSpans, KeyValue } from "@/api/traces.schemas";

export type { CreateTraceResponse, PublicTrace };

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

/**
 * Chunk spans into fixed-size batches for queue ingestion.
 */
const chunkSpans = <T>(spans: readonly T[], size: number): T[][] => {
  if (spans.length <= size) return [spans.slice()];
  const chunks: T[][] = [];
  for (let i = 0; i < spans.length; i += size) {
    chunks.push(spans.slice(i, i + size));
  }
  return chunks;
};

/**
 * Normalize Unix nanosecond timestamp string.
 *
 * Returns null for empty or missing values to enable filtering of incomplete spans.
 */
const normalizeUnixNano = (value: string | undefined): string | null => {
  if (!value) return null;
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : null;
};

/**
 * Builds a stable metering identifier for a span.
 */
const buildMeteringSpanId = (traceId: string, spanId: string): string =>
  `${traceId}:${spanId}`;

/**
 * Enqueues span metering messages for accepted spans.
 *
 * Fetches the organization's Stripe customer ID and enqueues a metering
 * message for each accepted span. Errors are logged but don't fail the
 * trace creation - eventual consistency via reconciliation is acceptable.
 */
export const enqueueSpanMetering = (
  spanIds: string[],
  organizationId: string,
  projectId: string,
  environmentId: string,
): Effect.Effect<void, never, DrizzleORM> =>
  Effect.gen(function* () {
    if (spanIds.length === 0) {
      return;
    }

    const queue = yield* Effect.serviceOption(SpansMeteringQueueService);
    /* v8 ignore start - Early return when queue not provided */
    if (Option.isNone(queue)) {
      return;
    }
    /* v8 ignore stop */

    const client = yield* DrizzleORM;

    // Fetch organization to get stripe customer ID
    const [org] = yield* client
      .select({ stripeCustomerId: organizations.stripeCustomerId })
      .from(organizations)
      .where(eq(organizations.id, organizationId))
      .pipe(
        Effect.catchAll((error) => {
          console.error(
            `[traces] Failed to fetch organization ${organizationId} for span metering:`,
            error,
          );
          return Effect.succeed([]);
        }),
      );

    if (!org) {
      console.error(
        `[traces] Organization ${organizationId} not found for span metering`,
      );
      return;
    }

    const timestamp = Date.now();

    // Enqueue metering message for each accepted span
    for (const spanId of spanIds) {
      const message: SpanMeteringMessage = {
        spanId,
        organizationId,
        projectId,
        environmentId,
        stripeCustomerId: org.stripeCustomerId,
        timestamp,
      };

      yield* queue.value.send(message).pipe(
        Effect.catchAll((error) => {
          console.error(
            `[traces] Failed to enqueue span metering for span ${spanId}:`,
            error,
          );
          return Effect.void;
        }),
      );
    }
  });

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
  PublicTrace | CreateTraceResponse,
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
   * Spans are enqueued for asynchronous ingestion into ClickHouse.
   * Accepted/rejected counts are based on queue enqueue success.
   * Accepted spans are metered when the spans metering queue is available.
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
      const queue = yield* Effect.serviceOption(SpansIngestQueue);

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
      const acceptedSpanIds: string[] = [];
      const receivedAt = Date.now();
      const maxSpansPerMessage = 50;

      for (const resourceSpan of data.resourceSpans) {
        const serviceName = extractServiceName(
          resourceSpan.resource?.attributes,
        );
        const serviceVersion = extractServiceVersion(
          resourceSpan.resource?.attributes,
        );
        const resourceAttributes = keyValueArrayToObject(
          resourceSpan.resource?.attributes,
        );

        // Transform and filter spans: only accept completed spans with both timestamps
        const allSpans = resourceSpan.scopeSpans.flatMap((scopeSpan) =>
          scopeSpan.spans.map((span) => {
            const startTimeUnixNano = normalizeUnixNano(span.startTimeUnixNano);
            const endTimeUnixNano = normalizeUnixNano(span.endTimeUnixNano);
            return {
              ...span,
              startTimeUnixNano,
              endTimeUnixNano,
              attributes: keyValueArrayToObject(span.attributes),
            };
          }),
        );

        // Separate completed spans from incomplete ones
        const completedSpans = allSpans.filter(
          (
            span,
          ): span is typeof span & {
            startTimeUnixNano: string;
            endTimeUnixNano: string;
          } => span.startTimeUnixNano !== null && span.endTimeUnixNano !== null,
        );
        const incompleteCount = allSpans.length - completedSpans.length;
        rejectedSpans += incompleteCount;

        if (completedSpans.length === 0) {
          continue;
        }

        const spansForResource = completedSpans;

        // Insert into PostgreSQL for annotations FK support
        for (const span of spansForResource) {
          // Upsert trace record
          const existingTrace = yield* client
            .select({ id: traces.id })
            .from(traces)
            .where(
              and(
                eq(traces.otelTraceId, span.traceId),
                eq(traces.environmentId, environmentId),
              ),
            )
            .limit(1)
            .pipe(
              /* v8 ignore start - Database error handling */
              Effect.mapError(
                (e) =>
                  new DatabaseError({
                    message: "Failed to query trace",
                    cause: e,
                  }),
              ),
              /* v8 ignore stop */
            );

          let traceDbId: string;
          if (existingTrace.length > 0 && existingTrace[0]?.id) {
            traceDbId = existingTrace[0].id;
          } else {
            const [newTrace] = yield* client
              .insert(traces)
              .values({
                otelTraceId: span.traceId,
                environmentId,
                projectId,
                organizationId,
                serviceName,
                serviceVersion,
                resourceAttributes,
              })
              .returning({ id: traces.id })
              .pipe(
                /* v8 ignore start - Database error handling */
                Effect.mapError(
                  (e) =>
                    new DatabaseError({
                      message: "Failed to insert trace",
                      cause: e,
                    }),
                ),
                /* v8 ignore stop */
              );
            /* v8 ignore start - Edge case: trace insert returns empty result */
            if (!newTrace?.id) {
              rejectedSpans++;
              continue;
            }
            /* v8 ignore stop */
            traceDbId = newTrace.id;
          }

          // Upsert span record
          yield* client
            .insert(spans)
            .values({
              traceId: traceDbId,
              otelTraceId: span.traceId,
              otelSpanId: span.spanId,
              parentSpanId: span.parentSpanId ?? null,
              environmentId,
              projectId,
              organizationId,
              name: span.name,
              kind: span.kind ?? null,
              startTimeUnixNano: BigInt(span.startTimeUnixNano),
              endTimeUnixNano: BigInt(span.endTimeUnixNano),
              attributes: span.attributes ?? {},
              status: span.status ?? {},
              events: span.events ?? [],
              links: span.links ?? [],
              droppedAttributesCount: span.droppedAttributesCount ?? null,
              droppedEventsCount: span.droppedEventsCount ?? null,
              droppedLinksCount: span.droppedLinksCount ?? null,
            })
            .onConflictDoNothing({
              target: [
                spans.otelSpanId,
                spans.otelTraceId,
                spans.environmentId,
              ],
            })
            .pipe(
              /* v8 ignore start - Database error handling */
              Effect.mapError(
                (e) =>
                  new DatabaseError({
                    message: "Failed to insert span",
                    cause: e,
                  }),
              ),
              /* v8 ignore stop */
            );
        }

        // Send to ClickHouse queue for analytics
        const batches = chunkSpans(spansForResource, maxSpansPerMessage);

        for (const batch of batches) {
          const message: SpansIngestMessage = {
            environmentId,
            projectId,
            organizationId,
            receivedAt,
            serviceName,
            serviceVersion,
            resourceAttributes,
            spans: batch,
          };

          const enqueued = yield* Option.match(queue, {
            onNone: () => Effect.succeed(false),
            onSome: (service) =>
              service.send(message).pipe(
                Effect.as(true),
                Effect.catchAll(() => Effect.succeed(false)),
              ),
          });

          if (enqueued) {
            acceptedSpans += batch.length;
            for (const span of batch) {
              acceptedSpanIds.push(
                buildMeteringSpanId(span.traceId, span.spanId),
              );
            }
          } else {
            rejectedSpans += batch.length;
          }
        }
      }

      yield* enqueueSpanMetering(
        acceptedSpanIds,
        organizationId,
        projectId,
        environmentId,
      );

      return {
        acceptedSpans,
        rejectedSpans,
        acceptedSpanIds,
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
        .orderBy(desc(traces.createdAt))
        .pipe(
          /* v8 ignore start - Database error handling */
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to list traces",
                cause: e,
              }),
          ),
          /* v8 ignore stop */
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
          /* v8 ignore start - Database error handling */
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to get trace",
                cause: e,
              }),
          ),
          /* v8 ignore stop */
        );

      if (!row) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Trace ${traceId} not found`,
            resource: "traces",
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
    CreateTraceResponse,
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
   * Note: Trace deletion is not currently supported. Traces are stored in
   * ClickHouse and deletion has not been implemented. This method always
   * returns NotFoundError after authorization check.
   *
   * Requires ADMIN role on the project.
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment containing the trace
   * @param args.traceId - The trace to delete
   * @throws NotFoundError - Always (deletion not supported)
   * @throws PermissionDeniedError - If the user lacks delete permission
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
      yield* this.authorize({
        userId,
        action: "delete",
        organizationId,
        projectId,
        environmentId,
        traceId,
      });

      return yield* Effect.fail(
        new NotFoundError({
          message: `Trace ${traceId} not found`,
          resource: "trace",
        }),
      );
    });
  }
}
