import { relations } from "drizzle-orm";
import { pgTable, timestamp, uuid } from "drizzle-orm/pg-core";
import { projects } from "./projects";
import { users } from "./users";
import { projectRoleEnum } from "./project-memberships";
import { auditActionEnum } from "./organization-membership-audit";

export const projectMembershipAudit = pgTable("project_membership_audit", {
  id: uuid("id").primaryKey().defaultRandom(),
  projectId: uuid("project_id")
    .references(() => projects.id, { onDelete: "cascade" })
    .notNull(),
  actorId: uuid("actor_id")
    .references(() => users.id)
    .notNull(),
  targetId: uuid("target_id")
    .references(() => users.id)
    .notNull(),
  action: auditActionEnum("action").notNull(),
  previousRole: projectRoleEnum("previous_role"),
  newRole: projectRoleEnum("new_role"),
  createdAt: timestamp("created_at", { withTimezone: true })
    .defaultNow()
    .notNull(),
});

export const projectMembershipAuditRelations = relations(
  projectMembershipAudit,
  ({ one }) => ({
    project: one(projects, {
      fields: [projectMembershipAudit.projectId],
      references: [projects.id],
    }),
    actor: one(users, {
      fields: [projectMembershipAudit.actorId],
      references: [users.id],
      relationName: "projectMembershipAuditActor",
    }),
    target: one(users, {
      fields: [projectMembershipAudit.targetId],
      references: [users.id],
      relationName: "projectMembershipAuditTarget",
    }),
  }),
);

// Internal types
export type ProjectMembershipAuditEntry =
  typeof projectMembershipAudit.$inferSelect;
export type NewProjectMembershipAuditEntry =
  typeof projectMembershipAudit.$inferInsert;

// Public types
export type PublicProjectMembershipAudit = Pick<
  ProjectMembershipAuditEntry,
  | "id"
  | "actorId"
  | "targetId"
  | "action"
  | "previousRole"
  | "newRole"
  | "createdAt"
>;
