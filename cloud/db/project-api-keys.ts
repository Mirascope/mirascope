/**
 * @fileoverview Effect-native Project API Keys (BYOK) service.
 *
 * Provides authenticated CRUD operations for project-level BYOK API keys
 * with AES-256-GCM encryption at rest. Keys are encrypted using the same
 * encryption infrastructure as claw secrets (`cloud/claws/crypto.ts`).
 *
 * ## Architecture
 *
 * ```
 * ProjectApiKeys (authenticated)
 *   └── authorization via ProjectMemberships.getRole()
 * ```
 *
 * ## Permissions
 *
 * All operations require project ADMIN role. Organization OWNER/ADMIN roles
 * have implicit ADMIN access through existing role hierarchy.
 *
 * ## Security
 *
 * - Keys are encrypted with AES-256-GCM using versioned encryption keys
 * - Only the last 4 characters (keySuffix) are stored in plaintext for display
 * - Decryption only happens at router proxy time via `get()`
 * - `list()` never returns decrypted keys
 */

import { and, eq } from "drizzle-orm";
import { Effect } from "effect";

import type { ProviderName } from "@/api/router/providers";

import { encryptSecrets, decryptSecrets } from "@/claws/crypto";
import { DrizzleORM } from "@/db/client";
import { ProjectMemberships } from "@/db/project-memberships";
import {
  projectApiKeys,
  type PublicProjectApiKey,
  type ProjectRole,
} from "@/db/schema";
import { DatabaseError, NotFoundError, PermissionDeniedError } from "@/errors";
import { Settings } from "@/settings";

/**
 * Effect-native Project API Keys (BYOK) service.
 *
 * Manages encrypted provider API keys at the project level. One key per
 * provider per project, stored with AES-256-GCM encryption.
 */
export class ProjectApiKeys {
  private readonly projectMemberships: ProjectMemberships;

  constructor(projectMemberships: ProjectMemberships) {
    this.projectMemberships = projectMemberships;
  }

  // ---------------------------------------------------------------------------
  // Authorization
  // ---------------------------------------------------------------------------

  /**
   * Verifies the user has ADMIN access to the project.
   */
  private authorize({
    userId,
    organizationId,
    projectId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
  }): Effect.Effect<
    ProjectRole,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const role = yield* this.projectMemberships.getRole({
        userId,
        organizationId,
        projectId,
      });
      if (role !== "ADMIN") {
        return yield* Effect.fail(
          new PermissionDeniedError({
            message:
              "You do not have permission to manage BYOK keys for this project",
            resource: "project_api_keys",
          }),
        );
      }
      return role;
    });
  }

  // ---------------------------------------------------------------------------
  // Public API
  // ---------------------------------------------------------------------------

  /**
   * Set (upsert) a BYOK key for a provider.
   *
   * Encrypts the key with AES-256-GCM and stores the last 4 characters
   * as `keySuffix` for display purposes.
   */
  set({
    userId,
    organizationId,
    projectId,
    provider,
    key,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    provider: ProviderName;
    key: string;
  }): Effect.Effect<
    PublicProjectApiKey,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM | Settings
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({ userId, organizationId, projectId });

      const client = yield* DrizzleORM;

      // Encrypt the key using the shared crypto module
      const encrypted = yield* encryptSecrets({ key }).pipe(
        Effect.mapError(
          (e) =>
            new DatabaseError({
              message: "Failed to encrypt BYOK key",
              cause: e,
            }),
        ),
      );

      const keySuffix = key.slice(-4);
      const now = new Date();

      const [result] = yield* client
        .insert(projectApiKeys)
        .values({
          projectId,
          provider,
          encryptedKey: encrypted.ciphertext,
          nonce: encrypted.keyId, // Store the keyId as nonce for decryption lookup
          keySuffix,
          createdAt: now,
          updatedAt: now,
        })
        .onConflictDoUpdate({
          target: [projectApiKeys.projectId, projectApiKeys.provider],
          set: {
            encryptedKey: encrypted.ciphertext,
            nonce: encrypted.keyId,
            keySuffix,
            updatedAt: now,
          },
        })
        .returning({
          provider: projectApiKeys.provider,
          keySuffix: projectApiKeys.keySuffix,
          updatedAt: projectApiKeys.updatedAt,
        })
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to set BYOK key",
                cause: e,
              }),
          ),
        );

      return result;
    });
  }

  /**
   * Get the decrypted BYOK key for a provider.
   *
   * **Internal only** — used by the router at proxy time. Never exposed via API.
   *
   * @returns The decrypted API key string, or null if no key is configured.
   */
  get({
    projectId,
    provider,
  }: {
    projectId: string;
    provider: ProviderName;
  }): Effect.Effect<string | null, DatabaseError, DrizzleORM | Settings> {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      const [row] = yield* client
        .select({
          encryptedKey: projectApiKeys.encryptedKey,
          nonce: projectApiKeys.nonce,
        })
        .from(projectApiKeys)
        .where(
          and(
            eq(projectApiKeys.projectId, projectId),
            eq(projectApiKeys.provider, provider),
          ),
        )
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to get BYOK key",
                cause: e,
              }),
          ),
        );

      if (!row) {
        return null;
      }

      // Decrypt using the keyId stored in the nonce column
      const decrypted = yield* decryptSecrets(row.encryptedKey, row.nonce).pipe(
        Effect.mapError(
          (e) =>
            new DatabaseError({
              message: "Failed to decrypt BYOK key",
              cause: e,
            }),
        ),
      );

      return decrypted.key ?? null;
    });
  }

  /**
   * Delete a BYOK key for a provider.
   */
  delete({
    userId,
    organizationId,
    projectId,
    provider,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    provider: ProviderName;
  }): Effect.Effect<
    void,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({ userId, organizationId, projectId });

      const client = yield* DrizzleORM;

      const result = yield* client
        .delete(projectApiKeys)
        .where(
          and(
            eq(projectApiKeys.projectId, projectId),
            eq(projectApiKeys.provider, provider),
          ),
        )
        .returning({ id: projectApiKeys.id })
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to delete BYOK key",
                cause: e,
              }),
          ),
        );

      if (result.length === 0) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `No BYOK key found for provider '${provider}'`,
            resource: "project_api_keys",
          }),
        );
      }
    });
  }

  /**
   * List all BYOK keys for a project (metadata only, no decrypted keys).
   */
  list({
    userId,
    organizationId,
    projectId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
  }): Effect.Effect<
    PublicProjectApiKey[],
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({ userId, organizationId, projectId });

      const client = yield* DrizzleORM;

      return yield* client
        .select({
          provider: projectApiKeys.provider,
          keySuffix: projectApiKeys.keySuffix,
          updatedAt: projectApiKeys.updatedAt,
        })
        .from(projectApiKeys)
        .where(eq(projectApiKeys.projectId, projectId))
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to list BYOK keys",
                cause: e,
              }),
          ),
        );
    });
  }
}
