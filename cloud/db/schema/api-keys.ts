import { relations } from "drizzle-orm";
import { pgTable, text, timestamp, uuid, unique } from "drizzle-orm/pg-core";

import { environments } from "./environments";
import { users, type PublicUser } from "./users";

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
    // Track who created this API key (for authentication & audit)
    ownerId: uuid("ownerId")
      .references(() => users.id)
      .notNull(),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
    // Track last usage for auditing
    lastUsedAt: timestamp("last_used_at", { withTimezone: true }),
    // Soft-delete timestamp (null = active, non-null = deleted)
    deletedAt: timestamp("deleted_at", { withTimezone: true }),
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
  ownedBy: one(users, {
    fields: [apiKeys.ownerId],
    references: [users.id],
  }),
}));

// Internal types
export type ApiKey = typeof apiKeys.$inferSelect;
export type NewApiKey = typeof apiKeys.$inferInsert;

// Public types for API responses (excludes keyHash)
export type PublicApiKey = Pick<
  ApiKey,
  | "id"
  | "name"
  | "keyPrefix"
  | "environmentId"
  | "ownerId"
  | "createdAt"
  | "lastUsedAt"
  | "deletedAt"
>;

// Type for the create response (includes the plaintext key)
export type ApiKeyCreateResponse = PublicApiKey & {
  key: string;
};

// Type for verified API key with full resource hierarchy
export type VerifiedApiKey = {
  apiKeyId: string;
  environmentId: string;
  projectId: string;
  organizationId: string;
};

// Helper type to capitalize the first letter of a string
type Capitalize<S extends string> = S extends `${infer First}${infer Rest}`
  ? `${Uppercase<First>}${Rest}`
  : S;

// Helper type to prefix PublicUser fields with "owner" and capitalize
type OwnerFields<T> = {
  [K in keyof T as `owner${Capitalize<string & K>}`]: T[K];
};

// ---------------------------------------------------------------------------
// API Key Info — type hierarchy for scoped API keys
// ---------------------------------------------------------------------------

/** Fields shared by all API key scopes. */
export type BaseApiKeyInfo = {
  apiKeyId: string;
  organizationId: string;
  /** Non-null when the key is owned by a claw (LEFT JOIN). */
  clawId: string | null;
} & OwnerFields<PublicUser>;

/**
 * Environment-scoped API key — tied to a specific project + environment.
 * This is the only scope that currently exists; the base type enables
 * future key scopes (e.g. org-scoped) without restructuring.
 */
export type EnvironmentApiKeyInfo = BaseApiKeyInfo & {
  environmentId: string;
  projectId: string;
};

/**
 * All API keys currently returned by getApiKeyInfo.
 * Today this is always EnvironmentApiKeyInfo; when new scopes are added,
 * this becomes a union (e.g. EnvironmentApiKeyInfo | OrgApiKeyInfo).
 */
export type ApiKeyInfo = EnvironmentApiKeyInfo;

// Type for API key with project and environment context (for listing all keys)
export type ApiKeyWithContext = PublicApiKey & {
  projectId: string;
  projectName: string;
  environmentName: string;
};
