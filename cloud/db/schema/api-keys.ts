import { relations } from "drizzle-orm";
import { sql } from "drizzle-orm";
import {
  check,
  pgTable,
  text,
  timestamp,
  uuid,
  unique,
} from "drizzle-orm/pg-core";

import { environments } from "./environments";
import { organizations } from "./organizations";
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
    // Environment-scoped keys (nullable for org-scoped keys)
    environmentId: uuid("environment_id").references(() => environments.id, {
      onDelete: "cascade",
    }),
    // Org-scoped keys (nullable for environment-scoped keys)
    organizationId: uuid("organization_id").references(() => organizations.id, {
      onDelete: "cascade",
    }),
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
    orgNameUnique: unique().on(table.organizationId, table.name),
    // Exactly one of environmentId or organizationId must be set
    scopeCheck: check(
      "api_key_scope_check",
      sql`(${table.environmentId} IS NOT NULL AND ${table.organizationId} IS NULL) OR (${table.environmentId} IS NULL AND ${table.organizationId} IS NOT NULL)`,
    ),
  }),
);

export const apiKeysRelations = relations(apiKeys, ({ one }) => ({
  environment: one(environments, {
    fields: [apiKeys.environmentId],
    references: [environments.id],
  }),
  organization: one(organizations, {
    fields: [apiKeys.organizationId],
    references: [organizations.id],
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
  | "organizationId"
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
// API Key Info — discriminated union for env-scoped vs org-scoped keys
// ---------------------------------------------------------------------------

/** Fields shared by all API key scopes. */
export type BaseApiKeyInfo = {
  apiKeyId: string;
  organizationId: string;
  /** Non-null when the key is owned by a claw (LEFT JOIN). */
  clawId: string | null;
} & OwnerFields<PublicUser>;

/** Environment-scoped API key — tied to a specific project + environment. */
export type EnvironmentApiKeyInfo = BaseApiKeyInfo & {
  environmentId: string;
  projectId: string;
};

/** Organization-scoped API key — grants access to all org resources. */
export type OrgApiKeyInfo = BaseApiKeyInfo & {
  environmentId: null;
  projectId: null;
};

/**
 * Union of all API key scopes. Discriminate on `environmentId`:
 *   - `string`  → EnvironmentApiKeyInfo
 *   - `null`    → OrgApiKeyInfo
 */
export type ApiKeyInfo = EnvironmentApiKeyInfo | OrgApiKeyInfo;

// Type for API key with project and environment context (for listing all keys)
// TODO: This type only makes sense for env-scoped keys — revisit when org keys
// get their own listing endpoint.
export type ApiKeyWithContext = PublicApiKey & {
  projectId: string;
  projectName: string;
  environmentName: string;
};
