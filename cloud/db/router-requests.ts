/**
 * @fileoverview Effect-native Router Requests service.
 *
 * Provides authenticated CRUD operations for router requests with role-based
 * access control. Router requests are immutable financial records that track
 * all LLM requests made through the router.
 *
 * ## Architecture
 *
 * ```
 * RouterRequests (authenticated)
 *   └── nested under API Keys
 *   └── authorization via ProjectMemberships.getRole()
 * ```
 *
 * ## Router Request Roles
 *
 * Router requests use the project's role system:
 * - `ADMIN` - Full access (create, read, update)
 * - `DEVELOPER` - Full access (create, read, update)
 * - `VIEWER` - Read-only access (read)
 * - `ANNOTATOR` - Read-only access (read)
 *
 * ## Implicit Access
 *
 * Organization OWNER and ADMIN roles have implicit ADMIN access to all projects
 * (and thus all environments and router requests) within their organization.
 *
 * ## Immutability
 *
 * Router requests are financial records:
 * - Can only update certain fields (status, usage, cost, completion data)
 * - Core identity fields (provider, model, IDs) are immutable
 * - Cannot be deleted (regulatory compliance requires audit trail)
 *
 * ## Security Model
 *
 * - Non-members cannot see router requests (returns NotFoundError)
 * - Router requests are queried by environment (not API key)
 * - Any user with environment access can see all requests for that environment
 * - apiKeyId is part of the path structure but not used for filtering
 * - Created via API key authentication during router operations
 *
 * @example
 * ```ts
 * const db = yield* Database;
 *
 * // Create a router request (typically done by router, not end users)
 * // Path parameters are injected automatically
 * const request = yield* db.organizations.projects.environments.apiKeys.routerRequests.create({
 *   userId: "user-123",
 *   organizationId: "org-456",
 *   projectId: "proj-789",
 *   environmentId: "env-012",
 *   apiKeyId: "key-345",
 *   data: {
 *     provider: "anthropic",
 *     model: "claude-3-opus-20240229",
 *     status: "pending",
 *   },
 * });
 *
 * // List all router requests for an environment
 * const requests = yield* db.organizations.projects.environments.apiKeys.routerRequests.findAll({
 *   userId: "user-123",
 *   organizationId: "org-456",
 *   projectId: "proj-789",
 *   environmentId: "env-012",
 *   apiKeyId: "key-345",
 * });
 *
 * // Get a specific router request
 * const request = yield* db.organizations.projects.environments.apiKeys.routerRequests.findById({
 *   userId: "user-123",
 *   organizationId: "org-456",
 *   projectId: "proj-789",
 *   environmentId: "env-012",
 *   apiKeyId: "key-345",
 *   routerRequestId: "req-123",
 * });
 * ```
 */

import { Effect } from "effect";
import { eq, and, desc } from "drizzle-orm";
import {
  BaseAuthenticatedEffectService,
  type PermissionTable,
} from "@/db/base";
import { DrizzleORM } from "@/db/client";
import { ProjectMemberships } from "@/db/project-memberships";
import { DatabaseError, NotFoundError, PermissionDeniedError } from "@/errors";
import {
  routerRequests,
  type NewRouterRequest,
  type RouterRequest,
  type ProjectRole,
} from "@/db/schema";

/**
 * Public fields to select from the router_requests table.
 */
const publicFields = {
  id: routerRequests.id,
  provider: routerRequests.provider,
  model: routerRequests.model,
  requestId: routerRequests.requestId,
  inputTokens: routerRequests.inputTokens,
  outputTokens: routerRequests.outputTokens,
  cacheReadTokens: routerRequests.cacheReadTokens,
  cacheWriteTokens: routerRequests.cacheWriteTokens,
  cacheWriteBreakdown: routerRequests.cacheWriteBreakdown,
  costCenticents: routerRequests.costCenticents,
  status: routerRequests.status,
  errorMessage: routerRequests.errorMessage,
  organizationId: routerRequests.organizationId,
  projectId: routerRequests.projectId,
  environmentId: routerRequests.environmentId,
  apiKeyId: routerRequests.apiKeyId,
  userId: routerRequests.userId,
  createdAt: routerRequests.createdAt,
  completedAt: routerRequests.completedAt,
};

/**
 * Type for creating router requests.
 * Omits path parameters (organizationId, projectId, environmentId, apiKeyId, userId)
 * since they are provided via the path and injected automatically.
 */
export type CreateRouterRequest = Omit<
  NewRouterRequest,
  | "organizationId"
  | "projectId"
  | "environmentId"
  | "apiKeyId"
  | "userId"
  | "createdAt"
>;

