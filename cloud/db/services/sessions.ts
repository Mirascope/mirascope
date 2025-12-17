import { Effect } from "effect";
import { eq } from "drizzle-orm";
import { BaseService } from "@/db/services/base";
import { DatabaseError, NotFoundError, InvalidSessionError } from "@/db/errors";
import { sessions, type PublicSession } from "@/db/schema";
import { users, type PublicUser } from "@/db/schema/users";

export class SessionService extends BaseService<
  PublicSession,
  "users/:userId/sessions/:sessionId",
  typeof sessions
> {
  protected getTable() {
    return sessions;
  }

  protected getResourceName() {
    return "session";
  }

  protected getIdParamName() {
    return "sessionId" as const;
  }

  protected getPublicFields() {
    return {
      id: sessions.id,
      expiresAt: sessions.expiresAt,
    };
  }

  /**
   * Finds a user by their session ID.
   * @param sessionId - The ID of the session to find the user for.
   * @returns The user associated with the session.
   * @throws NotFoundError if the session is not found.
   * @throws InvalidSessionError if the session has expired.
   * @throws DatabaseError if the database operation fails.
   */
  findUserBySessionId(
    sessionId: string,
  ): Effect.Effect<
    PublicUser,
    NotFoundError | InvalidSessionError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      const sessionWithUser = yield* Effect.tryPromise({
        try: async () => {
          return await this.db
            .select({
              id: users.id,
              email: users.email,
              name: users.name,
              userId: sessions.userId,
              expiresAt: sessions.expiresAt,
            })
            .from(sessions)
            .innerJoin(users, eq(sessions.userId, users.id))
            .where(eq(sessions.id, sessionId))
            .limit(1);
        },
        catch: (error) =>
          new DatabaseError({
            message: "Failed to find session",
            cause: error,
          }),
      });

      if (sessionWithUser.length === 0) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Session with id ${sessionId} not found`,
            resource: "session",
          }),
        );
      }

      const userSession = sessionWithUser[0];

      if (new Date() > userSession.expiresAt) {
        yield* this.delete({ userId: userSession.userId, sessionId });
        return yield* Effect.fail(
          new InvalidSessionError({
            message: "Session expired",
            sessionId,
          }),
        );
      }

      return yield* Effect.succeed({
        id: userSession.id,
        email: userSession.email,
        name: userSession.name,
        deletedAt: null, // this is getting deleted
      } satisfies PublicUser);
    });
  }

  /**
   * Deletes a session by its ID.
   * @param sessionId - The ID of the session to delete.
   * @returns The deleted session.
   * @throws NotFoundError if the session is not found.
   * @throws DatabaseError if the database operation fails.
   */
  deleteBySessionId(
    sessionId: string,
  ): Effect.Effect<void, NotFoundError | DatabaseError> {
    return Effect.gen(this, function* () {
      const deleted = yield* Effect.tryPromise({
        try: async () => {
          const [deleted] = await this.db
            .delete(sessions)
            .where(eq(sessions.id, sessionId))
            .returning({ id: sessions.id });
          return deleted;
        },
        catch: (error) =>
          new DatabaseError({
            message: "Failed to delete session",
            cause: error,
          }),
      });

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
