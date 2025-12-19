import { relations } from "drizzle-orm";
import {
  pgTable,
  timestamp,
  pgEnum,
  uuid,
  primaryKey,
} from "drizzle-orm/pg-core";
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
    memberId: uuid("member_id")
      .references(() => users.id)
      .notNull(),
    projectId: uuid("project_id")
      .references(() => projects.id, { onDelete: "cascade" })
      .notNull(),
    role: projectRoleEnum("role").notNull(),
    createdAt: timestamp("created_at").defaultNow(),
    updatedAt: timestamp("updated_at").defaultNow(),
  },
  (table) => ({
    pk: primaryKey({ columns: [table.memberId, table.projectId] }),
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
  }),
);

// Internal types
export type ProjectMembership = typeof projectMemberships.$inferSelect;
export type NewProjectMembership = typeof projectMemberships.$inferInsert;

// Public types
export type PublicProjectMembership = Pick<
  ProjectMembership,
  "memberId" | "projectId" | "role" | "createdAt"
>;