/**
 * Type for updating router requests.
 * Only allows updating status, usage metrics, cost, and completion data.
 * Core identity fields (provider, model, IDs) are immutable.
 */
export type UpdateRouterRequest = Partial<
  Pick<
    NewRouterRequest,
    | "status"
    | "requestId"
    | "inputTokens"
    | "outputTokens"
    | "cacheReadTokens"
    | "cacheWriteTokens"
    | "cacheWriteBreakdown"
    | "costCenticents"
    | "errorMessage"
    | "completedAt"
  >
>;

/**
 * Effect-native Router Requests service.
 *
 * Provides CRUD operations with role-based access control for router requests.
 * Router requests can be updated to add usage data and change status, but cannot
 * be deleted (regulatory compliance). Authorization is inherited from project membership.
 *
 * ## Permission Matrix
 *
 * | Action   | ADMIN | DEVELOPER | VIEWER | ANNOTATOR |
 * |----------|-------|-----------|--------|-----------|
 * | create   | ✓     | ✓         | ✗      | ✗         |
 * | read     | ✓     | ✓         | ✓      | ✓         |
 * | update   | ✓     | ✓         | ✗      | ✗         |
 * | delete   | ✗     | ✗         | ✗      | ✗         |
 *
 * Note: Delete always fails with PermissionDeniedError (financial records must be retained).
 */
