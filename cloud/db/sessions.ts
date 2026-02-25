/**
 * @fileoverview Effect-native Sessions service.
 *
 * Provides CRUD operations for the sessions table. Sessions are linked to users
 * and have expiration times. Unlike users, sessions use hard deletes.
 *
 * @example
 * ```ts
 * const db = yield* Database;
 *
 * // Create a session for a user
 * const session = yield* db.sessions.create({
 *   userId: user.id,
 *   data: { userId: user.id, expiresAt: new Date(Date.now() + 86400000) },
 * });
 *
 * // Find user by session (validates expiration)
 * const user = yield* db.sessions.findUserBySessionId(session.id);
 * ```
 */

import { and, eq } from "drizzle-orm";
import { Effect } from "effect";

import type { PublicUser } from "@/db/schema/users";

import { BaseEffectService } from "@/db/base";
import { DrizzleORM } from "@/db/client";
import {
  sessions,
  users,
  type PublicSession,
  type NewSession,
} from "@/db/schema";
import {
  DatabaseError,
  DeletedUserError,
  InvalidSessionError,
  NotFoundError,
} from "@/errors";

/**
 * Update type for sessions - only expiresAt can be updated.
 */
export type UpdateSession = Pick<NewSession, "expiresAt">;

/**
 * Public fields to select from the sessions table.
 */
const publicFields = {
  id: sessions.id,
  expiresAt: sessions.expiresAt,
};

/**
 * Type for selecting `PublicUser` and `PublicSession` on their inner join.
 */
export type PublicUserWithExpiration = PublicUser & { expiresAt: Date };

/**
 * Effect-native Sessions service.
 *
 * Provides CRUD operations for the sessions table. Sessions are scoped to users
 * via the path `users/:userId/sessions/:sessionId`.
 */
export class Sessions extends BaseEffectService<
  PublicSession,
  "users/:userId/sessions/:sessionId",
  NewSession,
  UpdateSession
