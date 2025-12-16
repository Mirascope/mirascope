import { relations } from "drizzle-orm";
import { pgEnum, pgTable, timestamp, uuid } from "drizzle-orm/pg-core";
import { organizations } from "./organizations";
import { users } from "./users";
import { organizationRoleEnum } from "./organization-memberships";

export const auditActionEnum = pgEnum("audit_action", [
  "GRANT", // New membership created
  "REVOKE", // Membership deleted
  "CHANGE", // Role changed
]);

export const organizationMembershipAudit = pgTable(
  "organization_membership_audit",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    organizationId: uuid("organization_id")
      .references(() => organizations.id, { onDelete: "cascade" })
      .notNull(),
    actorId: uuid("actor_id")
      .references(() => users.id)
      .notNull(),
    targetId: uuid("target_id")
      .references(() => users.id)
      .notNull(),
    action: auditActionEnum("action").notNull(),
    previousRole: organizationRoleEnum("previous_role"),
    newRole: organizationRoleEnum("new_role"),
    createdAt: timestamp("created_at").defaultNow().notNull(),
  },
);

export const organizationMembershipAuditRelations = relations(
  organizationMembershipAudit,
  ({ one }) => ({
    organization: one(organizations, {
      fields: [organizationMembershipAudit.organizationId],
      references: [organizations.id],
    }),
    actor: one(users, {
      fields: [organizationMembershipAudit.actorId],
      references: [users.id],
      relationName: "organizationMembershipAuditActor",
    }),
    target: one(users, {
      fields: [organizationMembershipAudit.targetId],
      references: [users.id],
      relationName: "organizationMembershipAuditTarget",
    }),
  }),
);

// Internal types
export type OrganizationMembershipAuditEntry =
  typeof organizationMembershipAudit.$inferSelect;
export type NewOrganizationMembershipAuditEntry =
  typeof organizationMembershipAudit.$inferInsert;
export type AuditAction = (typeof auditActionEnum.enumValues)[number];

// Public types
export type PublicOrganizationMembershipAudit = Pick<
  OrganizationMembershipAuditEntry,
  | "id"
  | "actorId"
  | "targetId"
  | "action"
  | "previousRole"
  | "newRole"
  | "createdAt"
>;