export class RouterRequests extends BaseAuthenticatedEffectService<
  RouterRequest,
  "organizations/:organizationId/projects/:projectId/environments/:environmentId/api-keys/:apiKeyId/router-requests/:routerRequestId",
  CreateRouterRequest,
  UpdateRouterRequest,
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
    return "router_request";
  }

  protected getPermissionTable(): PermissionTable<ProjectRole> {
    return {
      create: ["ADMIN", "DEVELOPER"],
      read: ["ADMIN", "DEVELOPER", "VIEWER", "ANNOTATOR"],
      update: ["ADMIN", "DEVELOPER"], // For updating status/usage after request completes
      delete: [], // No one can delete (financial records must be retained)
    };
  }

  // ---------------------------------------------------------------------------
  // Role Resolution
  // ---------------------------------------------------------------------------

  /**
   * Determines the user's effective role for router requests.
   *
   * Delegates to `ProjectMemberships.getRole` which handles:
   * - Org OWNER → treated as project ADMIN
   * - Org ADMIN → treated as project ADMIN
   * - Explicit project membership role
   * - No access → NotFoundError (hides router request existence)
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
    apiKeyId?: string;
    routerRequestId?: string;
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
   * Creates a new router request.
   *
   * Requires ADMIN or DEVELOPER role on the project.
   * Router requests are typically created by the router during API request processing,
   * not directly by end users.
   *
   * Path parameters (organizationId, projectId, environmentId, apiKeyId, userId) are
   * injected automatically and should not be included in the data parameter.
   *
   * @param args.userId - The authenticated user (from API key)
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment making the request
   * @param args.apiKeyId - The API key making the request
   * @param args.data - Router request data (provider, model, tokens, cost, etc.)
   * @returns The created router request
   * @throws PermissionDeniedError - If user lacks create permission
   * @throws NotFoundError - If the environment doesn't exist or user lacks access
   * @throws DatabaseError - If the database operation fails
   */
  create({
    userId,
    organizationId,
    projectId,
    environmentId,
    apiKeyId,
    data,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    apiKeyId: string;
    data: CreateRouterRequest;
  }): Effect.Effect<
    RouterRequest,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      // Authorize
      yield* this.authorize({
        userId,
        action: "create",
        organizationId,
        projectId,
        environmentId,
        apiKeyId,
        routerRequestId: "", // Not used for create
      });

      const [routerRequest] = yield* client
        .insert(routerRequests)
        .values({
          ...data,
          userId,
          organizationId,
          projectId,
          environmentId,
          apiKeyId,
        })
        .returning(publicFields)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to create router request",
                cause: e,
              }),
          ),
        );

      return routerRequest;
    });
  }

  /**
   * Retrieves all router requests for an environment.
   *
   * Requires any project role (ADMIN, DEVELOPER, VIEWER, or ANNOTATOR).
   * Results are ordered by creation time (most recent first).
   *
   * Note: apiKeyId is part of the path structure but queries are scoped to
   * environment, allowing any user with environment access to see all requests.
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment to list requests for
   * @param args.apiKeyId - Part of path structure (not used for filtering)
   * @returns Array of router requests for the environment
   * @throws NotFoundError - If the environment doesn't exist or user lacks access
   * @throws PermissionDeniedError - If the user lacks read permission
   * @throws DatabaseError - If the database query fails
   */
  findAll({
    userId,
    organizationId,
    projectId,
    environmentId,
    apiKeyId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    apiKeyId: string;
  }): Effect.Effect<
    RouterRequest[],
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      // Authorize
      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        apiKeyId,
        routerRequestId: "", // Not used for findAll
      });

      return yield* client
        .select(publicFields)
        .from(routerRequests)
        // NOTE: environment ID constrains us to the correct org/project already
        .where(eq(routerRequests.environmentId, environmentId))
        .orderBy(desc(routerRequests.createdAt))
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to find all router requests",
                cause: e,
              }),
          ),
        );
    });
  }

  /**
   * Retrieves a router request by ID.
   *
   * Requires any project role (ADMIN, DEVELOPER, VIEWER, or ANNOTATOR).
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment containing the request
   * @param args.apiKeyId - Part of path structure (not used for filtering)
   * @param args.routerRequestId - The router request to retrieve
   * @returns The router request
   * @throws NotFoundError - If the router request doesn't exist or user lacks access
   * @throws PermissionDeniedError - If the user lacks read permission
   * @throws DatabaseError - If the database query fails
   */
  findById({
    userId,
    organizationId,
    projectId,
    environmentId,
    apiKeyId,
    routerRequestId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    apiKeyId: string;
    routerRequestId: string;
  }): Effect.Effect<
    RouterRequest,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      // Authorize
      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        apiKeyId,
        routerRequestId,
      });

      const [routerRequest] = yield* client
        .select(publicFields)
        .from(routerRequests)
        .where(
          and(
            eq(routerRequests.id, routerRequestId),
            // NOTE: environment ID constrains us to the correct org/project already
            eq(routerRequests.environmentId, environmentId),
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to find router request",
                cause: e,
              }),
          ),
        );

      if (!routerRequest) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Router request with routerRequestId ${routerRequestId} not found`,
            resource: this.getResourceName(),
          }),
        );
      }

      return routerRequest;
    });
  }

  /**
   * Updates a router request with usage data and status.
   *
   * Requires ADMIN or DEVELOPER role on the project.
   * Typically called by the router after a request completes to update:
   * - status (pending → success/failure)
   * - usage metrics (inputTokens, outputTokens, cacheReadTokens, etc.)
   * - cost (costCenticents)
   * - completion time (completedAt)
   * - error message (errorMessage, if failed)
   *
   * Core identity fields (provider, model, IDs, createdAt) cannot be modified.
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment containing the request
   * @param args.apiKeyId - Part of path structure (not used for filtering)
   * @param args.routerRequestId - The router request to update
   * @param args.data - Fields to update (status, usage metrics, cost, etc.)
   * @returns The updated router request
   * @throws NotFoundError - If the router request doesn't exist
   * @throws PermissionDeniedError - If the user lacks update permission
   * @throws DatabaseError - If the database operation fails
   */
  update({
    userId,
    organizationId,
    projectId,
    environmentId,
    apiKeyId,
    routerRequestId,
    data,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    apiKeyId: string;
    routerRequestId: string;
    data: UpdateRouterRequest;
  }): Effect.Effect<
    RouterRequest,
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
        apiKeyId,
        routerRequestId,
      });

      const [updated] = yield* client
        .update(routerRequests)
        .set(data)
        .where(
          and(
            eq(routerRequests.id, routerRequestId),
            // NOTE: environment ID constrains us to the correct org/project already
            eq(routerRequests.environmentId, environmentId),
          ),
        )
        .returning(publicFields)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to update router request",
                cause: e,
              }),
          ),
        );

      if (!updated) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Router request with routerRequestId ${routerRequestId} not found`,
            resource: this.getResourceName(),
          }),
        );
      }

      return updated;
    });
  }

  /**
   * Deletes a router request (not supported - financial records must be retained).
   *
   * Always fails with PermissionDeniedError because no one has permission to delete
   * router requests. They are financial records that must be retained for regulatory
   * compliance and audit trails.
   *
   * @throws PermissionDeniedError - Always (no one can delete financial records)
   * @throws NotFoundError - If user lacks project access (hides request existence)
   */
  delete({
    userId,
    organizationId,
    projectId,
    environmentId,
    apiKeyId,
    routerRequestId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    apiKeyId: string;
    routerRequestId: string;
  }): Effect.Effect<
    void,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      // Authorize - this will always error since the user is either not a member (NotFoundError)
      // or they are a member, but no one has permission to delete (PermissionDeniedError)
      yield* this.authorize({
        userId,
        action: "delete",
        organizationId,
        projectId,
        environmentId,
        apiKeyId,
        routerRequestId,
      });
    });
  }
}
