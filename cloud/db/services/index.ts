export * from "@/db/services/base";
export * from "@/db/services/users";
export * from "@/db/services/sessions";
export * from "@/db/services/organizations";

import { Context } from "effect";
import { drizzle } from "drizzle-orm/postgres-js";
import postgres, { type Sql } from "postgres";
import type { PostgresJsDatabase } from "drizzle-orm/postgres-js";
import * as schema from "@/db/schema";
import { UserService } from "@/db/services/users";
import { SessionService } from "@/db/services/sessions";
import { OrganizationService } from "@/db/services/organizations";

export type Database = {
  readonly users: UserService;
  readonly sessions: SessionService;
  readonly organizations: OrganizationService;
  readonly close: () => Promise<void>;
};

export class DatabaseService extends Context.Tag("DatabaseService")<
  DatabaseService,
  Database
>() {}

export function getDatabase(
  connection: string | PostgresJsDatabase<typeof schema>,
): Database {
  let sql: Sql | null = null;

  const client =
    typeof connection === "string"
      ? (() => {
          sql = postgres(connection, {
            max: 5,
            fetch_types: false,
          });
          return drizzle(sql, { schema });
        })()
      : connection;

  const users = new UserService(client);
  const sessions = new SessionService(client);
  const organizations = new OrganizationService(client);

  return {
    users,
    sessions,
    organizations,
    close: async () => {
      if (sql) {
        await sql.end();
      }
    },
  };
}
