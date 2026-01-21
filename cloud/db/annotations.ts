/**
 * @fileoverview Effect-native Annotations service for span annotations.
 *
 * Provides authenticated CRUD operations for annotations with role-based access
 * control. Annotations belong to environments and inherit authorization from the
 * project's membership system.
 *
 * ## Architecture
 *
 * ```
 * Annotations (authenticated)
 *   └── authorization via ProjectMemberships.getRole()
 * ```
 *
 * ## Annotation Roles
 *
 * Annotations use the project's role system:
 * - `ADMIN` - Full annotation management (create, read, update, delete)
 * - `DEVELOPER` - Can create, read, and update annotations
 * - `VIEWER` - Read-only access to annotations
 * - `ANNOTATOR` - Can create, read, and update annotations
 *
 * ## Implicit Access
 *
 * Organization OWNER and ADMIN roles have implicit ADMIN access to all projects
 * (and thus all environments and annotations) within their organization.
 *
 * @example
 * ```ts
 * const db = yield* Database;
 *
 * // Create an annotation for a span
 * const annotation = yield* db.organizations.projects.environments.traces.annotations.create({
 *   userId: "user-123",
 *   organizationId: "org-456",
 *   projectId: "proj-789",
 *   environmentId: "env-012",
 *   data: {
 *     otelSpanId: "abc123",
 *     otelTraceId: "def456",
 *     label: "pass",
 *     reasoning: "Response was accurate",
 *   },
 * });
 *
 * // List annotations in an environment
 * const annotations = yield* db.organizations.projects.environments.traces.annotations.findAll({
 *   userId: "user-123",
 *   organizationId: "org-456",
 *   projectId: "proj-789",
 *   environmentId: "env-012",
 * });
 * ```
 */

import { Effect } from "effect";
import { and, eq, desc } from "drizzle-orm";
import {
  BaseAuthenticatedEffectService,
  type PermissionTable,
} from "@/db/base";
import { DrizzleORM } from "@/db/client";
import { ProjectMemberships } from "@/db/project-memberships";
import { Tags } from "@/db/tags";
import { ClickHouseSearch } from "@/db/clickhouse/search";
import { RealtimeSpans } from "@/workers/realtimeSpans";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/errors";
import {
  annotations,
  type NewAnnotation,
  type PublicAnnotation,
} from "@/db/schema/annotations";
import type { ProjectRole } from "@/db/schema";
import { isUniqueConstraintError } from "@/db/utils";

// =============================================================================
// Types
// =============================================================================

/**
 * Filters for listing annotations.
 */
export type AnnotationFilters = {
  otelTraceId?: string;
  otelSpanId?: string;
  label?: "pass" | "fail";
  limit?: number;
  offset?: number;
};

// =============================================================================
// Helpers
// =============================================================================

/**
 * Checks whether a span exists using realtime cache first, then ClickHouse.
 *
 * Checks RealtimeSpans cache first for fast lookups of recent spans,
 * then falls back to ClickHouse (source of truth) if not found.
 */
const checkSpanExists = ({
  environmentId,
  traceId,
  spanId,
}: {
  environmentId: string;
  traceId: string;
  spanId: string;
}): Effect.Effect<boolean, DatabaseError, ClickHouseSearch | RealtimeSpans> =>
  Effect.gen(function* () {
    const realtimeSpans = yield* RealtimeSpans;
    const clickHouseSearch = yield* ClickHouseSearch;

    // Check realtime cache first (fast path for recent spans)
    const realtimeExists = yield* realtimeSpans
      .exists({ environmentId, traceId, spanId })
      .pipe(Effect.catchAll(() => Effect.succeed(false)));

    if (realtimeExists) {
      return true;
    }

    // Fall back to ClickHouse (source of truth)
    return yield* clickHouseSearch
      .getTraceDetail({ environmentId, traceId })
      .pipe(
        Effect.map((detail) =>
          detail.spans.some((span) => span.spanId === spanId),
        ),
        Effect.catchAll(() => Effect.succeed(false)),
      );
  });

// =============================================================================
// Annotations Service
// =============================================================================

export type AnnotationCreateData = Pick<
  NewAnnotation,
  "otelSpanId" | "otelTraceId" | "label" | "reasoning" | "metadata" | "tags"
>;

/**
 * Effect-native Annotations service.
 *
 * Provides CRUD operations with role-based access control for annotations.
 * Authorization is inherited from project membership via ProjectMemberships.getRole().
 *
 * ## Permission Matrix
 *
 * | Action   | ADMIN | DEVELOPER | VIEWER | ANNOTATOR |
 * |----------|-------|-----------|--------|-----------|
 * | create   | ✓     | ✓         | ✗      | ✓         |
 * | read     | ✓     | ✓         | ✓      | ✓         |
 * | update   | ✓     | ✓         | ✗      | ✓         |
 * | delete   | ✓     | ✗         | ✗      | ✗         |
 *
 * ## Security Model
 *
 * - Org OWNER/ADMIN have implicit project ADMIN access (and thus annotation access)
 * - Non-members cannot see that an environment/annotation exists (returns NotFoundError)
 * - Annotations are linked to spans via OTLP span/trace IDs
 */
