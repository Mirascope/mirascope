export * from "@/db/services/users";
export * from "@/db/services/sessions";

import { Context } from "effect";
import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import type { PostgresJsDatabase } from "drizzle-orm/postgres-js";
import * as schema from "@/db/schema";
import { UserService } from "@/db/services/users";
import { SessionService } from "@/db/services/sessions";

export type Database = {
  readonly users: UserService;
  readonly sessions: SessionService;
};

export class DatabaseService extends Context.Tag("DatabaseService")<
  DatabaseService,
  Database
>() {}

export function getDatabase(
  connection: string | PostgresJsDatabase<typeof schema>,
): Database {
  const client =
    typeof connection === "string"
      ? drizzle(
          postgres(connection, {
            max: 5, // Limit connections for Workers
            fetch_types: false, // Disable if not using array types (reduces latency)
          }),
          { schema },
        )
      : connection;

  const users = new UserService(client);
  const sessions = new SessionService(client);

  return {
    users,
    sessions,
  };
}
