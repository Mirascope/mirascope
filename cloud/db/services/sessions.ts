import { Effect } from "effect";
import { eq } from "drizzle-orm";
import { BaseService } from "@/db/services/base";
import { DatabaseError, NotFoundError, InvalidSessionError } from "@/db/errors";
import { sessions, type PublicSession } from "@/db/schema";
import { users, type PublicUser } from "@/db/schema/users";

type UserSession = PublicSession & PublicUser;

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
    const fetchSessionWithUser = Effect.tryPromise({
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

    const handleEmptyResult = (result: UserSession[]) => {
      if (result.length === 0) {
        return Effect.fail(
          new NotFoundError({
            message: `Session with id ${sessionId} not found`,
            resource: "session",
          }),
        );
      }
      return Effect.succeed(result[0]);
    };

    const handleExpiredSession = (userSession: UserSession) => {
      if (new Date() > userSession.expiresAt) {
        // Delete expired session before returning error
        return this.delete(sessionId).pipe(
          Effect.flatMap(() =>
            Effect.fail(
              new InvalidSessionError({
                message: "Session expired",
                sessionId,
              }),
            ),
          ),
        );
      }
      return Effect.succeed(userSession);
    };

    const transformToPublicUser = (userSession: UserSession) => {
      return Effect.succeed({
        id: userSession.id,
        email: userSession.email,
        name: userSession.name,
      } satisfies PublicUser);
    };

    return fetchSessionWithUser.pipe(
      Effect.flatMap(handleEmptyResult),
      Effect.flatMap(handleExpiredSession),
      Effect.flatMap(transformToPublicUser),
    );
  }
}
