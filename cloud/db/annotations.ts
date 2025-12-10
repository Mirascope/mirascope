/**
 * @fileoverview Effect-native Annotations service for span annotations.
 *
 * Provides authenticated annotation management with role-based access control.
 * Annotations belong to environments and inherit authorization from the project's
 * membership system.
 *
 * ## Architecture
 *
 * ```
 * Annotations extends BaseAuthenticatedEffectService
 *   └── authorization via ProjectMemberships.getRole()
 * ```
 *
 * ## Annotation Roles
 *
 * Annotations use the project's role system:
 * - `ADMIN` - Full annotation management
 * - `DEVELOPER` - Can create/read/update annotations
 * - `VIEWER` - Read-only access
 * - `ANNOTATOR` - Can create/read/update annotations
 *
 * ## Security
 *
 * - API key authentication provides environment context
 * - The API key owner's userId is used for authorization
 * - Authorization is delegated to ProjectMemberships
 */

import { Effect } from "effect";
import { and, eq, desc, sql } from "drizzle-orm";
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
import {
  annotations,
  type NewAnnotation,
  type PublicAnnotation,
} from "@/db/schema/annotations";
import { spans } from "@/db/schema/spans";
import type { ProjectRole } from "@/db/schema";
import { isUniqueConstraintError } from "@/db/utils";

// =============================================================================
// Types
// =============================================================================

/**
 * Context for an environment within a project.
 */
type EnvironmentContext = {
  environmentId: string;
  projectId: string;
  organizationId: string;
};

/**
 * Input data for creating an annotation.
 */
export type CreateAnnotationInput = {
  spanId: string; // OTLP span_id (hex string)
  traceId: string; // OTLP trace_id (hex string)
  label?: string | null;
  reasoning?: string | null;
  data?: Record<string, unknown> | null;
};

/**
 * Input data for updating an annotation.
 */
export type UpdateAnnotationInput = {
  label?: string | null;
  reasoning?: string | null;
  data?: Record<string, unknown> | null;
};

/**
 * Filters for listing annotations.
 */
export type AnnotationFilters = {
  traceId?: string;
  spanId?: string;
  label?: string;
  limit?: number;
  offset?: number;
};

type SpanInfo = {
  id: string;
  traceDbId: string;
  spanId: string;
  traceId: string;
};

// =============================================================================
// Annotations Service
// =============================================================================

/** Path pattern for annotation resources */
type AnnotationPath =
  "organizations/:organizationId/projects/:projectId/environments/:environmentId/annotations/:annotationId";

/**
 * Effect-native Annotations service for span annotations.
 *
 * Extends BaseAuthenticatedEffectService for standardized authorization.
 * Authorization is delegated to ProjectMemberships.getRole().
 *
 * ## Permission Matrix
 *
 * | Action   | ADMIN | DEVELOPER | VIEWER | ANNOTATOR |
 * |----------|-------|-----------|--------|-----------|
 * | create   | ✓     | ✓         | ✗      | ✓         |
 * | read     | ✓     | ✓         | ✓      | ✓         |
 * | update   | ✓     | ✓         | ✗      | ✓         |
 * | delete   | ✓     | ✗         | ✗      | ✗         |
 */
export class Annotations extends BaseAuthenticatedEffectService<
  PublicAnnotation,
  AnnotationPath,
  CreateAnnotationInput,
  UpdateAnnotationInput,
  ProjectRole
