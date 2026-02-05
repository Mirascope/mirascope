import { relations } from "drizzle-orm";
import {
  bigint,
  pgEnum,
  pgTable,
  text,
  timestamp,
  unique,
  uuid,
} from "drizzle-orm/pg-core";

import { clawMemberships } from "@/db/schema/claw-memberships";

import { organizations } from "./organizations";
import { users } from "./users";

export const clawStatusEnum = pgEnum("claw_status", [
  "pending",
  "provisioning",
  "active",
  "paused",
  "error",
]);

export const clawInstanceTypeEnum = pgEnum("claw_instance_type", [
  "lite",
  "basic",
  "standard-1",
  "standard-2",
  "standard-3",
  "standard-4",
]);

export const claws = pgTable(
  "claws",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    slug: text("slug").notNull(),
    displayName: text("display_name"),
    description: text("description"),
    organizationId: uuid("organization_id")
      .references(() => organizations.id, { onDelete: "cascade" })
      .notNull(),
    createdByUserId: uuid("created_by_user_id")
      .references(() => users.id)
      .notNull(),
    status: clawStatusEnum("status").notNull().default("pending"),
    instanceType: clawInstanceTypeEnum("instance_type")
      .notNull()
      .default("basic"),
    lastDeployedAt: timestamp("last_deployed_at", { withTimezone: true }),
    lastError: text("last_error"),
    // Secrets stored as base64-encoded AES-256-GCM ciphertext
    secretsEncrypted: text("secrets_encrypted"),
    secretsKeyId: text("secrets_key_id"),
    bucketName: text("bucket_name"),
    // Per-claw spending guardrails (optional — billing is at org level via credit pool)
    // Stored in centicents: 1 cent = 100 centicents, $1 = 10,000 centicents
    weeklySpendingGuardrailCenticents: bigint(
      "weekly_spending_guardrail_centicents",
      { mode: "bigint" },
    ),
    // Usage tracking — weekly billing window
    weeklyWindowStart: timestamp("weekly_window_start", {
      withTimezone: true,
    }),
    weeklyUsageCenticents: bigint("weekly_usage_centicents", {
      mode: "bigint",
    }),
    // Usage tracking — 5-hour burst rate-limit window
    burstWindowStart: timestamp("burst_window_start", { withTimezone: true }),
    burstUsageCenticents: bigint("burst_usage_centicents", {
      mode: "bigint",
    }),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow(),
  },
  (table) => ({
    uniqueOrgSlug: unique().on(table.organizationId, table.slug),
    // Composite unique on (id, organizationId) to support composite FK from claw_memberships
    uniqueIdOrg: unique().on(table.id, table.organizationId),
  }),
);

export const clawsRelations = relations(claws, ({ one, many }) => ({
  createdBy: one(users, {
    fields: [claws.createdByUserId],
    references: [users.id],
  }),
  organization: one(organizations, {
    fields: [claws.organizationId],
    references: [organizations.id],
  }),
  memberships: many(clawMemberships),
}));

// Internal types
export type Claw = typeof claws.$inferSelect;
export type NewClaw = typeof claws.$inferInsert;

// Public types for API responses
export type PublicClaw = Pick<
  Claw,
  | "id"
  | "slug"
  | "displayName"
  | "description"
  | "organizationId"
  | "createdByUserId"
  | "status"
  | "instanceType"
  | "lastDeployedAt"
  | "lastError"
  | "secretsEncrypted"
  | "secretsKeyId"
  | "bucketName"
  | "weeklySpendingGuardrailCenticents"
  | "weeklyWindowStart"
  | "weeklyUsageCenticents"
  | "burstWindowStart"
  | "burstUsageCenticents"
  | "createdAt"
  | "updatedAt"
>;
