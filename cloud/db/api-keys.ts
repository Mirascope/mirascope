/**
 * @fileoverview Effect-native API Keys service.
 *
 * Provides authenticated CRUD operations for API keys with role-based access
 * control. API keys belong to environments and inherit authorization from the
 * project's membership system.
 *
 * ## Architecture
 *
 * ```
 * ApiKeys (authenticated)
 *   └── authorization via ProjectMemberships.getRole()
 * ```
 *
 * ## API Key Roles
 *
 * API keys use the project's role system:
 * - `ADMIN` - Full API key management (create, read, update, delete)
 * - `DEVELOPER` - Can create, read, and update API keys
 * - `VIEWER` - No access to API keys
 * - `ANNOTATOR` - No access to API keys
 *
 * ## Implicit Access
 *
 * Organization OWNER and ADMIN roles have implicit ADMIN access to all projects
 * (and thus all environments and API keys) within their organization.
 *
 * ## Security
 *
 * - API keys are stored as SHA-256 hashes, never plaintext
 * - The plaintext key is only returned once at creation time
 * - A prefix is stored for display purposes (e.g., "mk_abc...")
 *
 * @example
 * ```ts
 * const db = yield* Database;
 *
 * // Create an API key (returns plaintext key only at creation)
 * const { key, ...apiKey } = yield* db.organizations.projects.environments.apiKeys.create({
 *   userId: "user-123",
 *   organizationId: "org-456",
 *   projectId: "proj-789",
 *   environmentId: "env-012",
 *   data: { name: "production-key" },
 * });
 *
 * // Get API key info for authentication (includes owner details)
 * const apiKeyInfo = yield* db.organizations.projects.environments.apiKeys.getApiKeyInfo(key);
 * ```
 */

import * as crypto from "crypto";
import { and, eq, inArray, isNull, or, sql } from "drizzle-orm";
import { Effect } from "effect";

import {
  BaseAuthenticatedEffectService,
  type PermissionTable,
} from "@/db/base";
import { DrizzleORM } from "@/db/client";
import { ProjectMemberships } from "@/db/project-memberships";
import {
  apiKeys,
  claws,
  users,
  environments,
  projects,
  projectMemberships,
  organizationMemberships,
  type NewApiKey,
  type PublicApiKey,
  type ApiKeyCreateResponse,
  type ApiKeyInfo,
  type ApiKeyWithContext,
  type ProjectRole,
} from "@/db/schema";
import { isUniqueConstraintError } from "@/db/utils";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/errors";

// =============================================================================
// API Key Utilities
// =============================================================================

/** API key prefix for user keys */
const API_KEY_PREFIX = "mk_";

/** API key prefix for claw keys */
const CLAW_API_KEY_PREFIX = "mck_";

/**
 * Generate a cryptographically secure random API key.
 *
 * @param prefix - Key prefix (defaults to "mk_" for user keys)
 */
export function generateApiKey(prefix: string = API_KEY_PREFIX): string {
  const bytes = crypto.randomBytes(32);
  return prefix + bytes.toString("base64url");
}

/**
 * Hash an API key for storage using SHA-256.
 */
export function hashApiKey(key: string): string {
  return crypto.createHash("sha256").update(key).digest("hex");
}

/**
 * Generate a display prefix for an API key (e.g., "mk_abc...").
 */
export function getKeyPrefix(key: string): string {
  return key.substring(0, 10) + "...";
}

/**
 * Generate a claw API key with the "mck_" prefix.
 */
export function generateClawApiKey(): string {
  return generateApiKey(CLAW_API_KEY_PREFIX);
}

// =============================================================================
// Public Fields
// =============================================================================

/**
 * Public fields to select from the api_keys table.
 * Excludes keyHash for security.
 */