> {
  // ===========================================================================
  // CRUD Operations
  // ===========================================================================

  /**
   * Creates a new session for a user.
   *
   * @param userId - The user's ID (parent parameter)
   * @param data - Session data including userId and expiresAt
   * @returns The created session with id and expiresAt
   * @throws DatabaseError - If the database operation fails
   */
  create({
    userId,
    data,
  }: {
    userId: string;
    data: NewSession;
  }): Effect.Effect<PublicSession, DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const [session]: PublicSession[] = yield* client
        .insert(sessions)
        .values({ ...data, userId })
        .returning(publicFields)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to create session",
                cause: e,
              }),
          ),
        );

      return session;
    });
  }

  /**
   * Retrieves all sessions for a user.
   *
   * @param userId - The user's ID to find sessions for
   * @returns Array of sessions for the user
   * @throws DatabaseError - If the database operation fails
   */
  findAll({
    userId,
  }: {
    userId: string;
  }): Effect.Effect<PublicSession[], DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      return yield* client
        .select(publicFields)
        .from(sessions)
        .where(eq(sessions.userId, userId))
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to find all sessions",
                cause: e,
              }),
          ),
        );
    });
  }

  /**
   * Finds a session by its ID.
   *
   * @param userId - The user's ID (for path consistency)
   * @param sessionId - The session's ID
   * @returns The session if found
   * @throws NotFoundError - If the session doesn't exist
   * @throws DatabaseError - If the database operation fails
   */
  findById({
    userId,
    sessionId,
  }: {
    userId: string;
    sessionId: string;
  }): Effect.Effect<PublicSession, NotFoundError | DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const [session]: PublicSession[] = yield* client
        .select(publicFields)
        .from(sessions)
        .where(and(eq(sessions.id, sessionId), eq(sessions.userId, userId)))
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to find session",
                cause: e,
              }),
          ),
        );

      if (!session) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `session with sessionId ${sessionId} not found for user with userId ${userId}`,
            resource: "session",
          }),
        );
      }

      return session;
    });
  }

  /**
   * Updates a session's expiration time.
   *
   * @param userId - The user's ID
   * @param sessionId - The session's ID
   * @param data - Update data containing new expiresAt
   * @returns The updated session
   * @throws NotFoundError - If the session doesn't exist
   * @throws DatabaseError - If the database operation fails
   */
  update({
    userId,
    sessionId,
    data,
  }: {
    userId: string;
    sessionId: string;
    data: UpdateSession;
  }): Effect.Effect<PublicSession, NotFoundError | DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const [updated]: PublicSession[] = yield* client
        .update(sessions)
        .set({ ...data, updatedAt: new Date() })
        .where(and(eq(sessions.id, sessionId), eq(sessions.userId, userId)))
        .returning(publicFields)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to update session",
                cause: e,
              }),
          ),
        );

      if (!updated) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `session with sessionId ${sessionId} not found for user with userId ${userId}`,
            resource: "session",
          }),
        );
      }

      return updated;
    });
  }

  /**
   * Deletes a session (hard delete).
   *
   * @param userId - The user's ID
   * @param sessionId - The session's ID
   * @throws NotFoundError - If the session doesn't exist
   * @throws DatabaseError - If the database operation fails
   */
  delete({
    userId,
    sessionId,
  }: {
    userId: string;
    sessionId: string;
  }): Effect.Effect<void, NotFoundError | DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const [deleted]: { id: string }[] = yield* client
        .delete(sessions)
        .where(and(eq(sessions.id, sessionId), eq(sessions.userId, userId)))
        .returning({ id: sessions.id })
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to delete session",
                cause: e,
              }),
          ),
        );

      if (!deleted) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `session with sessionId ${sessionId} not found for user with userId ${userId}`,
            resource: "session",
          }),
        );
      }
    });
  }

  // ===========================================================================
  // Custom Methods
  // ===========================================================================

  /**
   * Finds a user by their session ID and validates the session.
   *
   * This method:
   * 1. Looks up the session and joins with users
   * 2. Returns NotFoundError if session doesn't exist
   * 3. Returns InvalidSessionError if session is expired
   * 4. Returns the user if session is valid (including soft-deleted users)
   *
   * @param sessionId - The session ID to look up
   * @returns The user associated with the session
   * @throws NotFoundError - If the session doesn't exist
   * @throws InvalidSessionError - If the session has expired
   * @throws DatabaseError - If the database operation fails
   */
  findUserBySessionId(
    sessionId: string,
  ): Effect.Effect<
    PublicUser,
    NotFoundError | DeletedUserError | InvalidSessionError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      const client = yield* DrizzleORM;

      const [userWithExpiration]: PublicUserWithExpiration[] = yield* client
        .select({
          id: users.id,
          email: users.email,
          name: users.name,
          deletedAt: users.deletedAt,
          expiresAt: sessions.expiresAt,
        })
        .from(sessions)
        .innerJoin(users, eq(sessions.userId, users.id))
        .where(eq(sessions.id, sessionId))
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to find session",
                cause: e,
              }),
          ),
        );

      if (!userWithExpiration) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Session with id ${sessionId} not found`,
            resource: "session",
          }),
        );
      }

      if (userWithExpiration.deletedAt !== null) {
        return yield* Effect.fail(
          new DeletedUserError({
            message: "This user has been deleted",
            resource: "users",
          }),
        );
      }

      if (new Date() > userWithExpiration.expiresAt) {
        return yield* Effect.fail(
          new InvalidSessionError({
            message: "Session expired",
            sessionId,
          }),
        );
      }

      return {
        id: userWithExpiration.id,
        email: userWithExpiration.email,
        name: userWithExpiration.name,
        deletedAt: userWithExpiration.deletedAt,
      } satisfies PublicUser;
    });
  }

  /**
   * Deletes a session by its ID only (without requiring userId).
   *
   * This is useful for logout operations where you only have the session ID.
   *
   * @param sessionId - The session ID to delete
   * @throws NotFoundError - If the session doesn't exist
   * @throws DatabaseError - If the database operation fails
   */
  deleteBySessionId(
    sessionId: string,
  ): Effect.Effect<void, NotFoundError | DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const [deleted]: { id: string }[] = yield* client
        .delete(sessions)
        .where(eq(sessions.id, sessionId))
        .returning({ id: sessions.id })
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to delete session",
                cause: e,
              }),
          ),
        );

      if (!deleted) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Session with sessionId ${sessionId} not found`,
            resource: "session",
          }),
        );
      }
    });
  }
}
