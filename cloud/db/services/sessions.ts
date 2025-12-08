import { Effect } from "effect";
import { eq } from "drizzle-orm";
import { BaseService } from "@/db/services/base";
import { DatabaseError, NotFoundError } from "@/db/errors";
import { sessions, type PublicSession } from "@/db/schema";
import { users, type PublicUser } from "@/db/schema/users";

export class SessionService extends BaseService<
  PublicSession,
  string,
  typeof sessions
> {
  protected getTable() {
    return sessions;
  }

  protected getResourceName() {
    return "session";
  }

  protected getPublicFields() {
    return {
      id: sessions.id,
      expiresAt: sessions.expiresAt,
    };
  }

  /**
   * Check if a session is valid (exists and not expired)
   * Automatically deletes expired sessions
   */
  isValid(sessionId: string): Effect.Effect<boolean, DatabaseError> {
    return Effect.gen(this, function* () {
      const session = yield* Effect.tryPromise({
        try: async () => {
          const [result] = await this.db
            .select({
              id: sessions.id,
              expiresAt: sessions.expiresAt,
            })
            .from(sessions)
            .where(eq(sessions.id, sessionId))
            .limit(1);

          return result;
        },
        catch: (error) =>
          new DatabaseError({
            message: "Failed to check session validity",
            cause: error,
          }),
      });

      if (!session) {
        return false;
      }

      if (new Date() > session.expiresAt) {
        yield* Effect.either(this.delete(sessionId));
        return false;
      }

      return true;
    });
  }

  /**
   * Find user by session ID
   * Handles validity checks internally - returns user only if session is valid
   * Automatically deletes expired sessions
   */
  findUserBySessionId(
    sessionId: string,
  ): Effect.Effect<PublicUser, NotFoundError | DatabaseError> {
    return Effect.gen(this, function* () {
      const result = yield* Effect.tryPromise({
        try: async () => {
          const queryResult = await this.db
            .select({
              id: users.id,
              email: users.email,
              name: users.name,
              expiresAt: sessions.expiresAt,
            })
            .from(sessions)
            .innerJoin(users, eq(sessions.userId, users.id))
            .where(eq(sessions.id, sessionId))
            .limit(1);

          return queryResult;
        },
        catch: (error) => {
          return new DatabaseError({
            message: "Failed to find session",
            cause: error,
          });
        },
      });

      if (result.length === 0) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Session with id ${sessionId} not found`,
            resource: "session",
          }),
        );
      }

      const sessionData = result[0];

      if (new Date() > sessionData.expiresAt) {
        yield* this.delete(sessionId);
        return yield* Effect.fail(
          new NotFoundError({
            message: "Session expired",
            resource: "session",
          }),
        );
      }

      return {
        id: sessionData.id,
        email: sessionData.email,
        name: sessionData.name,
      };
    });
  }
}
