import { relations } from "drizzle-orm";
import { pgTable, text, timestamp, uuid, unique } from "drizzle-orm/pg-core";
import { environments } from "./environments";

export const apiKeys = pgTable(
  "api_keys",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    name: text("name").notNull(),
    // Store only the hash of the key, never the plaintext
    keyHash: text("key_hash").notNull(),
    // Store a prefix for display purposes (e.g., "mk_abc...")
    keyPrefix: text("key_prefix").notNull(),
    environmentId: uuid("environment_id")
      .references(() => environments.id, { onDelete: "cascade" })
      .notNull(),
    createdAt: timestamp("created_at").defaultNow(),
    // Track last usage for auditing
    lastUsedAt: timestamp("last_used_at"),
  },
  (table) => ({
    environmentNameUnique: unique().on(table.environmentId, table.name),
  }),
);

export const apiKeysRelations = relations(apiKeys, ({ one }) => ({
  environment: one(environments, {
    fields: [apiKeys.environmentId],
    references: [environments.id],
  }),
}));

// Internal types
export type ApiKey = typeof apiKeys.$inferSelect;
export type NewApiKey = typeof apiKeys.$inferInsert;

// Public types for API responses (excludes keyHash)
export type PublicApiKey = Pick<
  ApiKey,
  "id" | "name" | "keyPrefix" | "environmentId" | "createdAt" | "lastUsedAt"
>;

// Type for the create response (includes the plaintext key)
export type ApiKeyCreateResponse = PublicApiKey & {
  key: string;
};
