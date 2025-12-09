import { Effect } from "effect";
import { eq, sql } from "drizzle-orm";
import { BaseService } from "@/db/services/base";
import { DatabaseError } from "@/db/errors";
import { users, type PublicUser } from "@/db/schema/users";

export class UserService extends BaseService<PublicUser, string, typeof users> {
  protected getTable() {
    return users;
  }

  protected getResourceName() {
    return "user";
  }

  protected getPublicFields() {
    return {
      id: users.id,
      email: users.email,
      name: users.name,
    };
  }

  createOrUpdate(data: {
    email: string;
    name?: string | null;
  }): Effect.Effect<PublicUser, DatabaseError> {
    // Note: Drizzle's `onConflictDoUpdate` always returns `undefined` in the result array
    // (even though TypeScript types suggest it might return a value). This is a known
    // Drizzle behavior. We always perform a subsequent select to retrieve the user data
    // after the upsert operation.
    const upsertUser = Effect.tryPromise({
      try: async () => {
        await this.db
          .insert(users)
          .values({
            email: data.email,
            name: data.name,
          })
          .onConflictDoUpdate({
            target: users.email,
            set: {
              name: data.name,
              updatedAt: new Date(),
            },
            where: sql`${users.name} IS DISTINCT FROM ${data.name ?? null}`,
          });
      },
      catch: (error) =>
        new DatabaseError({
          message: "Failed to create or update user",
          cause: error,
        }),
    });

    const fetchUser = Effect.tryPromise({
      try: async () => {
        const publicFields = this.getPublicFields();
        const [result] = await this.db
          .select(publicFields)
          .from(users)
          .where(eq(users.email, data.email))
          .limit(1);

        return result as PublicUser | undefined;
      },
      catch: (error) =>
        new DatabaseError({
          message: "Failed to create or update user",
          cause: error,
        }),
    });

    const handleUserNotFound = (user: PublicUser | undefined) => {
      if (!user) {
        return Effect.fail(
          new DatabaseError({
            message: "Failed to create or update user",
          }),
        );
      }
      return Effect.succeed(user);
    };

    return upsertUser.pipe(
      Effect.andThen(fetchUser),
      Effect.flatMap(handleUserNotFound),
    );
  }
}
