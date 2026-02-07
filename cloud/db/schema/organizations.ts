import { relations, sql } from "drizzle-orm";
import {
  bigint,
  boolean,
  pgTable,
  text,
  timestamp,
  uuid,
} from "drizzle-orm/pg-core";

import { organizationMemberships } from "./organization-memberships";

export const organizations = pgTable("organizations", {
  id: uuid("id").primaryKey().defaultRandom(),
  name: text("name").notNull(),
  slug: text("slug").notNull().unique(),
  stripeCustomerId: text("stripe_customer_id").notNull().unique(),
  autoReloadEnabled: boolean("auto_reload_enabled").default(false).notNull(),
  autoReloadThresholdCenticents: bigint("auto_reload_threshold_centicents", {
    mode: "bigint",
  })
    .default(sql`0`)
    .notNull(),
  autoReloadAmountCenticents: bigint("auto_reload_amount_centicents", {
    mode: "bigint",
  })
    .default(sql`500000`)
    .notNull(),
  lastAutoReloadAt: timestamp("last_auto_reload_at", { withTimezone: true }),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow(),
});

export const organizationsRelations = relations(organizations, ({ many }) => ({
  memberships: many(organizationMemberships),
}));

// Internal types
export type Organization = typeof organizations.$inferSelect;
export type NewOrganization = typeof organizations.$inferInsert;

// Public types for API responses
export type PublicOrganization = Pick<
  Organization,
  "id" | "name" | "slug" | "stripeCustomerId"
>;
