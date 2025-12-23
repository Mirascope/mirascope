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
 * const db = yield* EffectDatabase;
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
 * // Verify an API key for authentication
 * const result = yield* db.organizations.projects.environments.apiKeys.verifyApiKey(key);
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
} from "@/errors";
import { isUniqueConstraintError } from "@/db/utils";
import {
  apiKeys,
  users,
  type NewApiKey,
  type PublicApiKey,
  type PublicUser,
  type ApiKeyCreateResponse,
  type ProjectRole,
} from "@/db/schema";
import * as crypto from "crypto";

// =============================================================================
// API Key Utilities
// =============================================================================

/** API key prefix for identification */
const API_KEY_PREFIX = "mk_";

/**
 * Generate a cryptographically secure random API key.
 */
function generateApiKey(): string {
  const bytes = crypto.randomBytes(32);
  return API_KEY_PREFIX + bytes.toString("base64url");
}

/**
 * Hash an API key for storage using SHA-256.
 */
function hashApiKey(key: string): string {
  return crypto.createHash("sha256").update(key).digest("hex");
}

/**
 * Generate a display prefix for an API key (e.g., "mk_abc...").
 */
function getKeyPrefix(key: string): string {
  return key.substring(0, 10) + "...";
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
  ownerId: apiKeys.ownerId,
  createdAt: apiKeys.createdAt,
  lastUsedAt: apiKeys.lastUsedAt,
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
   * @param args.data - API key data (name)
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
        .where(eq(apiKeys.environmentId, environmentId))
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
   * @param args.data - Fields to update (only `name` allowed)
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

      // Delete the API key
      const [deleted] = yield* client
        .delete(apiKeys)
        .where(
          and(
            eq(apiKeys.id, apiKeyId),
            eq(apiKeys.environmentId, environmentId),
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
   * Verifies an API key and returns its metadata.
   *
   * This method is used for API key authentication. It:
   * 1. Hashes the provided key
   * 2. Looks up the hash in the database
   * 3. Updates the lastUsedAt timestamp
   * 4. Returns the API key ID and environment ID
   *
   * Note: This method does NOT require authentication - it IS the authentication.
   *
   * @param key - The plaintext API key to verify
   * @returns The API key ID and environment ID
   * @throws NotFoundError - If the API key is invalid
   * @throws DatabaseError - If the database operation fails
   */
  verifyApiKey(
    key: string,
  ): Effect.Effect<
    { apiKeyId: string; environmentId: string },
    NotFoundError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;
      const keyHash = hashApiKey(key);

      // Look up the API key by hash
      const [apiKey] = yield* client
        .select({
          id: apiKeys.id,
          environmentId: apiKeys.environmentId,
        })
        .from(apiKeys)
        .where(eq(apiKeys.keyHash, keyHash))
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to verify API key",
                cause: e,
              }),
          ),
        );

      if (!apiKey) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "Invalid API key",
            resource: this.getResourceName(),
          }),
        );
      }

      // Update last used timestamp
      yield* client
        .update(apiKeys)
        .set({ lastUsedAt: new Date() })
        .where(eq(apiKeys.id, apiKey.id))
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to update API key last used timestamp",
                cause: e,
              }),
          ),
        );

      return { apiKeyId: apiKey.id, environmentId: apiKey.environmentId };
    });
  }

  /**
   * Gets the user who created an API key.
   *
   * This method is used after API key verification to get the user context
   * for authorization and audit purposes. The API key's creator determines
   * what permissions the API key has - it can only do what that user can do.
   *
   * Note: This method does NOT require authentication - it's called after
   * API key verification to establish user context for the request.
   *
   * @param apiKeyId - The API key ID (from verifyApiKey result)
   * @returns The user who created the API key
   * @throws NotFoundError - If the API key or user is not found
   * @throws DatabaseError - If the database operation fails
   */
  getCreator(
    apiKeyId: string,
  ): Effect.Effect<PublicUser, NotFoundError | DatabaseError, DrizzleORM> {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      const [creator] = yield* client
        .select({
          id: users.id,
          email: users.email,
          name: users.name,
          deletedAt: users.deletedAt,
        })
        .from(apiKeys)
        .innerJoin(users, eq(apiKeys.ownerId, users.id))
        .where(eq(apiKeys.id, apiKeyId))
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to get API key creator",
                cause: e,
              }),
          ),
        );

      if (!creator) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `API key ${apiKeyId} not found`,
            resource: this.getResourceName(),
          }),
        );
      }

      return creator;
    });
  }
}
