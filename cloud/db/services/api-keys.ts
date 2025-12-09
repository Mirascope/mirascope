import { Effect } from "effect";
import { and, eq } from "drizzle-orm";
import type { PgColumn } from "drizzle-orm/pg-core";
import type { PostgresJsDatabase } from "drizzle-orm/postgres-js";
import { BaseService, BaseAuthenticatedService } from "@/db/services/base";
import type { PermissionAction } from "@/db/services/base";
import {
  DatabaseError,
  NotFoundError,
  AlreadyExistsError,
  PermissionDeniedError,
} from "@/db/errors";
import * as schema from "@/db/schema";
import {
  apiKeys,
  type PublicApiKey,
  type ApiKeyCreateResponse,
} from "@/db/schema/api-keys";
import { environments } from "@/db/schema/environments";
import { projects } from "@/db/schema/projects";
import { organizationMemberships } from "@/db/schema/organization-memberships";
import * as crypto from "crypto";

// Role hierarchy for permission checks
const ROLE_HIERARCHY = {
  OWNER: 4,
  ADMIN: 3,
  DEVELOPER: 2,
  ANNOTATOR: 1,
} as const;

// Required role for each action
const REQUIRED_ROLE_FOR_ACTION: Record<
  PermissionAction,
  keyof typeof ROLE_HIERARCHY
> = {
  read: "DEVELOPER",
  create: "DEVELOPER",
  update: "ADMIN",
  delete: "ADMIN",
};

// API key prefix for identification
const API_KEY_PREFIX = "mk_";

/**
 * Generate a cryptographically secure random API key
 */
function generateApiKey(): string {
  const bytes = crypto.randomBytes(32);
  return API_KEY_PREFIX + bytes.toString("base64url");
}

/**
 * Hash an API key for storage
 */
function hashApiKey(key: string): string {
  return crypto.createHash("sha256").update(key).digest("hex");
}

/**
 * Generate a display prefix for an API key (e.g., "mk_abc...")
 */
function getKeyPrefix(key: string): string {
  return key.substring(0, 10) + "...";
}

class BaseApiKeyService extends BaseService<
  PublicApiKey,
  string,
  typeof apiKeys
> {
  /* v8 ignore start */
  protected getTable() {
    return apiKeys;
  }

  protected getResourceName() {
    return "api_key";
  }

  protected getPublicFields(): Record<string, PgColumn> {
    return {
      id: apiKeys.id,
      name: apiKeys.name,
      keyPrefix: apiKeys.keyPrefix,
      environmentId: apiKeys.environmentId,
      createdAt: apiKeys.createdAt,
      lastUsedAt: apiKeys.lastUsedAt,
    };
  }
  /* v8 ignore stop */
}

export class ApiKeyService extends BaseAuthenticatedService<
  PublicApiKey,
  string,
  typeof apiKeys