const publicFields = {
  id: apiKeys.id,
  name: apiKeys.name,
  keyPrefix: apiKeys.keyPrefix,
  environmentId: apiKeys.environmentId,
  organizationId: apiKeys.organizationId,
  ownerId: apiKeys.ownerId,
  createdAt: apiKeys.createdAt,
  lastUsedAt: apiKeys.lastUsedAt,
  deletedAt: apiKeys.deletedAt,
};

// =============================================================================
// ApiKeys Service
// =============================================================================

/**
 * Effect-native API Keys service.
 *
 * Provides CRUD operations with role-based access control for API keys.
 * Authorization is inherited from project membership via ProjectMemberships.getRole().
 *
 * ## Permission Matrix
 *
 * | Action   | ADMIN | DEVELOPER | VIEWER | ANNOTATOR |
 * |----------|-------|-----------|--------|-----------|
 * | create   | ✓     | ✓         | ✗      | ✗         |
 * | read     | ✓     | ✓         | ✗      | ✗         |
 * | update   | ✓     | ✓         | ✗      | ✗         |
 * | delete   | ✓     | ✓*        | ✗      | ✗         |
 *
 * *DEVELOPER can only delete API keys they created
 *
 * ## Security Model
 *
 * - Org OWNER/ADMIN have implicit project ADMIN access (and thus API key access)
 * - Non-members cannot see that an environment/API key exists (returns NotFoundError)
 * - API key names must be unique within an environment
 * - Keys are hashed with SHA-256 before storage
 */
