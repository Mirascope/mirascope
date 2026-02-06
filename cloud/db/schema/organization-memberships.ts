import { relations } from "drizzle-orm";
import {
  pgEnum,
  pgTable,
  primaryKey,
  timestamp,
  uuid,
} from "drizzle-orm/pg-core";

import { organizations, type PublicOrganization } from "./organizations";
import { users } from "./users";

export const organizationRoleEnum = pgEnum("organization_role", [
  "OWNER",
  "ADMIN",
  "MEMBER",
  "BOT",
]);
export const ORGANIZATION_ROLE_VALUES = organizationRoleEnum.enumValues;

export const organizationMemberships = pgTable(
  "organization_memberships",
  {
    memberId: uuid("member_id")
      .references(() => users.id)
      .notNull(),
    organizationId: uuid("organization_id")
      .references(() => organizations.id, { onDelete: "cascade" })
      .notNull(),
    role: organizationRoleEnum("role").notNull(),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow(),
  },
  (table) => ({
    pk: primaryKey({ columns: [table.memberId, table.organizationId] }),
  }),
);

export const organizationMembershipsRelations = relations(
  organizationMemberships,
  ({ one }) => ({
    member: one(users, {
      fields: [organizationMemberships.memberId],
      references: [users.id],
    }),
    organization: one(organizations, {
      fields: [organizationMemberships.organizationId],
      references: [organizations.id],
    }),
  }),
);

// Internal types
export type OrganizationMembership =
  typeof organizationMemberships.$inferSelect;
export type NewOrganizationMembership =
  typeof organizationMemberships.$inferInsert;
export type OrganizationRole = (typeof organizationRoleEnum.enumValues)[number];

// Public types
export type PublicOrganizationMembership = Pick<
  OrganizationMembership,
  "memberId" | "role" | "createdAt"
>;

// Public organization with user's membership role
export type PublicOrganizationWithMembership = PublicOrganization & {
  role: OrganizationRole;
};