export class Annotations extends BaseAuthenticatedEffectService<
  PublicAnnotation,
  "organizations/:organizationId/projects/:projectId/environments/:environmentId/annotations/:annotationId",
  AnnotationCreateData,
  Partial<Pick<NewAnnotation, "label" | "reasoning" | "metadata" | "tags">>,
  ProjectRole,
  ClickHouseSearch | RealtimeSpans
> {
  private readonly projectMemberships: ProjectMemberships;
  private readonly tags: Tags;

  constructor(projectMemberships: ProjectMemberships, tags: Tags) {
    super();
    this.projectMemberships = projectMemberships;
    this.tags = tags;
  }

  // ---------------------------------------------------------------------------
  // Base Implementation
  // ---------------------------------------------------------------------------

  protected getResourceName(): string {
    return "annotation";
  }

  protected getPermissionTable(): PermissionTable<ProjectRole> {
    return {
      create: ["ADMIN", "DEVELOPER", "ANNOTATOR"],
      read: ["ADMIN", "DEVELOPER", "VIEWER", "ANNOTATOR"],
      update: ["ADMIN", "DEVELOPER", "ANNOTATOR"],
      delete: ["ADMIN"],
    };
  }

  // ---------------------------------------------------------------------------
  // Role Resolution
  // ---------------------------------------------------------------------------

  /**
   * Determines the user's effective role for an annotation.
   *
   * Delegates to `ProjectMemberships.getRole` which handles:
   * - Org OWNER → treated as project ADMIN
   * - Org ADMIN → treated as project ADMIN
   * - Explicit project membership role
   * - No access → NotFoundError (hides annotation existence)
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
    annotationId?: string;
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
   * Creates an annotation for a span.
   *
   * Requires ADMIN, DEVELOPER, or ANNOTATOR role on the project.
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment containing the span
   * @param args.data - The annotation data
   * @returns The created annotation
   * @throws NotFoundError - If the span doesn't exist or user lacks access
   * @throws AlreadyExistsError - If an annotation already exists for this span
   * @throws PermissionDeniedError - If the user lacks create permission
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
    data: AnnotationCreateData;
  }): Effect.Effect<
    PublicAnnotation,
    AlreadyExistsError | NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM | ClickHouseSearch | RealtimeSpans
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "create",
        organizationId,
        projectId,
        environmentId,
        annotationId: "",
      });

      const spanExists = yield* checkSpanExists({
        environmentId,
        traceId: data.otelTraceId,
        spanId: data.otelSpanId,
      });

      if (!spanExists) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Span with otelSpanId=${data.otelSpanId}, otelTraceId=${data.otelTraceId} not found`,
            resource: "span",
          }),
        );
      }

      if (data.tags) {
        yield* this.tags.findByNames({
          userId,
          organizationId,
          projectId,
          names: data.tags,
        });
      }

      const newAnnotation: NewAnnotation = {
        otelSpanId: data.otelSpanId,
        otelTraceId: data.otelTraceId,
        label: data.label ?? null,
        reasoning: data.reasoning ?? null,
        metadata: data.metadata ?? null,
        tags: data.tags ?? null,
        environmentId,
        projectId,
        organizationId,
        createdBy: userId,
      };

      const result: PublicAnnotation[] = yield* client
        .insert(annotations)
        .values(newAnnotation)
        .returning()
        .pipe(
          Effect.mapError((e) => {
            if (isUniqueConstraintError(e)) {
              return new AlreadyExistsError({
                message: `Annotation for span ${data.otelSpanId} already exists`,
                resource: "annotation",
              });
            }
            return new DatabaseError({
              message: "Failed to create annotation",
              cause: e,
            });
          }),
        );

      const [row] = result;
      return row;
    });
  }

  /**
   * Retrieves all annotations in an environment with optional filters.
   *
   * Requires any role on the project (ADMIN, DEVELOPER, VIEWER, or ANNOTATOR).
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment to list annotations for
   * @param args.filters - Optional filters for the query
   * @returns Array of annotations
   * @throws NotFoundError - If the environment doesn't exist or user lacks access
   * @throws PermissionDeniedError - If the user lacks read permission
   * @throws DatabaseError - If the database query fails
   */
  findAll({
    userId,
    organizationId,
    projectId,
    environmentId,
    filters,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    filters?: AnnotationFilters;
  }): Effect.Effect<
    PublicAnnotation[],
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
        annotationId: "",
      });

      const conditions = [eq(annotations.environmentId, environmentId)];

      if (filters?.otelTraceId) {
        conditions.push(eq(annotations.otelTraceId, filters.otelTraceId));
      }

      if (filters?.otelSpanId) {
        conditions.push(eq(annotations.otelSpanId, filters.otelSpanId));
      }

      if (filters?.label) {
        conditions.push(eq(annotations.label, filters.label));
      }

      const whereClause = and(...conditions);

      let query = client
        .select()
        .from(annotations)
        .where(whereClause)
        .orderBy(desc(annotations.createdAt));

      if (filters?.limit) {
        query = query.limit(filters.limit) as typeof query;
      }

      if (filters?.offset) {
        query = query.offset(filters.offset) as typeof query;
      }

      const results: PublicAnnotation[] = yield* query.pipe(
        Effect.mapError(
          (e) =>
            new DatabaseError({
              message: "Failed to list annotations",
              cause: e,
            }),
        ),
      );

      return results;
    });
  }

  /**
   * Retrieves an annotation by ID.
   *
   * Requires any role on the project (ADMIN, DEVELOPER, VIEWER, or ANNOTATOR).
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment containing the annotation
   * @param args.annotationId - The annotation to retrieve
   * @returns The annotation
   * @throws NotFoundError - If the annotation doesn't exist or user lacks access
   * @throws PermissionDeniedError - If the user lacks read permission
   * @throws DatabaseError - If the database query fails
   */
  findById({
    userId,
    organizationId,
    projectId,
    environmentId,
    annotationId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    annotationId: string;
  }): Effect.Effect<
    PublicAnnotation,
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
        annotationId,
      });

      const result: PublicAnnotation[] = yield* client
        .select()
        .from(annotations)
        .where(
          and(
            eq(annotations.id, annotationId),
            eq(annotations.environmentId, environmentId),
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to get annotation",
                cause: e,
              }),
          ),
        );

      const [row] = result;
      if (!row) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Annotation with id ${annotationId} not found`,
            resource: "annotation",
          }),
        );
      }

      return row;
    });
  }

  /**
   * Updates an annotation.
   *
   * Requires ADMIN, DEVELOPER, or ANNOTATOR role on the project.
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment containing the annotation
   * @param args.annotationId - The annotation to update
   * @param args.data - The update data
   * @returns The updated annotation
   * @throws NotFoundError - If the annotation doesn't exist or user lacks access
   * @throws PermissionDeniedError - If the user lacks update permission
   * @throws DatabaseError - If the database operation fails
   */
  update({
    userId,
    organizationId,
    projectId,
    environmentId,
    annotationId,
    data,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    annotationId: string;
    data: Partial<
      Pick<NewAnnotation, "label" | "reasoning" | "metadata" | "tags">
    >;
  }): Effect.Effect<
    PublicAnnotation,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      yield* this.authorize({
        userId,
        action: "update",
        organizationId,
        projectId,
        environmentId,
        annotationId,
      });

      const updateData: Partial<NewAnnotation> = {
        updatedAt: new Date(),
      };

      if (data.label !== undefined) {
        updateData.label = data.label;
      }
      if (data.reasoning !== undefined) {
        updateData.reasoning = data.reasoning;
      }
      if (data.metadata !== undefined) {
        updateData.metadata = data.metadata;
      }
      if (data.tags) {
        yield* this.tags.findByNames({
          userId,
          organizationId,
          projectId,
          names: data.tags,
        });
        updateData.tags = data.tags;
      } else if (data.tags === null) {
        updateData.tags = null;
      }

      const result: PublicAnnotation[] = yield* client
        .update(annotations)
        .set(updateData)
        .where(
          and(
            eq(annotations.id, annotationId),
            eq(annotations.environmentId, environmentId),
          ),
        )
        .returning()
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to update annotation",
                cause: e,
              }),
          ),
        );

      const [row] = result;
      if (!row) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Annotation with id ${annotationId} not found`,
            resource: "annotation",
          }),
        );
      }

      return row;
    });
  }

  /**
   * Deletes an annotation.
   *
   * Requires ADMIN role on the project.
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment containing the annotation
   * @param args.annotationId - The annotation to delete
   * @throws NotFoundError - If the annotation doesn't exist or user lacks access
   * @throws PermissionDeniedError - If the user lacks delete permission
   * @throws DatabaseError - If the database operation fails
   */
  delete({
    userId,
    organizationId,
    projectId,
    environmentId,
    annotationId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    annotationId: string;
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
        annotationId,
      });

      const result: { id: string }[] = yield* client
        .delete(annotations)
        .where(
          and(
            eq(annotations.id, annotationId),
            eq(annotations.environmentId, environmentId),
          ),
        )
        .returning({ id: annotations.id })
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to delete annotation",
                cause: e,
              }),
          ),
        );

      const [row] = result;
      if (!row) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Annotation with id ${annotationId} not found`,
            resource: "annotation",
          }),
        );
      }
    });
  }
}
