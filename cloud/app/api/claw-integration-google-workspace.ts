import { eq } from "drizzle-orm";
import { Effect } from "effect";

import { DrizzleORM } from "@/db/client";
import {
  clawIntegrationGoogleWorkspace,
  type PublicClawIntegrationGoogleWorkspace,
} from "@/db/schema";
import { DatabaseError, NotFoundError } from "@/errors";

/**
 * Retrieves a Google Workspace connection for a given claw.
 */
export function getConnectionByClaw(
  clawId: string,
): Effect.Effect<
  PublicClawIntegrationGoogleWorkspace,
  NotFoundError | DatabaseError,
  DrizzleORM
> {
  return Effect.gen(function* () {
    const client = yield* DrizzleORM;

    const [connection] = yield* client
      .select({
        id: clawIntegrationGoogleWorkspace.id,
        clawId: clawIntegrationGoogleWorkspace.clawId,
        userId: clawIntegrationGoogleWorkspace.userId,
        scopes: clawIntegrationGoogleWorkspace.scopes,
        connectedEmail: clawIntegrationGoogleWorkspace.connectedEmail,
        tokenExpiresAt: clawIntegrationGoogleWorkspace.tokenExpiresAt,
        createdAt: clawIntegrationGoogleWorkspace.createdAt,
        updatedAt: clawIntegrationGoogleWorkspace.updatedAt,
      })
      .from(clawIntegrationGoogleWorkspace)
      .where(eq(clawIntegrationGoogleWorkspace.clawId, clawId))
      .limit(1)
      .pipe(
        Effect.mapError(
          (e) =>
            new DatabaseError({
              message: "Failed to query Google Workspace connection",
              cause: e,
            }),
        ),
      );

    if (!connection) {
      return yield* Effect.fail(
        new NotFoundError({
          message: "No Google Workspace connection found for this claw",
          resource: "google_workspace_connection",
        }),
      );
    }

    return connection;
  });
}

/**
 * Deletes a Google Workspace connection for a given claw.
 */
export function deleteConnection(
  clawId: string,
): Effect.Effect<void, DatabaseError, DrizzleORM> {
  return Effect.gen(function* () {
    const client = yield* DrizzleORM;

    yield* client
      .delete(clawIntegrationGoogleWorkspace)
      .where(eq(clawIntegrationGoogleWorkspace.clawId, clawId))
      .pipe(
        Effect.mapError(
          (e) =>
            new DatabaseError({
              message: "Failed to delete Google Workspace connection",
              cause: e,
            }),
        ),
      );
  });
}

/**
 * Checks if a Google Workspace connection exists for a given claw.
 */
export function hasConnection(
  clawId: string,
): Effect.Effect<boolean, DatabaseError, DrizzleORM> {
  return Effect.gen(function* () {
    const client = yield* DrizzleORM;

    const [row] = yield* client
      .select({ id: clawIntegrationGoogleWorkspace.id })
      .from(clawIntegrationGoogleWorkspace)
      .where(eq(clawIntegrationGoogleWorkspace.clawId, clawId))
      .limit(1)
      .pipe(
        Effect.mapError(
          (e) =>
            new DatabaseError({
              message: "Failed to check Google Workspace connection",
              cause: e,
            }),
        ),
      );

    return !!row;
  });
}
