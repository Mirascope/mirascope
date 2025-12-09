export * from "@/db/services/base";
export * from "@/db/services/users";
export * from "@/db/services/sessions";
export * from "@/db/services/organizations";
export * from "@/db/services/projects";
export * from "@/db/services/environments";
export * from "@/db/services/api-keys";

import { Context } from "effect";
import { drizzle } from "drizzle-orm/postgres-js";
import postgres, { type Sql } from "postgres";
import type { PostgresJsDatabase } from "drizzle-orm/postgres-js";
import * as schema from "@/db/schema";
import { UserService } from "@/db/services/users";
import { SessionService } from "@/db/services/sessions";
import { OrganizationService } from "@/db/services/organizations";
import { ProjectService } from "@/db/services/projects";
import { EnvironmentService } from "@/db/services/environments";
import { ApiKeyService } from "@/db/services/api-keys";

export type Database = {
  readonly users: UserService;
  readonly sessions: SessionService;
  readonly organizations: OrganizationService;
  readonly projects: ProjectService;
  readonly environments: EnvironmentService;
  readonly apiKeys: ApiKeyService;
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
  const projects = new ProjectService(client);
  const apiKeysService = new ApiKeyService(client);

  return {
    users,
    sessions,
    organizations,
    projects,
    environments,
    apiKeys: apiKeysService,
    close: async () => {
      if (sql) {
        await sql.end();
      }
    },
  };
}