> {
  protected initializeBaseService(): BaseApiKeyService {
    return new BaseApiKeyService(this.db);
  }

  /**
   * Check if user has permission for the environment that owns the API key
   */
  private checkEnvironmentPermission(
    userId: string,
    action: PermissionAction,
    environmentId: string,
  ): Effect.Effect<void, PermissionDeniedError | DatabaseError> {
    return Effect.gen(this, function* () {
      const requiredRole = REQUIRED_ROLE_FOR_ACTION[action];
      const requiredLevel = ROLE_HIERARCHY[requiredRole];

      // Get the environment to find its project
      const environment = yield* Effect.tryPromise({
        try: async () => {
          const result = await this.db
            .select({ projectId: environments.projectId })
            .from(environments)
            .where(eq(environments.id, environmentId))
            .limit(1);
          return result[0] || null;
        },
        catch: (error) =>
          new DatabaseError({
            message: `Failed to fetch environment: ${error instanceof Error ? error.message : "Unknown error"}`,
          }),
      });

      if (!environment) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: `User does not have ${action} permission for this API key`,
          }),
        );
      }

      // Get the project to find its organization
      const project = yield* Effect.tryPromise({
        try: async () => {
          const result = await this.db
            .select({ organizationId: projects.organizationId })
            .from(projects)
            .where(eq(projects.id, environment.projectId))
            .limit(1);
          return result[0] || null;
        },
        catch: (error) =>
          new DatabaseError({
            message: `Failed to fetch project: ${error instanceof Error ? error.message : "Unknown error"}`,
          }),
      });

      if (!project) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: `User does not have ${action} permission for this API key`,
          }),
        );
      }

      // Check user's membership in the organization
      const membership = yield* Effect.tryPromise({
        try: async () => {
          const result = await this.db
            .select({ role: organizationMemberships.role })
            .from(organizationMemberships)
            .where(
              and(
                eq(organizationMemberships.userId, userId),
                eq(
                  organizationMemberships.organizationId,
                  project.organizationId,
                ),
              ),
            )
            .limit(1);
          return result[0] || null;
        },
        catch: (error) =>
          new DatabaseError({
            message: `Failed to check membership: ${error instanceof Error ? error.message : "Unknown error"}`,
          }),
      });

      if (!membership) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: `User does not have ${action} permission for this API key`,
          }),
        );
      }

      const userLevel = ROLE_HIERARCHY[membership.role];
      if (userLevel < requiredLevel) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: `User does not have ${action} permission for this API key`,
          }),
        );
      }
    });
  }

  /**
   * Check permission for an existing API key
   */
  protected checkPermission(
    userId: string,
    action: PermissionAction,
    apiKeyId: string,
  ): Effect.Effect<void, PermissionDeniedError | DatabaseError> {
    return Effect.gen(this, function* () {
      // Get the API key to find its environment
      const apiKey = yield* Effect.tryPromise({
        try: async () => {
          const result = await this.db
            .select({ environmentId: apiKeys.environmentId })
            .from(apiKeys)
            .where(eq(apiKeys.id, apiKeyId))
            .limit(1);
          return result[0] || null;
        },
        catch: (error) =>
          new DatabaseError({
            message: `Failed to fetch API key: ${error instanceof Error ? error.message : "Unknown error"}`,
          }),
      });

      if (!apiKey) {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message: `User does not have ${action} permission for this API key`,
          }),
        );
      }

      yield* this.checkEnvironmentPermission(
        userId,
        action,
        apiKey.environmentId,
      );
    });
  }

  /**
   * Create a new API key. Returns the plaintext key only at creation time.
   */
  create(
    data: { name: string; environmentId: string },
    userId: string,
  ): Effect.Effect<
    ApiKeyCreateResponse,
    AlreadyExistsError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      // Check permission on the environment
      yield* this.checkEnvironmentPermission(
        userId,
        "create",
        data.environmentId,
      );

      // Check for existing API key with same name in same environment
      const existing = yield* Effect.tryPromise({
        try: async () => {
          const result = await this.db
            .select({ id: apiKeys.id })
            .from(apiKeys)
            .where(
              and(
                eq(apiKeys.environmentId, data.environmentId),
                eq(apiKeys.name, data.name),
              ),
            )
            .limit(1);
          return result[0] || null;
        },
        catch: (error) =>
          new DatabaseError({
            message: `Failed to check existing API key: ${error instanceof Error ? error.message : "Unknown error"}`,
          }),
      });

      if (existing) {
        return yield* Effect.fail(
          new AlreadyExistsError({
            message: `API key with name "${data.name}" already exists in this environment`,
          }),
        );
      }

      // Generate the API key
      const plaintextKey = generateApiKey();
      const keyHash = hashApiKey(plaintextKey);
      const keyPrefix = getKeyPrefix(plaintextKey);

      // Create the API key
      const created = yield* Effect.tryPromise({
        try: async () => {
          const [result] = await this.db
            .insert(apiKeys)
            .values({
              name: data.name,
              keyHash,
              keyPrefix,
              environmentId: data.environmentId,
            })
            .returning({
              id: apiKeys.id,
              name: apiKeys.name,
              keyPrefix: apiKeys.keyPrefix,
              environmentId: apiKeys.environmentId,
              createdAt: apiKeys.createdAt,
              lastUsedAt: apiKeys.lastUsedAt,
            });
          return result;
        },
        catch: (error) =>
          new DatabaseError({
            message: `Failed to create API key: ${error instanceof Error ? error.message : "Unknown error"}`,
          }),
      });

      // Return with the plaintext key (only returned at creation)
      return {
        ...created,
        key: plaintextKey,
      };
    });
  }

  /**
   * Find all API keys for environments the user has access to
   */
  findAll(userId: string): Effect.Effect<PublicApiKey[], DatabaseError> {
    return Effect.tryPromise({
      try: async () => {
        const result = await this.db
          .select({
            id: apiKeys.id,
            name: apiKeys.name,
            keyPrefix: apiKeys.keyPrefix,
            environmentId: apiKeys.environmentId,
            createdAt: apiKeys.createdAt,
            lastUsedAt: apiKeys.lastUsedAt,
          })
          .from(apiKeys)
          .innerJoin(environments, eq(apiKeys.environmentId, environments.id))
          .innerJoin(projects, eq(environments.projectId, projects.id))
          .innerJoin(
            organizationMemberships,
            eq(projects.organizationId, organizationMemberships.organizationId),
          )
          .where(eq(organizationMemberships.userId, userId));
        return result;
      },
      catch: (error) =>
        new DatabaseError({
          message: `Failed to fetch API keys: ${error instanceof Error ? error.message : "Unknown error"}`,
        }),
    });
  }

  /**
   * Find all API keys for a specific environment
   */
  findByEnvironment(
    environmentId: string,
    userId: string,
  ): Effect.Effect<PublicApiKey[], PermissionDeniedError | DatabaseError> {
    return Effect.gen(this, function* () {
      // Check read permission
      yield* this.checkEnvironmentPermission(userId, "read", environmentId);

      return yield* Effect.tryPromise({
        try: async () => {
          const result = await this.db
            .select({
              id: apiKeys.id,
              name: apiKeys.name,
              keyPrefix: apiKeys.keyPrefix,
              environmentId: apiKeys.environmentId,
              createdAt: apiKeys.createdAt,
              lastUsedAt: apiKeys.lastUsedAt,
            })
            .from(apiKeys)
            .where(eq(apiKeys.environmentId, environmentId));
          return result;
        },
        catch: (error) =>
          new DatabaseError({
            message: `Failed to fetch API keys for environment: ${error instanceof Error ? error.message : "Unknown error"}`,
          }),
      });
    });
  }

  /**
   * Find an API key by ID with permission check
   */
  override findById(
    id: string,
    userId: string,
  ): Effect.Effect<
    PublicApiKey,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      yield* this.checkPermission(userId, "read", id);
      return yield* this.baseService.findById(id);
    });
  }

  /**
   * Delete an API key with permission check
   */
  override delete(
    id: string,
    userId: string,
  ): Effect.Effect<
    void,
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      yield* this.checkPermission(userId, "delete", id);
      yield* this.baseService.delete(id);
    });
  }

  /**
   * Verify an API key and return the associated environment.
   * This is used for API key authentication.
   */
  verifyApiKey(
    key: string,
  ): Effect.Effect<
    { apiKeyId: string; environmentId: string },
    NotFoundError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      const keyHash = hashApiKey(key);

      const result = yield* Effect.tryPromise({
        try: async () => {
          const [apiKey] = await this.db
            .select({
              id: apiKeys.id,
              environmentId: apiKeys.environmentId,
            })
            .from(apiKeys)
            .where(eq(apiKeys.keyHash, keyHash))
            .limit(1);

          if (apiKey) {
            // Update last used timestamp
            await this.db
              .update(apiKeys)
              .set({ lastUsedAt: new Date() })
              .where(eq(apiKeys.id, apiKey.id));
          }

          return apiKey || null;
        },
        catch: (error) =>
          new DatabaseError({
            message: `Failed to verify API key: ${error instanceof Error ? error.message : "Unknown error"}`,
          }),
      });

      if (!result) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "Invalid API key",
          }),
        );
      }

      return { apiKeyId: result.id, environmentId: result.environmentId };
    });
  }

  /**
   * Get a user with access to the environment's organization.
   * Returns the first owner/admin found for the organization.
   */
  getUserForEnvironment(
    environmentId: string,
  ): Effect.Effect<
    { id: string; email: string; name: string | null },
    NotFoundError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      const result = yield* Effect.tryPromise({
        try: async () => {
          // Query to find a user with access to this environment's organization
          // environment -> project -> organization -> membership -> user
          const rows = await this.db
            .select({
              userId: organizationMemberships.userId,
              email: schema.users.email,
              name: schema.users.name,
            })
            .from(environments)
            .innerJoin(projects, eq(environments.projectId, projects.id))
            .innerJoin(
              organizationMemberships,
              eq(
                projects.organizationId,
                organizationMemberships.organizationId,
              ),
            )
            .innerJoin(
              schema.users,
              eq(organizationMemberships.userId, schema.users.id),
            )
            .where(eq(environments.id, environmentId))
            .limit(1);

          return rows[0] || null;
        },
        catch: (error) =>
          new DatabaseError({
            message: `Failed to get user for environment: ${error instanceof Error ? error.message : "Unknown error"}`,
          }),
      });

      if (!result) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "No user found with access to this environment",
          }),
        );
      }

      return {
        id: result.userId,
        email: result.email,
        name: result.name,
      };
    });
  }
}
