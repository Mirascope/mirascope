import { relations, sql } from "drizzle-orm";
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
import { users } from "./users";

export const apiKeys = pgTable(
  "api_keys",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    name: text("name").notNull(),
    // Store only the hash of the key, never the plaintext
    keyHash: text("key_hash").notNull(),
    // Store a prefix for display purposes (e.g., "mk_abc...")
    keyPrefix: text("key_prefix").notNull(),
    // Environment-scoped keys set this; org-scoped keys leave it NULL
    environmentId: uuid("environment_id").references(() => environments.id, {
      onDelete: "cascade",
    }),
    // Org-scoped keys set this; environment-scoped keys leave it NULL
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
    organizationNameUnique: unique().on(table.organizationId, table.name),
    // Exactly one of environment_id or organization_id must be set
    scopeCheck: check(
      "api_keys_scope_check",
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

// ---------------------------------------------------------------------------
// Table-level types (raw row shapes)
// ---------------------------------------------------------------------------

/** Full row from api_keys table. */
export type ApiKey = typeof apiKeys.$inferSelect;

/** Insert shape for api_keys table. */
export type NewApiKey = typeof apiKeys.$inferInsert;

// ---------------------------------------------------------------------------
// Public API key types (excludes keyHash, safe for API responses)
// ---------------------------------------------------------------------------

/** Base fields present on every API key response. */
export type BasePublicApiKey = {
  id: string;
  name: string;
  keyPrefix: string;
  ownerId: string;
  createdAt: Date | null;
  lastUsedAt: Date | null;
  deletedAt: Date | null;
};

/** Environment-scoped public API key. */
export type EnvironmentPublicApiKey = BasePublicApiKey & {
  environmentId: string;
};

/** Org-scoped public API key (no environment). */
export type OrgPublicApiKey = BasePublicApiKey & {
  organizationId: string;
  environmentId: null;
};

/** Discriminated union of public API key types — dispatch on `environmentId`. */
export type PublicApiKey = EnvironmentPublicApiKey | OrgPublicApiKey;

/** Create response — includes the plaintext key (shown once). */
export type EnvironmentApiKeyCreateResponse = EnvironmentPublicApiKey & {
  key: string;
};

/** Org-scoped create response — includes the plaintext key (shown once). */
export type OrgApiKeyCreateResponse = OrgPublicApiKey & {
  key: string;
};

/** Discriminated union of create response types. */
export type ApiKeyCreateResponse =
  | EnvironmentApiKeyCreateResponse
  | OrgApiKeyCreateResponse;

// ---------------------------------------------------------------------------
// Authenticated API key info (returned by getApiKeyInfo)
// ---------------------------------------------------------------------------

/** Owner info resolved from the users table. */
export type ApiKeyOwner = {
  ownerId: string;
  ownerEmail: string;
  ownerName: string | null;
  ownerAccountType: "user" | "claw";
  ownerDeletedAt: Date | null;
};

/** Base authenticated key info — identity + resolved owner. */
export type BaseApiKeyAuth = {
  apiKeyId: string;
  organizationId: string;
  /** Non-null when the key's owner is a claw bot user. */
  clawId: string | null;
} & ApiKeyOwner;

/** Environment-scoped authenticated key info. */
export type EnvironmentApiKeyAuth = BaseApiKeyAuth & {
  environmentId: string;
  projectId: string;
};

/** Org-scoped authenticated key info (no environment/project). */
export type OrgApiKeyAuth = BaseApiKeyAuth & {
  environmentId: null;
};

/** Discriminated union of authenticated key info — dispatch on `environmentId`. */
export type ApiKeyAuth = EnvironmentApiKeyAuth | OrgApiKeyAuth;

// Backward compat aliases — consumers can migrate at their own pace
/** @deprecated Use EnvironmentApiKeyAuth */
export type EnvironmentApiKeyInfo = EnvironmentApiKeyAuth;
/** @deprecated Use ApiKeyAuth */
export type ApiKeyInfo = ApiKeyAuth;

// ---------------------------------------------------------------------------
// Display types — for UI listing with resolved context
// ---------------------------------------------------------------------------

/** Context fields shared by all API key display types. */
export type BaseApiKeyContext = {
  ownerName: string | null;
  ownerAccountType: "user" | "claw";
};

/** Environment-scoped key with full display context. */
export type EnvironmentApiKeyWithContext = EnvironmentPublicApiKey &
  BaseApiKeyContext & {
    projectId: string;
    projectName: string;
    environmentName: string;
  };

/** Org-scoped key with display context. */
export type OrgApiKeyWithContext = OrgPublicApiKey &
  BaseApiKeyContext & {
    organizationName: string;
  };

/** Discriminated union of API key with display context. */
export type ApiKeyWithContext =
  | EnvironmentApiKeyWithContext
  | OrgApiKeyWithContext;
