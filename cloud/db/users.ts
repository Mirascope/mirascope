/**
 * @fileoverview Effect-native Users service.
 *
 * Implements CRUD operations for users using `yield* DrizzleORM` for
 * Effect-native database queries. Soft-delete is used for user deletion.
 *
 * @example
 * ```ts
 * const db = yield* Database;
 *
 * const user = yield* db.users.create({
 *   data: { email: "user@example.com", name: "User" },
 * });
 *
 * const found = yield* db.users.findById({ userId: user.id });
 * ```
 */

import { and, eq, isNull, sql } from "drizzle-orm";
import { Effect } from "effect";

import { BaseEffectService } from "@/db/base";
import { DrizzleORM } from "@/db/client";
import { users, type PublicUser, type NewUser } from "@/db/schema/users";
import { isUniqueConstraintError } from "@/db/utils";
import { AlreadyExistsError, DatabaseError, NotFoundError } from "@/errors";

/**
 * Type for user updates - excludes fields that shouldn't be directly updated.
 */
export type UpdateUser = Partial<Pick<NewUser, "email" | "name">>;

/**
 * Public fields to select from the users table.
 */
const publicFields = {
  id: users.id,
  email: users.email,
  name: users.name,
  accountType: users.accountType,
  deletedAt: users.deletedAt,
};

/**
 * Effect-native Users service.
 *
 * Provides CRUD operations for the users table with soft-delete support.
 * All methods use `yield* DrizzleORM` internally for database operations.
 */
export class Users extends BaseEffectService<
  PublicUser,
  "users/:userId",
  NewUser,
  UpdateUser
> {
  /**
   * Creates a new user.
   *
   * @throws AlreadyExistsError - If a user with the same email already exists
   * @throws DatabaseError - If the database operation fails
   */
  create({
    data,
  }: {
    data: NewUser;
  }): Effect.Effect<
    PublicUser,
    AlreadyExistsError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const [user]: PublicUser[] = yield* client
        .insert(users)
        .values({
          ...data,
          email: data.email.toLowerCase().trim(), // Normalize email
        })
        .returning(publicFields)
        .pipe(
          Effect.mapError((e): AlreadyExistsError | DatabaseError =>
            isUniqueConstraintError(e.cause)
              ? new AlreadyExistsError({
                  message: "User already exists",
                  resource: "user",
                })
              : new DatabaseError({
                  message: "Failed to create user",
                  cause: e,
                }),
          ),
        );

      return user;
    });
  }

  /**
   * Retrieves all users.
   *
   * @throws DatabaseError - If the database operation fails
   */
  findAll(): Effect.Effect<PublicUser[], DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      return yield* client
        .select(publicFields)
        .from(users)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to get users",
                cause: e,
              }),
          ),
        );
    });
  }

  /**
   * Retrieves a user by ID.
   *
   * NOTE: soft-deleted users will be found by ID.
   *
   * @throws NotFoundError - If the user doesn't exist
   * @throws DatabaseError - If the database operation fails
   */
  findById({
    userId,
  }: {
    userId: string;
  }): Effect.Effect<PublicUser, NotFoundError | DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const [user]: PublicUser[] = yield* client
        .select(publicFields)
        .from(users)
        .where(eq(users.id, userId))
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to get user",
                cause: e,
              }),
          ),
        );

      if (!user) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "User not found",
            resource: "user",
          }),
        );
      }

      return user;
    });
  }

  /**
   * Updates a user by ID.
   *
   * @throws NotFoundError - If the user doesn't exist
   * @throws DatabaseError - If the database operation fails
   */
  update({
    userId,
    data,
  }: {
    userId: string;
    data: UpdateUser;
  }): Effect.Effect<PublicUser, NotFoundError | DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const [updated]: PublicUser[] = yield* client
        .update(users)
        .set({ ...data, updatedAt: new Date() })
        .where(eq(users.id, userId))
        .returning(publicFields)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to update user",
                cause: e,
              }),
          ),
        );

      if (!updated) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "User not found",
            resource: "user",
          }),
        );
      }

      return updated;
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
   * @throws NotFoundError - If the user doesn't exist or is already deleted
   * @throws DatabaseError - If the database operation fails
   */
  delete({
    userId,
  }: {
    userId: string;
  }): Effect.Effect<void, NotFoundError | DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const [deleted]: { id: string }[] = yield* client
        .update(users)
        .set({
          email: `deleted-${userId}@deleted.local`,
          name: null,
          deletedAt: new Date(),
          updatedAt: new Date(),
        })
        .where(and(eq(users.id, userId), isNull(users.deletedAt)))
        .returning({ id: users.id })
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to delete user",
                cause: e,
              }),
          ),
        );

      if (!deleted) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "User not found",
            resource: "user",
          }),
        );
      }
    });
  }

  // ===========================================================================
  // Custom Methods
  // ===========================================================================

  /**
   * Finds a user by email.
   *
   * @param email - The email to search for
   * @returns The user if found
   * @throws NotFoundError - If no user with that email exists (or is deleted)
   * @throws DatabaseError - If the database operation fails
   */
  findByEmail(
    email: string,
  ): Effect.Effect<PublicUser, NotFoundError | DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const [user]: PublicUser[] = yield* client
        .select(publicFields)
        .from(users)
        .where(eq(users.email, email))
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to find user by email",
                cause: e,
              }),
          ),
        );

      if (!user) {
        return yield* Effect.fail(
          new NotFoundError({
            message: "User not found",
            resource: "user",
          }),
        );
      }

      return user;
    });
  }

  /**
   * Counts the total number of non-deleted users.
   *
   * @returns The count of active users
   * @throws DatabaseError - If the database operation fails
   */
  count(): Effect.Effect<number, DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const [{ count }]: { count: number }[] = yield* client
        .select({ count: sql<number>`count(*)::int` })
        .from(users)
        .where(isNull(users.deletedAt))
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to count users",
                cause: e,
              }),
          ),
        );

      return count ?? 0;
    });
  }
}
