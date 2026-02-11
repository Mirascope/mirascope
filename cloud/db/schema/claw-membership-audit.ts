import { relations } from "drizzle-orm";
import { pgTable, timestamp, uuid } from "drizzle-orm/pg-core";

import { clawRoleEnum } from "./claw-memberships";
import { claws } from "./claws";
import { auditActionEnum } from "./organization-membership-audit";
import { users } from "./users";

export const clawMembershipAudit = pgTable("claw_membership_audit", {
  id: uuid("id").primaryKey().defaultRandom(),
  clawId: uuid("claw_id")
    .references(() => claws.id, { onDelete: "cascade" })
    .notNull(),
  actorId: uuid("actor_id")
    .references(() => users.id)
    .notNull(),
  targetId: uuid("target_id")
    .references(() => users.id)
    .notNull(),
  action: auditActionEnum("action").notNull(),
  previousRole: clawRoleEnum("previous_role"),
  newRole: clawRoleEnum("new_role"),
  createdAt: timestamp("created_at", { withTimezone: true })
    .defaultNow()
    .notNull(),
});

export const clawMembershipAuditRelations = relations(
  clawMembershipAudit,
  ({ one }) => ({
    claw: one(claws, {
      fields: [clawMembershipAudit.clawId],
      references: [claws.id],
    }),
    actor: one(users, {
      fields: [clawMembershipAudit.actorId],
      references: [users.id],
      relationName: "clawMembershipAuditActor",
    }),
    target: one(users, {
      fields: [clawMembershipAudit.targetId],
      references: [users.id],
      relationName: "clawMembershipAuditTarget",
    }),
  }),
);

// Internal types
export type ClawMembershipAuditEntry = typeof clawMembershipAudit.$inferSelect;
export type NewClawMembershipAuditEntry =
  typeof clawMembershipAudit.$inferInsert;

// Public types
export type PublicClawMembershipAudit = Pick<
  ClawMembershipAuditEntry,
  | "id"
  | "actorId"
  | "targetId"
  | "action"
  | "previousRole"
  | "newRole"
  | "createdAt"
>;
