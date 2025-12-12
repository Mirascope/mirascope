import { relations } from "drizzle-orm";
import { pgEnum, pgTable, timestamp, unique, uuid } from "drizzle-orm/pg-core";
import { organizations, type PublicOrganization } from "./organizations";
import { users } from "./users";

export const roleEnum = pgEnum("role", [
  "OWNER",
  "ADMIN",
  "DEVELOPER",
  "VIEWER",
]);
export const ROLE_VALUES = roleEnum.enumValues;

export const organizationMemberships = pgTable(
  "organization_memberships",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    userId: uuid("user_id")
      .references(() => users.id)
      .notNull(),
    organizationId: uuid("organization_id")
      .references(() => organizations.id)
      .notNull(),
    role: roleEnum("role").notNull(),
    createdAt: timestamp("created_at").defaultNow(),
    updatedAt: timestamp("updated_at").defaultNow(),
  },
  (table) => ({
    userOrgUnique: unique().on(table.userId, table.organizationId),
  }),
);

export const organizationMembershipsRelations = relations(
  organizationMemberships,
  ({ one }) => ({
    user: one(users, {
      fields: [organizationMemberships.userId],
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
export type Role = (typeof roleEnum.enumValues)[number];

// Public types
export type PublicOrganizationMembership = Pick<
  OrganizationMembership,
  "id" | "role" | "createdAt"
>;

// Public organization with user's membership role
export type PublicOrganizationWithMembership = PublicOrganization & {
  role: Role;
};
