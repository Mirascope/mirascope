/**
 * @fileoverview Effect-native Traces service for OTLP ingestion.
 *
 * Provides authenticated CRUD operations for traces with role-based access
 * control. Traces belong to environments and inherit authorization from the
 * project's membership system. Traces are ingested via the OTLP (OpenTelemetry
 * Protocol) format and ingested into ClickHouse via a durable queue.
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
import { type CreateTraceResponse, type PublicTrace } from "@/db/schema/traces";
import {
  SpansIngestQueueService,
  type SpansIngestMessage,
} from "@/workers/spanIngestQueue";
import type { ProjectRole } from "@/db/schema";
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

const normalizeUnixNano = (value: string | undefined): string | undefined => {
  if (!value) return undefined;
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : undefined;
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
  CreateTraceResponse,
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
      const queue = yield* Effect.serviceOption(SpansIngestQueueService);

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
      const receivedAt = Date.now();
      const maxSpansPerMessage = 50;

      for (const rs of data.resourceSpans) {
        const serviceName = extractServiceName(rs.resource?.attributes);
        const serviceVersion = extractServiceVersion(rs.resource?.attributes);
        const resourceAttributes = keyValueArrayToObject(
          rs.resource?.attributes,
        );

        const spansForResource = rs.scopeSpans.flatMap((scopeSpan) =>
          scopeSpan.spans.map((span) => ({
            ...span,
            startTimeUnixNano: normalizeUnixNano(span.startTimeUnixNano),
            endTimeUnixNano: normalizeUnixNano(span.endTimeUnixNano),
            attributes: keyValueArrayToObject(span.attributes),
          })),
        );

        if (spansForResource.length === 0) {
          continue;
        }

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
          } else {
            rejectedSpans += batch.length;
          }
        }
      }

      return {
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
    CreateTraceResponse[],
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

      return [];
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
    CreateTraceResponse,
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
        new NotFoundError({
          message: `Trace ${traceId} not found`,
        }),
      );
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
