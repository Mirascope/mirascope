import { relations } from "drizzle-orm";
import {
  pgTable,
  text,
  timestamp,
  uuid,
  unique,
  jsonb,
  index,
} from "drizzle-orm/pg-core";
import { environments } from "./environments";
import { projects } from "./projects";
import { organizations } from "./organizations";

export type DependencyInfo = {
  version: string;
  extras: string[] | null;
};

export const functions = pgTable(
  "functions",
  {
    id: uuid("id").primaryKey().defaultRandom(),

    // Version identification
    hash: text("hash").notNull(), // SHA256 of complete closure code
    signatureHash: text("signature_hash").notNull(), // SHA256 of function signature

    // Metadata
    name: text("name").notNull(), // Function name (qualified or custom)
    description: text("description"), // Docstring
    version: text("version").notNull(), // Computed version string (e.g., "1.0", "1.1")

    // User-provided metadata
    tags: jsonb("tags").$type<string[]>(), // ["production", "ml"]
    metadata: jsonb("metadata").$type<Record<string, string>>(), // {"owner": "team-ml"}

    // Code storage
    code: text("code").notNull(), // Complete closure code
    signature: text("signature").notNull(), // Function signature only
    dependencies: jsonb("dependencies").$type<Record<string, DependencyInfo>>(),

    // Scope (API Key auth provides environment context)
    environmentId: uuid("environment_id")
      .references(() => environments.id, { onDelete: "cascade" })
      .notNull(),
    projectId: uuid("project_id")
      .references(() => projects.id, { onDelete: "cascade" })
      .notNull(),
    organizationId: uuid("organization_id")
      .references(() => organizations.id, { onDelete: "cascade" })
      .notNull(),

    createdAt: timestamp("created_at").defaultNow(),
    updatedAt: timestamp("updated_at").defaultNow(),
  },
  (table) => ({
    // Same hash in same environment = same version (deduplication)
    hashEnvUnique: unique().on(table.hash, table.environmentId),
    // Query by name for version history
    envNameIdx: index("functions_env_name_idx").on(
      table.environmentId,
      table.name,
    ),
    // Query by signature hash for major version detection
    envSigHashIdx: index("functions_env_sig_hash_idx").on(
      table.environmentId,
      table.signatureHash,
    ),
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

// Internal types
export type Function = typeof functions.$inferSelect;
export type NewFunction = typeof functions.$inferInsert;

// Public types for API responses
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
