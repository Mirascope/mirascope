export * from "@/db/services/base";
export * from "@/db/services/users";
export * from "@/db/services/sessions";
export * from "@/db/services/organizations";
export * from "@/db/services/project-memberships";

import { Context } from "effect";
import { drizzle } from "drizzle-orm/postgres-js";
import postgres, { type Sql } from "postgres";
import type { PostgresJsDatabase } from "drizzle-orm/postgres-js";
import * as schema from "@/db/schema";
import { UserService } from "@/db/services/users";
import { SessionService } from "@/db/services/sessions";
import { OrganizationService } from "@/db/services/organizations";
import { ProjectMembershipService } from "@/db/services/project-memberships";

export type Database = {
  readonly users: UserService;
  readonly sessions: SessionService;
  readonly organizations: OrganizationService;
  readonly projectMemberships: ProjectMembershipService;
  /** @internal TODO: Remove when ProjectService is implemented (use db.projects instead) */
  readonly client: PostgresJsDatabase<typeof schema>;
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
  const projectMemberships = new ProjectMembershipService(
    client,
    organizations,
  );

  return {
    users,
    sessions,
    organizations,
    projectMemberships,
    client, // TODO: Remove when ProjectService is implemented
    close: async () => {
      if (sql) {
        await sql.end();
      }
    },
  };
}