export class ApiKeys extends BaseAuthenticatedEffectService<
  PublicApiKey,
  "organizations/:organizationId/projects/:projectId/environments/:environmentId/apiKeys/:apiKeyId",
  Pick<NewApiKey, "name">,
  Partial<Pick<NewApiKey, "name">>,
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
    return "api_key";
  }

  protected getPermissionTable(): PermissionTable<ProjectRole> {
    return {
      create: ["ADMIN", "DEVELOPER"],
      read: ["ADMIN", "DEVELOPER"],
      update: ["ADMIN", "DEVELOPER"],
      delete: ["ADMIN", "DEVELOPER"], // DEVELOPER can only delete their own keys (enforced in delete method)
    };
  }

  // ---------------------------------------------------------------------------
  // Role Resolution
  // ---------------------------------------------------------------------------

  /**
   * Determines the user's effective role for an API key.
   *
   * Delegates to `ProjectMemberships.getRole` which handles:
   * - Org OWNER → treated as project ADMIN
   * - Org ADMIN → treated as project ADMIN
   * - Explicit project membership role
   * - No access → NotFoundError (hides API key existence)
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
   * Creates a new API key within an environment.
   *
   * Requires ADMIN or DEVELOPER role on the project.
   * Returns the plaintext key only at creation time - it cannot be retrieved later.
   *
   * @param args.userId - The user creating the API key
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment to create the API key in
   * @param args.data - API key data
   * @returns The created API key with plaintext key
   * @throws PermissionDeniedError - If user lacks create permission
   * @throws AlreadyExistsError - If an API key with this name exists in the environment
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
    data: Pick<NewApiKey, "name">;
  }): Effect.Effect<
    ApiKeyCreateResponse,
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
        apiKeyId: "", // Not used for create
      });

      // Generate the API key
      const plaintextKey = generateApiKey();
      const keyHash = hashApiKey(plaintextKey);
      const keyPrefix = getKeyPrefix(plaintextKey);

      // Insert the API key
      const [apiKey] = yield* client
        .insert(apiKeys)
        .values({
          name: data.name,
          keyHash,
          keyPrefix,
          environmentId,
          ownerId: userId,
        })
        .returning(publicFields)
        .pipe(
          Effect.mapError((e): AlreadyExistsError | DatabaseError =>
            isUniqueConstraintError(e.cause)
              ? new AlreadyExistsError({
                  message: `An API key with name "${data.name}" already exists in this environment`,
                  resource: this.getResourceName(),
                })
              : new DatabaseError({
                  message: "Failed to create API key",
                  cause: e,
                }),
          ),
        );

      // Return with the plaintext key (only returned at creation)
      return {
        ...apiKey,
        key: plaintextKey,
      } as ApiKeyCreateResponse;
    });
  }

  /**
   * Creates a new org-scoped API key.
   *
   * Requires OWNER or ADMIN role on the organization.
   * Org-scoped keys can access any resource within the organization.
   *
   * @param args.userId - The user creating the API key
   * @param args.organizationId - The organization to scope the key to
   * @param args.data - API key data
   * @returns The created API key with plaintext key
   * @throws PermissionDeniedError - If user lacks org OWNER/ADMIN role
   * @throws AlreadyExistsError - If an org key with this name already exists
   * @throws NotFoundError - If the org doesn't exist or user is not a member
   * @throws DatabaseError - If the database operation fails
   */
  createOrgScoped({
    userId,
    organizationId,
    data,
  }: {
    userId: string;
    organizationId: string;
    data: Pick<NewApiKey, "name">;
  }): Effect.Effect<
    ApiKeyCreateResponse,
    AlreadyExistsError | NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      // Verify user is org OWNER or ADMIN
      const [orgMembership] = yield* client
        .select({ role: organizationMemberships.role })
        .from(organizationMemberships)
        .where(
          and(
            eq(organizationMemberships.organizationId, organizationId),
            eq(organizationMemberships.memberId, userId),
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to check organization membership",
                cause: e,
              }),
          ),
        );

      if (!orgMembership) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "Organization not found or you are not a member",
            resource: "Organization",
          }),
        );
      }

      if (orgMembership.role !== "OWNER" && orgMembership.role !== "ADMIN") {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message:
              "Organization OWNER or ADMIN role required to create org-scoped API keys",
          }),
        );
      }

      const plaintextKey = generateApiKey();
      const keyHash = hashApiKey(plaintextKey);
      const keyPrefix = getKeyPrefix(plaintextKey);

      const [apiKey] = yield* client
        .insert(apiKeys)
        .values({
          name: data.name,
          keyHash,
          keyPrefix,
          organizationId,
          ownerId: userId,
        })
        .returning(publicFields)
        .pipe(
          Effect.mapError((e): AlreadyExistsError | DatabaseError =>
            isUniqueConstraintError(e.cause)
              ? new AlreadyExistsError({
                  message: `An org-scoped API key with name "${data.name}" already exists`,
                  resource: this.getResourceName(),
                })
              : new DatabaseError({
                  message: "Failed to create org-scoped API key",
                  cause: e,
                }),
          ),
        );

      return {
        ...apiKey,
        key: plaintextKey,
      } as ApiKeyCreateResponse;
    });
  }

  /**
   * Retrieves all API keys in an environment.
   *
   * Requires ADMIN or DEVELOPER role on the project.
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment to list API keys for
   * @returns Array of API keys in the environment (without plaintext keys)
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
    PublicApiKey[],
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      // Authorize via project membership
      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        apiKeyId: "", // Not used for findAll
      });

      const results: PublicApiKey[] = yield* client
        .select(publicFields)
        .from(apiKeys)
        .where(
          and(
            eq(apiKeys.environmentId, environmentId),
            isNull(apiKeys.deletedAt),
          ),
        )
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to find all API keys",
                cause: e,
              }),
          ),
        );

      return results;
    });
  }

  /**
   * Retrieves an API key by ID.
   *
   * Requires ADMIN or DEVELOPER role on the project.
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment containing the API key
   * @param args.apiKeyId - The API key to retrieve
   * @returns The API key (without plaintext key)
   * @throws NotFoundError - If the API key doesn't exist or user lacks access
   * @throws PermissionDeniedError - If the user lacks read permission
   * @throws DatabaseError - If the database query fails
   */
  findById({
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
    PublicApiKey,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      // Authorize via project membership
      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        apiKeyId,
      });

      const [apiKey] = yield* client
        .select(publicFields)
        .from(apiKeys)
        .where(
          and(
            eq(apiKeys.id, apiKeyId),
            eq(apiKeys.environmentId, environmentId),
            isNull(apiKeys.deletedAt),
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to find API key",
                cause: e,
              }),
          ),
        );

      if (!apiKey) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `API key with apiKeyId ${apiKeyId} not found`,
            resource: this.getResourceName(),
          }),
        );
      }

      return apiKey;
    });
  }

  /**
   * Updates an API key.
   *
   * Requires ADMIN or DEVELOPER role on the project.
   * Only the name can be updated.
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment containing the API key
   * @param args.apiKeyId - The API key to update
   * @param args.data - Fields to update
   * @returns The updated API key
   * @throws NotFoundError - If the API key doesn't exist
   * @throws PermissionDeniedError - If the user lacks update permission
   * @throws AlreadyExistsError - If the new name conflicts with existing API key
   * @throws DatabaseError - If the database operation fails
   */
  update({
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
    data: Partial<Pick<NewApiKey, "name">>;
  }): Effect.Effect<
    PublicApiKey,
    NotFoundError | PermissionDeniedError | AlreadyExistsError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      // Authorize via project membership
      yield* this.authorize({
        userId,
        action: "update",
        organizationId,
        projectId,
        environmentId,
        apiKeyId,
      });

      const [updated] = yield* client
        .update(apiKeys)
        .set({ ...data })
        .where(
          and(
            eq(apiKeys.id, apiKeyId),
            eq(apiKeys.environmentId, environmentId),
            isNull(apiKeys.deletedAt),
          ),
        )
        .returning(publicFields)
        .pipe(
          Effect.mapError((e): AlreadyExistsError | DatabaseError =>
            isUniqueConstraintError(e.cause)
              ? new AlreadyExistsError({
                  message: `An API key with name "${data.name}" already exists in this environment`,
                  resource: this.getResourceName(),
                })
              : new DatabaseError({
                  message: "Failed to update API key",
                  cause: e,
                }),
          ),
        );

      if (!updated) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `API key with apiKeyId ${apiKeyId} not found`,
            resource: this.getResourceName(),
          }),
        );
      }

      return updated;
    });
  }

  /**
   * Deletes an API key.
   *
   * Requires ADMIN or DEVELOPER role on the project.
   * - ADMIN can delete any API key
   * - DEVELOPER can only delete API keys they created
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization containing the project
   * @param args.projectId - The project containing the environment
   * @param args.environmentId - The environment containing the API key
   * @param args.apiKeyId - The API key to delete
   * @throws NotFoundError - If the API key doesn't exist
   * @throws PermissionDeniedError - If the user lacks delete permission or is not the creator (DEVELOPER)
   * @throws DatabaseError - If the database operation fails
   */
  delete({
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
    void,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      // Get user's role (must be ADMIN or DEVELOPER)
      const role = yield* this.authorize({
        userId,
        action: "delete",
        organizationId,
        projectId,
        environmentId,
        apiKeyId,
      });

      // Fetch the API key to check ownership if not ADMIN
      if (role !== "ADMIN") {
        const [apiKey] = yield* client
          .select({ ownerId: apiKeys.ownerId })
          .from(apiKeys)
          .where(
            and(
              eq(apiKeys.id, apiKeyId),
              eq(apiKeys.environmentId, environmentId),
              isNull(apiKeys.deletedAt),
            ),
          )
          .limit(1)
          .pipe(
            Effect.mapError(
              (e) =>
                new DatabaseError({
                  message: "Failed to find API key",
                  cause: e,
                }),
            ),
          );

        if (!apiKey) {
          return yield* Effect.fail(
            new NotFoundError({
              message: `API key with apiKeyId ${apiKeyId} not found`,
              resource: this.getResourceName(),
            }),
          );
        }

        // DEVELOPER can only delete their own keys
        if (apiKey.ownerId !== userId) {
          return yield* Effect.fail(
            new PermissionDeniedError({
              message: "You can only delete API keys you created",
              resource: this.getResourceName(),
            }),
          );
        }
      }

      // Soft-delete the API key by setting deletedAt and renaming to free up the name
      const [deleted] = yield* client
        .update(apiKeys)
        .set({
          name: `deleted-${apiKeyId}`,
          deletedAt: new Date(),
        })
        .where(
          and(
            eq(apiKeys.id, apiKeyId),
            eq(apiKeys.environmentId, environmentId),
            isNull(apiKeys.deletedAt),
          ),
        )
        .returning({ id: apiKeys.id })
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to delete API key",
                cause: e,
              }),
          ),
        );

      if (!deleted) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `API key with apiKeyId ${apiKeyId} not found`,
            resource: this.getResourceName(),
          }),
        );
      }
    });
  }

  // ---------------------------------------------------------------------------
  // Custom Methods
  // ---------------------------------------------------------------------------

  /**
   * Gets complete API key information including owner details.
   *
   * This method is used for API key authentication. It:
   * 1. Hashes the provided key
   * 2. Looks up the hash in the database with an inner join on users
   * 3. Updates the lastUsedAt timestamp
   * 4. Returns the API key ID, full resource hierarchy, and owner information
   *
   * If the user associated with the API key doesn't exist, this returns a NotFoundError.
   * This ensures that we only proceed with authentication if there is a valid user for the API key.
   *
   * Note: This method does NOT require authentication - it IS the authentication.
   *
   * @param key - The plaintext API key to verify
   * @returns Complete API key information including owner details
   * @throws NotFoundError - If the API key is invalid or the owner doesn't exist
   * @throws DatabaseError - If the database operation fails
   */
  getApiKeyInfo(
    key: string,
  ): Effect.Effect<ApiKeyInfo, NotFoundError | DatabaseError, DrizzleORM> {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;
      const keyHash = hashApiKey(key);

      // Look up the API key by hash and resolve the full hierarchy + owner info.
      // Supports both environment-scoped keys (join through env→project→org)
      // and org-scoped keys (direct organizationId on the key).
      // LEFT JOIN to claws to get clawId for claw-user-owned keys.
      const [apiKeyInfo] = yield* client
        .select({
          apiKeyId: apiKeys.id,
          environmentId: apiKeys.environmentId,
          projectId: environments.projectId,
          // Org-scoped keys have organizationId directly; env-scoped resolve through project
          organizationId:
            sql<string>`COALESCE(${apiKeys.organizationId}, ${projects.organizationId})`.as(
              "organizationId",
            ),
          clawId: claws.id,
          ownerId: users.id,
          ownerEmail: users.email,
          ownerName: users.name,
          ownerAccountType: users.accountType,
          ownerDeletedAt: users.deletedAt,
        })
        .from(apiKeys)
        // LEFT JOIN for env-scoped keys (null for org-scoped)
        .leftJoin(environments, eq(apiKeys.environmentId, environments.id))
        .leftJoin(projects, eq(environments.projectId, projects.id))
        .innerJoin(users, eq(apiKeys.ownerId, users.id))
        .leftJoin(claws, eq(claws.botUserId, users.id))
        .where(
          and(
            eq(apiKeys.keyHash, keyHash),
            isNull(users.deletedAt),
            isNull(apiKeys.deletedAt),
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to get API key info",
                cause: e,
              }),
          ),
        );

      if (!apiKeyInfo) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "Invalid API key or owner not found",
            resource: this.getResourceName(),
          }),
        );
      }

      // Update last used timestamp
      yield* client
        .update(apiKeys)
        .set({ lastUsedAt: new Date() })
        .where(eq(apiKeys.id, apiKeyInfo.apiKeyId))
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to update API key last used timestamp",
                cause: e,
              }),
          ),
        );

      // Narrow to the discriminated union based on environmentId presence
      return apiKeyInfo as ApiKeyInfo;
    });
  }

  /**
   * Retrieves all API keys across all projects and environments in an organization
   * that the user has access to.
   *
   * - Org OWNER/ADMIN can see all API keys in the organization
   * - Other members can only see API keys in projects they have explicit membership in
   *   with ADMIN or DEVELOPER role
   *
   * @param args.userId - The authenticated user
   * @param args.organizationId - The organization to list API keys for
   * @returns Array of API keys with project and environment context
   * @throws NotFoundError - If the organization doesn't exist or user is not a member
   * @throws DatabaseError - If the database query fails
   */
  findAllForOrganization({
    userId,
    organizationId,
  }: {
    userId: string;
    organizationId: string;
  }): Effect.Effect<
    ApiKeyWithContext[],
    NotFoundError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      // Check the user's organization membership
      const [orgMembership] = yield* client
        .select({ role: organizationMemberships.role })
        .from(organizationMemberships)
        .where(
          and(
            eq(organizationMemberships.organizationId, organizationId),
            eq(organizationMemberships.memberId, userId),
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to check organization membership",
                cause: e,
              }),
          ),
        );

      if (!orgMembership) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "Organization not found",
            resource: "organization",
          }),
        );
      }

      const isOrgAdmin =
        orgMembership.role === "OWNER" || orgMembership.role === "ADMIN";

      // Build the query for API keys with context
      // Note: this only returns env-scoped keys (inner joins on environments/projects)
      const baseQuery = client
        .select({
          id: apiKeys.id,
          name: apiKeys.name,
          keyPrefix: apiKeys.keyPrefix,
          environmentId: apiKeys.environmentId,
          organizationId: apiKeys.organizationId,
          ownerId: apiKeys.ownerId,
          createdAt: apiKeys.createdAt,
          lastUsedAt: apiKeys.lastUsedAt,
          deletedAt: apiKeys.deletedAt,
          projectId: projects.id,
          projectName: projects.name,
          environmentName: environments.name,
        })
        .from(apiKeys)
        .innerJoin(environments, eq(apiKeys.environmentId, environments.id))
        .innerJoin(projects, eq(environments.projectId, projects.id));

      let results: ApiKeyWithContext[];

      if (isOrgAdmin) {
        // Org OWNER/ADMIN can see all API keys in the organization
        results = yield* baseQuery
          .where(
            and(
              eq(projects.organizationId, organizationId),
              isNull(apiKeys.deletedAt),
            ),
          )
          .pipe(
            Effect.mapError(
              (e) =>
                new DatabaseError({
                  message: "Failed to find API keys for organization",
                  cause: e,
                }),
            ),
          );
      } else {
        // Get projects where the user has ADMIN or DEVELOPER role
        const userProjectMemberships = yield* client
          .select({ projectId: projectMemberships.projectId })
          .from(projectMemberships)
          .where(
            and(
              eq(projectMemberships.memberId, userId),
              eq(projectMemberships.organizationId, organizationId),
              or(
                eq(projectMemberships.role, "ADMIN"),
                eq(projectMemberships.role, "DEVELOPER"),
              ),
            ),
          )
          .pipe(
            Effect.mapError(
              (e) =>
                new DatabaseError({
                  message: "Failed to get user project memberships",
                  cause: e,
                }),
            ),
          );

        const accessibleProjectIds = userProjectMemberships.map(
          (m) => m.projectId,
        );

        if (accessibleProjectIds.length === 0) {
          return [];
        }

        // Get API keys for accessible projects only
        results = yield* baseQuery
          .where(
            and(
              eq(projects.organizationId, organizationId),
              inArray(projects.id, accessibleProjectIds),
              isNull(apiKeys.deletedAt),
            ),
          )
          .pipe(
            Effect.mapError(
              (e) =>
                new DatabaseError({
                  message: "Failed to find API keys for organization",
                  cause: e,
                }),
            ),
          );
      }

      return results;
    });
  }
}
