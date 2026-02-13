import { pgTable, text, timestamp, unique, uuid } from "drizzle-orm/pg-core";

import { projects } from "./projects";

export const projectApiKeys = pgTable(
  "project_api_keys",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    projectId: uuid("project_id")
      .references(() => projects.id, { onDelete: "cascade" })
      .notNull(),
    provider: text("provider").notNull(),
    encryptedKey: text("encrypted_key").notNull(),
    nonce: text("nonce").notNull(),
    keySuffix: text("key_suffix").notNull(),
    createdAt: timestamp("created_at", { withTimezone: true })
      .defaultNow()
      .notNull(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .defaultNow()
      .notNull(),
  },
  (table) => ({
    uniqueProjectProvider: unique().on(table.projectId, table.provider),
  }),
);

// Internal types
export type ProjectApiKey = typeof projectApiKeys.$inferSelect;
export type NewProjectApiKey = typeof projectApiKeys.$inferInsert;

// Public types for API responses (never includes the encrypted key)
export type PublicProjectApiKey = Pick<
  ProjectApiKey,
  "provider" | "keySuffix" | "updatedAt"
>;
