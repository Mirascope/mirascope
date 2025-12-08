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

  /**
   * Create or update a user by email (upsert)
   */
  createOrUpdate(data: {
    email: string;
    name?: string | null;
  }): Effect.Effect<PublicUser, DatabaseError> {
    return Effect.tryPromise({
      try: async () => {
        const publicFields = this.getPublicFields();

        const [result] = await this.db
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
          })
          .returning(publicFields);

        if (!result) {
          const [existing] = await this.db
            .select(publicFields)
            .from(users)
            .where(eq(users.email, data.email))
            .limit(1);

          if (!existing) {
            throw new Error("Failed to create or update user");
          }

          return existing;
        }

        return result;
      },
      catch: (error) => {
        return new DatabaseError({
          message: "Failed to create or update user",
          cause: error,
        });
      },
    });
  }
}
