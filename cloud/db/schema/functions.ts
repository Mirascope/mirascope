import { relations } from "drizzle-orm";
import {
  pgTable,
  text,
  timestamp,
  uuid,
  unique,
  jsonb,
  index,
  foreignKey,
} from "drizzle-orm/pg-core";

import { environments } from "./environments";
import { organizations } from "./organizations";
import { projects } from "./projects";

export type DependencyInfo = {
  version: string;
  extras: string[] | null;
};

export const functions = pgTable(
  "functions",
  {
    id: uuid("id").primaryKey().defaultRandom(),

    hash: text("hash").notNull(),
    signatureHash: text("signature_hash").notNull(),
    name: text("name").notNull(),
    description: text("description"),
    version: text("version").notNull(),
    tags: jsonb("tags").$type<string[]>(),
    metadata: jsonb("metadata").$type<Record<string, string>>(),
    code: text("code").notNull(),
    signature: text("signature").notNull(),
    dependencies: jsonb("dependencies").$type<Record<string, DependencyInfo>>(),

    environmentId: uuid("environment_id")
      .references(() => environments.id, { onDelete: "cascade" })
      .notNull(),
    projectId: uuid("project_id")
      .references(() => projects.id, { onDelete: "cascade" })
      .notNull(),
    organizationId: uuid("organization_id")
      .references(() => organizations.id, { onDelete: "cascade" })
      .notNull(),

    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow(),
  },
  (table) => ({
    uniqueEnvironmentHash: unique().on(table.environmentId, table.hash),
    environmentNameIndex: index("functions_env_name_idx").on(
      table.environmentId,
      table.name,
    ),
    environmentSignatureHashIndex: index("functions_env_sig_hash_idx").on(
      table.environmentId,
      table.signatureHash,
    ),
    environmentProjectFk: foreignKey({
      columns: [table.projectId, table.environmentId],
      foreignColumns: [environments.projectId, environments.id],
      name: "functions_env_project_fk",
    }).onDelete("cascade"),
    projectOrgFk: foreignKey({
      columns: [table.organizationId, table.projectId],
      foreignColumns: [projects.organizationId, projects.id],
      name: "functions_project_org_fk",
    }).onDelete("cascade"),
  }),
);

export const functionsRelations = relations(functions, ({ one }) => ({
  environment: one(environments, {
    fields: [functions.environmentId],
    references: [environments.id],
  }),
  project: one(projects, {
    fields: [functions.projectId],
    references: [projects.id],
  }),
  organization: one(organizations, {
    fields: [functions.organizationId],
    references: [organizations.id],
  }),
}));

export type Function = typeof functions.$inferSelect;
export type NewFunction = typeof functions.$inferInsert;

export type PublicFunction = Pick<
  Function,
  | "id"
  | "hash"
  | "signatureHash"
  | "name"
  | "description"
  | "version"
  | "tags"
  | "metadata"
  | "code"
  | "signature"
  | "dependencies"
  | "environmentId"
  | "projectId"
  | "organizationId"
  | "createdAt"
  | "updatedAt"
>;
