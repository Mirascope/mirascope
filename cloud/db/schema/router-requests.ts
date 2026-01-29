import { relations } from "drizzle-orm";
import {
  pgTable,
  text,
  timestamp,
  uuid,
  pgEnum,
  bigint,
  jsonb,
  index,
} from "drizzle-orm/pg-core";

import type { CostInCenticents } from "@/api/router/cost-utils";

import { apiKeys } from "@/db/schema/api-keys";
import { creditReservations } from "@/db/schema/credit-reservations";
import { environments } from "@/db/schema/environments";
import { organizations } from "@/db/schema/organizations";
import { projects } from "@/db/schema/projects";
import { users } from "@/db/schema/users";

/**
 * Request status enum for tracking request lifecycle.
 *
 * - pending: Request is being processed
 * - success: Request completed successfully
 * - failure: Request failed
 */
export const requestStatusEnum = pgEnum("request_status", [
  "pending",
  "success",
  "failure",
]);

/**
 * Router requests table for storing complete request lifecycle data.
 *
 * ## Purpose
 * This table stores ALL router requests (successful or failed) with complete
 * metadata for observability, analytics, and cost reconciliation.
 *
 * ## Relationship with credit_reservations
 * - credit_reservations table: Financial instrument (fund locking/releasing)
 * - router_requests table: Request lifecycle and observability
 * - One-to-one relationship via routerRequestId foreign key
 *
 * ## Financial Data Immutability
 * Like credit_reservations, this table stores financial records that must
 * NEVER be deleted. Records are linked to organizations (not environments)
 * to ensure data persistence even if environments are deleted.
 *
 * ## Analytics and Outbox Pattern
 * Long-term plan: Sync this table to ClickHouse via outbox pattern for
 * high-performance analytics and usage reporting.
 *
 * ## Cost Storage Format
 * All costs are stored as BIGINT in centi-cents, where 1 = $0.0001 USD.
 * See credit-reservations.ts for detailed explanation.
 */
export const routerRequests = pgTable(
  "router_requests",
  {
    id: uuid("id").primaryKey().defaultRandom(),

    // Provider metadata
    provider: text("provider").notNull(),
    model: text("model").notNull(),
    requestId: text("request_id"), // External provider request ID (OpenAI ID, etc.)

    // Token usage
    inputTokens: bigint("input_tokens", { mode: "bigint" }),
    outputTokens: bigint("output_tokens", { mode: "bigint" }),
    cacheReadTokens: bigint("cache_read_tokens", { mode: "bigint" }),
    cacheWriteTokens: bigint("cache_write_tokens", { mode: "bigint" }),

    // Provider-specific cache breakdown (JSONB for flexibility)
    // Example for Anthropic: { "ephemeral5m": 100, "ephemeral1h": 50 }
    cacheWriteBreakdown: jsonb("cache_write_breakdown"),

    // Cost (in centi-cents: 1 = $0.0001 USD)
    costCenticents: bigint("cost_centicents", {
      mode: "bigint",
    }),

    // Request status
    status: requestStatusEnum("status").default("pending").notNull(),
    errorMessage: text("error_message"),

    // Organizational hierarchy (for scoping and analytics)
    // TODO: we should not cascade delete requests (since they provide our source of truth)
    // so we should prioritize soft-deletion for org/project/env
    organizationId: uuid("organization_id").notNull(),
    projectId: uuid("project_id").notNull(),
    environmentId: uuid("environment_id").notNull(),

    // Authentication context (who made the request)
    apiKeyId: uuid("api_key_id")
      .notNull() // TODO: same thing here re: soft-deletion
      .references(() => apiKeys.id),
    userId: uuid("user_id")
      .notNull()
      .references(() => users.id),

    // Timestamps
    createdAt: timestamp("created_at", { withTimezone: true })
      .defaultNow()
      .notNull(),
    completedAt: timestamp("completed_at", { withTimezone: true }),
  },
  (table) => ({
    // Index for analytics queries by organization over time
    orgCreatedAtIndex: index("router_requests_org_created_at_index").on(
      table.organizationId,
      table.createdAt,
    ),
    // Index for environment-scoped queries
    environmentIndex: index("router_requests_environment_index").on(
      table.environmentId,
    ),
  }),
);

export const routerRequestsRelations = relations(routerRequests, ({ one }) => ({
  organization: one(organizations, {
    fields: [routerRequests.organizationId],
    references: [organizations.id],
  }),
  project: one(projects, {
    fields: [routerRequests.projectId],
    references: [projects.id],
  }),
  environment: one(environments, {
    fields: [routerRequests.environmentId],
    references: [environments.id],
  }),
  apiKey: one(apiKeys, {
    fields: [routerRequests.apiKeyId],
    references: [apiKeys.id],
  }),
  user: one(users, {
    fields: [routerRequests.userId],
    references: [users.id],
  }),
  // One-to-one relationship with credit reservation
  creditReservation: one(creditReservations, {
    fields: [routerRequests.id],
    references: [creditReservations.routerRequestId],
  }),
}));

// Internal types
export type RouterRequest = typeof routerRequests.$inferSelect;
export type NewRouterRequest = typeof routerRequests.$inferInsert;
export type RequestStatus = (typeof requestStatusEnum.enumValues)[number];

// Helper to ensure cost fields use the CostInCenticents type
export type RouterRequestWithTypedCosts = Omit<
  RouterRequest,
  "costCenticents"
> & {
  costCenticents: CostInCenticents | null;
};
