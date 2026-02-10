import { relations } from "drizzle-orm";
import {
  foreignKey,
  pgEnum,
  pgTable,
  primaryKey,
  timestamp,
  uuid,
} from "drizzle-orm/pg-core";

import { claws } from "./claws";
import { organizationMemberships } from "./organization-memberships";
import { users } from "./users";

export const clawRoleEnum = pgEnum("claw_role", [
  "ADMIN",
  "DEVELOPER",
  "VIEWER",
  "ANNOTATOR",
]);
export const CLAW_ROLE_VALUES = clawRoleEnum.enumValues;

export type ClawRole = (typeof clawRoleEnum.enumValues)[number];

export const clawMemberships = pgTable(
  "claw_memberships",
  {
    memberId: uuid("member_id").notNull(),
    organizationId: uuid("organization_id").notNull(),
    clawId: uuid("claw_id").notNull(),
    role: clawRoleEnum("role").notNull(),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow(),
  },
  (table) => ({
    pk: primaryKey({ columns: [table.memberId, table.clawId] }),
    // Enforces that claw members must be organization members.
    // Cascade delete removes claw membership when org membership is removed.
    orgMembershipFk: foreignKey({
      columns: [table.memberId, table.organizationId],
      foreignColumns: [
        organizationMemberships.memberId,
        organizationMemberships.organizationId,
      ],
    }).onDelete("cascade"),
    // Enforces that claw_memberships.organization_id matches claws.organization_id.
    // Prevents members from Org A being added to claws in Org B.
    clawOrgFk: foreignKey({
      columns: [table.clawId, table.organizationId],
      foreignColumns: [claws.id, claws.organizationId],
    }).onDelete("cascade"),
  }),
);

export const clawMembershipsRelations = relations(
  clawMemberships,
  ({ one }) => ({
    member: one(users, {
      fields: [clawMemberships.memberId],
      references: [users.id],
    }),
    claw: one(claws, {
      fields: [clawMemberships.clawId],
      references: [claws.id],
    }),
    organizationMembership: one(organizationMemberships, {
      fields: [clawMemberships.memberId, clawMemberships.organizationId],
      references: [
        organizationMemberships.memberId,
        organizationMemberships.organizationId,
      ],
    }),
  }),
);

// Internal types
export type ClawMembership = typeof clawMemberships.$inferSelect;
export type NewClawMembership = typeof clawMemberships.$inferInsert;

// Public types
export type PublicClawMembership = Pick<
  ClawMembership,
  "memberId" | "organizationId" | "clawId" | "role" | "createdAt"
>;
