import { Effect } from "effect";
import { eq } from "drizzle-orm";
import { BaseService } from "@/db/services/base";
import { DatabaseError, NotFoundError, InvalidSessionError } from "@/db/errors";
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
        yield* this.delete({ id: sessionId });
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
      } satisfies PublicUser);
    });
  }
}
