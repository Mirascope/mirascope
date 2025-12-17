export * from "@/db/services/base";
export * from "@/db/services/organizations";
export * from "@/db/services/project-memberships";
export * from "@/db/services/projects";

import { Context } from "effect";
import { drizzle } from "drizzle-orm/postgres-js";
import postgres, { type Sql } from "postgres";
import type { PostgresJsDatabase } from "drizzle-orm/postgres-js";
import * as schema from "@/db/schema";
import { Users } from "@/db/users";
import { type Ready, makeReady } from "@/db/base";
import { type DrizzleORMClient } from "@/db/client";
import { Sessions } from "@/db/sessions";
import { OrganizationService } from "@/db/services/organizations";
import { ProjectService } from "@/db/services/projects";

export type Database = {
  readonly users: Ready<Users>;
  readonly sessions: Ready<Sessions>;
  readonly organizations: OrganizationService;
  readonly projects: ProjectService;
  /** @internal TODO: Remove when tests are updated to use db.projects */
  readonly client: PostgresJsDatabase<typeof schema>;
  readonly close: () => Promise<void>;
};

export class DatabaseService extends Context.Tag("DatabaseService")<
  DatabaseService,
  Database
>() {}

/**
 * Wraps a PostgresJsDatabase as a DrizzleORMClient for compatibility with makeReady.
 *
 * The legacy DatabaseService uses postgres-js directly, while the new Users service
 * expects DrizzleORMClient (from @effect/sql-drizzle). Since both are Drizzle instances
 * with the same query methods, we can cast with a stub withTransaction.
 */
function asDrizzleORMClient(
  client: PostgresJsDatabase<typeof schema>,
): DrizzleORMClient {
  return Object.assign(client, {
    // Stub - legacy services don't use Effect transactions
    withTransaction: () => {
      throw new Error(
        "withTransaction is not supported in legacy DatabaseService. Use EffectDatabase instead.",
      );
    },
  }) as unknown as DrizzleORMClient;
}

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

  // Wrap the client for compatibility with the new Users service
  const drizzleORMClient = asDrizzleORMClient(client);
  const users = makeReady(drizzleORMClient, new Users());
  const sessions = makeReady(drizzleORMClient, new Sessions());
  const organizations = new OrganizationService(client);
  const projects = new ProjectService(client, organizations.memberships);

  return {
    users,
    sessions,
    organizations,
    projects,
    client, // TODO: Remove when tests are updated to use db.projects
    close: async () => {
      if (sql) {
        await sql.end();
      }
    },
  };
}
