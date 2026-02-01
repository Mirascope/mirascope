import { relations } from "drizzle-orm";
import {
  pgTable,
  timestamp,
  pgEnum,
  uuid,
  primaryKey,
  foreignKey,
} from "drizzle-orm/pg-core";

import { organizationMemberships } from "./organization-memberships";
import { projects } from "./projects";
import { users } from "./users";

export const projectRoleEnum = pgEnum("project_role", [
  "ADMIN",
  "DEVELOPER",
  "VIEWER",
  "ANNOTATOR",
]);
export const PROJECT_ROLE_VALUES = projectRoleEnum.enumValues;

export type ProjectRole = (typeof projectRoleEnum.enumValues)[number];

export const projectMemberships = pgTable(
  "project_memberships",
  {
    memberId: uuid("member_id").notNull(),
    organizationId: uuid("organization_id").notNull(),
    projectId: uuid("project_id")
      .references(() => projects.id, { onDelete: "cascade" })
      .notNull(),
    role: projectRoleEnum("role").notNull(),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow(),
  },
  (table) => ({
    pk: primaryKey({ columns: [table.memberId, table.projectId] }),
    // Enforces that project members must be organization members.
    // Cascade delete removes project membership when org membership is removed.
    orgMembershipFk: foreignKey({
      columns: [table.memberId, table.organizationId],
      foreignColumns: [
        organizationMemberships.memberId,
        organizationMemberships.organizationId,
      ],
    }).onDelete("cascade"),
  }),
);

export const projectMembershipsRelations = relations(
  projectMemberships,
  ({ one }) => ({
    member: one(users, {
      fields: [projectMemberships.memberId],
      references: [users.id],
    }),
    project: one(projects, {
      fields: [projectMemberships.projectId],
      references: [projects.id],
    }),
    organizationMembership: one(organizationMemberships, {
      fields: [projectMemberships.memberId, projectMemberships.organizationId],
      references: [
        organizationMemberships.memberId,
        organizationMemberships.organizationId,
      ],
    }),
  }),
);

// Internal types
export type ProjectMembership = typeof projectMemberships.$inferSelect;
export type NewProjectMembership = typeof projectMemberships.$inferInsert;

// Public types
export type PublicProjectMembership = Pick<
  ProjectMembership,
  "memberId" | "organizationId" | "projectId" | "role" | "createdAt"
>;
