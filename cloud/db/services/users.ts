import { Effect } from "effect";
import { and, eq, isNull, sql } from "drizzle-orm";
import { BaseService } from "@/db/services/base";
import { DatabaseError, NotFoundError } from "@/db/errors";
import { users, type PublicUser } from "@/db/schema/users";

export class UserService extends BaseService<
  PublicUser,
  "users/:userId",
  typeof users
> {
  protected getTable() {
    return users;
  }

  protected getResourceName() {
    return "user";
  }

  protected getIdParamName() {
    return "userId" as const;
  }

  protected getPublicFields() {
    return {
      id: users.id,
      email: users.email,
      name: users.name,
    };
  }

  // ---------------------------------------------------------------------------
  // CRUD Overrides (filter out soft-deleted users)
  // ---------------------------------------------------------------------------

  /**
   * Retrieves all non-deleted users.
   *
   * Overrides base implementation to filter out soft-deleted users.
   */
  override findAll(): Effect.Effect<PublicUser[], DatabaseError> {
    return Effect.tryPromise({
      try: async () => {
        const results = await this.db
          .select(this.getPublicFields())
          .from(users)
          .where(isNull(users.deletedAt));
        return results as PublicUser[];
      },
      catch: (error) =>
        new DatabaseError({
          message: "Failed to get users",
          cause: error,
        }),
    });
  }

  /**
   * Retrieves a non-deleted user by ID.
   *
   * Overrides base implementation to filter out soft-deleted users.
   *
   * @throws NotFoundError - If the user doesn't exist or is deleted
   */
  override findById({
    userId,
  }: {
    userId: string;
  }): Effect.Effect<PublicUser, NotFoundError | DatabaseError> {
    return Effect.gen(this, function* () {
      const result = yield* Effect.tryPromise({
        try: async () => {
          const [user] = await this.db
            .select(this.getPublicFields())
            .from(users)
            .where(and(eq(users.id, userId), isNull(users.deletedAt)))
            .limit(1);
          return user as PublicUser | undefined;
        },
        catch: (error) =>
          new DatabaseError({
            message: "Failed to get user",
            cause: error,
          }),
      });

      if (!result) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "User not found",
            resource: "user",
          }),
        );
      }
      return result;
    });
  }

  /**
   * Soft-deletes a user by removing PII and setting deletedAt timestamp.
   *
   * The user's UUID is preserved, but:
   * - email is replaced with `deleted-{userId}@deleted.local`
   * - name is set to null
   * - deletedAt is set to the current timestamp
   *
   * @param args.userId - The ID of the user to delete
   * @throws NotFoundError - If the user doesn't exist or is already deleted
   * @throws DatabaseError - If the database operation fails
   */
  override delete({
    userId,
  }: {
    userId: string;
  }): Effect.Effect<void, NotFoundError | DatabaseError> {
    return Effect.gen(this, function* () {
      const result = yield* Effect.tryPromise({
        try: async () => {
          const [updated] = await this.db
            .update(users)
            .set({
              email: `deleted-${userId}@deleted.local`,
              name: null,
              deletedAt: new Date(),
              updatedAt: new Date(),
            })
            .where(and(eq(users.id, userId), isNull(users.deletedAt)))
            .returning({ id: users.id });
          return updated;
        },
        catch: (error) =>
          new DatabaseError({
            message: "Failed to delete user",
            cause: error,
          }),
      });

      if (!result) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "User not found",
            resource: "user",
          }),
        );
      }
    });
  }

  // ---------------------------------------------------------------------------
  // Custom Methods
  // ---------------------------------------------------------------------------

  /**
   * Creates or updates a user.
   * @param data - The data to create or update the user with.
   * @returns The created or updated user.
   * @throws DatabaseError if the database operation fails.
   */
  createOrUpdate(data: {
    email: string;
    name?: string | null;
  }): Effect.Effect<PublicUser, DatabaseError> {
    return Effect.gen(this, function* () {
      // upsert user
      yield* Effect.tryPromise({
        try: async () => {
          await this.db
            .insert(users)
            .values(data)
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

      // Note: Drizzle's `onConflictDoUpdate` always returns `undefined` in the result array
      // (even though TypeScript types suggest it might return a value). This is a known
      // Drizzle behavior. We always perform a subsequent select to retrieve the user data
      // after the upsert operation.
      const user = yield* Effect.tryPromise({
        try: async () => {
          const [result] = await this.db
            .select(this.getPublicFields())
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

      if (!user) {
        return yield* Effect.fail(
          new DatabaseError({
            message: "Failed to create or update user",
          }),
        );
      }
      return user;
    });
  }
}
