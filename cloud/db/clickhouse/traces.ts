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
 * This service lives under `cloud/db/clickhouse` to keep ClickHouse ingestion
 * logic grouped with ClickHouse services while still handling authorization
 * and ingestion orchestration for trace requests.
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
import {
  BaseAuthenticatedEffectService,
  type PermissionTable,
} from "@/db/base";
import { DrizzleORM } from "@/db/client";
import { ClickHouseSearch } from "@/db/clickhouse/search";
import { ProjectMemberships } from "@/db/project-memberships";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
  ImmutableResourceError,
} from "@/errors";
import {
  SpansIngestQueue,
  type SpansIngestMessage,
} from "@/workers/spanIngestQueue";
import type { ProjectRole } from "@/db/schema";
import type { ResourceSpans, KeyValue } from "@/api/traces.schemas";

/** Response type for trace creation. */
export type CreateTraceResponse = {
  acceptedSpans: number;
  rejectedSpans: number;
  acceptedSpanIds: string[];
};

/** Public trace representation. */
export type PublicTrace = {
  id: string;
  otelTraceId: string;
  environmentId: string;
  projectId: string;
  organizationId: string;
  serviceName: string | null;
  serviceVersion: string | null;
  resourceAttributes: Record<string, unknown> | null;
  createdAt: Date | null;
};

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
      const queueOption = yield* Effect.serviceOption(SpansIngestQueue);

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

      /* v8 ignore start -- Spans ingest queue is required in worker configuration */
      if (Option.isNone(queueOption)) {
        return yield* Effect.fail(
          new DatabaseError({
            message: "Spans ingest queue is required for trace ingestion.",
          }),
        );
      }
      /* v8 ignore stop */

      const queue = queueOption.value;

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

          const enqueued = yield* queue.send(message).pipe(
            Effect.as(true),
            Effect.catchAll(() => Effect.succeed(false)),
          );

          if (enqueued) {
            acceptedSpans += batch.length;
            for (const span of batch) {
              acceptedSpanIds.push(span.spanId);
            }
          } else {
            rejectedSpans += batch.length;
          }
        }
      }

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
      const clickHouseOption = yield* Effect.serviceOption(ClickHouseSearch);

      /* v8 ignore start -- ClickHouseSearch is required for trace reads */
      if (Option.isNone(clickHouseOption)) {
        return yield* Effect.fail(
          new DatabaseError({
            message: "ClickHouseSearch is required to list traces.",
          }),
        );
      }
      /* v8 ignore stop */

      const clickHouseSearch = clickHouseOption.value;

      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        traceId: "",
      });

      const endTime = new Date();
      const startTime = new Date(endTime.getTime() - 30 * 24 * 60 * 60 * 1000);

      const searchResult = yield* clickHouseSearch
        .search({
          environmentId,
          startTime,
          endTime,
          limit: 1000,
          offset: 0,
        })
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to list traces",
                cause: e,
              }),
          ),
        );

      const tracesById = new Map<string, PublicTrace>();
      for (const span of searchResult.spans) {
        if (!tracesById.has(span.traceId)) {
          tracesById.set(span.traceId, {
            id: span.traceId,
            otelTraceId: span.traceId,
            environmentId,
            projectId,
            organizationId,
            serviceName: null,
            serviceVersion: null,
            resourceAttributes: null,
            createdAt: new Date(span.startTime),
          });
        }
      }

      return Array.from(tracesById.values()).sort((a, b) => {
        const aTime = a.createdAt?.getTime() ?? 0;
        const bTime = b.createdAt?.getTime() ?? 0;
        return bTime - aTime;
      });
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
      const clickHouseOption = yield* Effect.serviceOption(ClickHouseSearch);

      /* v8 ignore start -- ClickHouseSearch is required for trace reads */
      if (Option.isNone(clickHouseOption)) {
        return yield* Effect.fail(
          new DatabaseError({
            message: "ClickHouseSearch is required to read traces.",
          }),
        );
      }
      /* v8 ignore stop */

      const clickHouseSearch = clickHouseOption.value;

      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        traceId,
      });

      const detail = yield* clickHouseSearch
        .getTraceDetail({ environmentId, traceId })
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to get trace",
                cause: e,
              }),
          ),
        );

      if (detail.spans.length === 0) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Trace ${traceId} not found`,
            resource: "traces",
          }),
        );
      }

      const firstSpan = detail.spans[0];
      let resourceAttributes: Record<string, unknown> | null = null;
      if (firstSpan?.resourceAttributes) {
        try {
          const parsed = JSON.parse(firstSpan.resourceAttributes) as unknown;
          if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
            resourceAttributes = parsed as Record<string, unknown>;
          }
        } catch {
          resourceAttributes = null;
        }
      }

      return {
        id: traceId,
        otelTraceId: traceId,
        environmentId,
        projectId,
        organizationId,
        serviceName: firstSpan?.serviceName ?? null,
        serviceVersion: firstSpan?.serviceVersion ?? null,
        resourceAttributes,
        createdAt: firstSpan?.startTime ? new Date(firstSpan.startTime) : null,
      };
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