> {
  private readonly projectMemberships: ProjectMemberships;

  constructor(projectMemberships: ProjectMemberships) {
    super();
    this.projectMemberships = projectMemberships;
  }

  // ---------------------------------------------------------------------------
  // BaseAuthenticatedEffectService Implementation
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
  // Internal Helpers
  // ---------------------------------------------------------------------------

  /**
   * Find span by OTLP identifiers.
   */
  private findSpan(
    spanId: string,
    traceId: string,
    environmentId: string,
  ): Effect.Effect<SpanInfo, NotFoundError | DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const result: SpanInfo[] = yield* client
        .select({
          id: spans.id,
          traceDbId: spans.traceDbId,
          spanId: spans.spanId,
          traceId: spans.traceId,
        })
        .from(spans)
        .where(
          and(
            eq(spans.spanId, spanId),
            eq(spans.traceId, traceId),
            eq(spans.environmentId, environmentId),
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: `Failed to find span: ${e instanceof Error ? e.message : "Unknown error"}`,
                cause: e,
              }),
          ),
        );

      const row = result[0];
      if (!row) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Span with spanId=${spanId}, traceId=${traceId} not found`,
            resource: "span",
          }),
        );
      }

      return row;
    });
  }

  // ---------------------------------------------------------------------------
  // CRUD Methods (BaseAuthenticatedEffectService interface)
  // ---------------------------------------------------------------------------

  /**
   * Create annotation for a span with authorization.
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
    data: CreateAnnotationInput;
  }): Effect.Effect<
    PublicAnnotation,
    AlreadyExistsError | NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      // Authorize using base class method
      yield* this.authorize({
        userId,
        action: "create",
        organizationId,
        projectId,
        environmentId,
        annotationId: "",
      });

      return yield* this.createInternal(
        data,
        {
          environmentId,
          projectId,
          organizationId,
        },
        userId,
      );
    });
  }

  /**
   * Internal create - does NOT perform authorization.
   */
  private createInternal(
    data: CreateAnnotationInput,
    context: EnvironmentContext,
    createdBy: string,
  ): Effect.Effect<
    PublicAnnotation,
    NotFoundError | AlreadyExistsError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      // Find the span by OTLP identifiers
      const spanInfo = yield* this.findSpan(
        data.spanId,
        data.traceId,
        context.environmentId,
      );

      // Create the annotation
      const newAnnotation: NewAnnotation = {
        spanDbId: spanInfo.id,
        traceDbId: spanInfo.traceDbId,
        spanId: spanInfo.spanId,
        traceId: spanInfo.traceId,
        label: data.label ?? null,
        reasoning: data.reasoning ?? null,
        data: data.data ?? null,
        environmentId: context.environmentId,
        projectId: context.projectId,
        organizationId: context.organizationId,
        createdBy,
      };

      const result: PublicAnnotation[] = yield* client
        .insert(annotations)
        .values(newAnnotation)
        .returning()
        .pipe(
          Effect.mapError((e) => {
            if (isUniqueConstraintError(e)) {
              return new AlreadyExistsError({
                message: `Annotation for span ${data.spanId} already exists`,
                resource: "annotation",
              });
            }
            return new DatabaseError({
              message: `Failed to create annotation: ${e instanceof Error ? e.message : "Unknown error"}`,
              cause: e,
            });
          }),
        );

      return result[0];
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
    PublicAnnotation[],
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
        annotationId: "",
      });

      const result = yield* this.listInternal(environmentId);
      return result.annotations;
    });
  }

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
      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        annotationId,
      });

      return yield* this.getByIdInternal(annotationId, environmentId);
    });
  }

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
    data: UpdateAnnotationInput;
  }): Effect.Effect<
    PublicAnnotation,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      // Authorize using base class method
      yield* this.authorize({
        userId,
        action: "update",
        organizationId,
        projectId,
        environmentId,
        annotationId,
      });

      return yield* this.updateInternal(annotationId, data, environmentId);
    });
  }

  /**
   * Internal update - does NOT perform authorization.
   */
  private updateInternal(
    id: string,
    data: UpdateAnnotationInput,
    environmentId: string,
  ): Effect.Effect<
    PublicAnnotation,
    NotFoundError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const updateData: Partial<NewAnnotation> = {
        updatedAt: new Date(),
      };

      if (data.label !== undefined) {
        updateData.label = data.label;
      }
      if (data.reasoning !== undefined) {
        updateData.reasoning = data.reasoning;
      }
      if (data.data !== undefined) {
        updateData.data = data.data;
      }

      const result: PublicAnnotation[] = yield* client
        .update(annotations)
        .set(updateData)
        .where(
          and(
            eq(annotations.id, id),
            eq(annotations.environmentId, environmentId),
          ),
        )
        .returning()
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: `Failed to update annotation: ${e instanceof Error ? e.message : "Unknown error"}`,
                cause: e,
              }),
          ),
        );

      if (!result[0]) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Annotation with id ${id} not found`,
            resource: "annotation",
          }),
        );
      }

      return result[0];
    });
  }

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
      // Authorize using base class method
      yield* this.authorize({
        userId,
        action: "delete",
        organizationId,
        projectId,
        environmentId,
        annotationId,
      });

      return yield* this.deleteInternal(annotationId, environmentId);
    });
  }

  /**
   * Internal delete - does NOT perform authorization.
   */
  private deleteInternal(
    id: string,
    environmentId: string,
  ): Effect.Effect<void, NotFoundError | DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const result: { id: string }[] = yield* client
        .delete(annotations)
        .where(
          and(
            eq(annotations.id, id),
            eq(annotations.environmentId, environmentId),
          ),
        )
        .returning({ id: annotations.id })
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: `Failed to delete annotation: ${e instanceof Error ? e.message : "Unknown error"}`,
                cause: e,
              }),
          ),
        );

      if (!result[0]) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Annotation with id ${id} not found`,
            resource: "annotation",
          }),
        );
      }
    });
  }

  // ---------------------------------------------------------------------------
  // Annotation Retrieval (Authorized)
  // ---------------------------------------------------------------------------

  /**
   * Get annotation by ID with authorization.
   */
  getById({
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
      // Authorize using base class method
      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        annotationId,
      });

      return yield* this.getByIdInternal(annotationId, environmentId);
    });
  }

  /**
   * Internal getById - does NOT perform authorization.
   */
  private getByIdInternal(
    id: string,
    environmentId: string,
  ): Effect.Effect<
    PublicAnnotation,
    NotFoundError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const result: PublicAnnotation[] = yield* client
        .select()
        .from(annotations)
        .where(
          and(
            eq(annotations.id, id),
            eq(annotations.environmentId, environmentId),
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: `Failed to get annotation: ${e instanceof Error ? e.message : "Unknown error"}`,
                cause: e,
              }),
          ),
        );

      const row = result[0];
      if (!row) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Annotation with id ${id} not found`,
            resource: "annotation",
          }),
        );
      }

      return row;
    });
  }

  /**
   * List annotations with filters and authorization.
   */
  list({
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
    { annotations: PublicAnnotation[]; total: number },
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      // Authorize using base class method
      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        annotationId: "",
      });

      return yield* this.listInternal(environmentId, filters);
    });
  }

  /**
   * Internal list - does NOT perform authorization.
   */
  private listInternal(
    environmentId: string,
    filters?: AnnotationFilters,
  ): Effect.Effect<
    { annotations: PublicAnnotation[]; total: number },
    DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const conditions = [eq(annotations.environmentId, environmentId)];

      if (filters?.traceId) {
        conditions.push(eq(annotations.traceId, filters.traceId));
      }

      if (filters?.spanId) {
        conditions.push(eq(annotations.spanId, filters.spanId));
      }

      if (filters?.label) {
        conditions.push(eq(annotations.label, filters.label));
      }

      const whereClause = and(...conditions);

      // Get total count
      const countResult: { count: number }[] = yield* client
        .select({ count: sql<number>`count(*)::int` })
        .from(annotations)
        .where(whereClause)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: `Failed to count annotations: ${e instanceof Error ? e.message : "Unknown error"}`,
                cause: e,
              }),
          ),
        );

      const total = countResult[0]?.count ?? 0;

      // Build query
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
              message: `Failed to list annotations: ${e instanceof Error ? e.message : "Unknown error"}`,
              cause: e,
            }),
        ),
      );

      return {
        annotations: results,
        total,
      };
    });
  }
}
