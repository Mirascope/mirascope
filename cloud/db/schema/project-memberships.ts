import { relations } from "drizzle-orm";
import { pgTable, timestamp, unique, uuid } from "drizzle-orm/pg-core";
import { projects } from "./projects";
import { users } from "./users";
import { roleEnum } from "./organization-memberships";

export const projectMemberships = pgTable(
  "project_memberships",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    projectId: uuid("project_id")
      .references(() => projects.id, { onDelete: "cascade" })
      .notNull(),
    userId: uuid("user_id")
      .references(() => users.id, { onDelete: "cascade" })
      .notNull(),
    role: roleEnum("role").notNull(),
    createdAt: timestamp("created_at").defaultNow(),
    updatedAt: timestamp("updated_at").defaultNow(),
  },
  (table) => ({
    projectUserUnique: unique().on(table.projectId, table.userId),
  }),
);

export const projectMembershipsRelations = relations(
  projectMemberships,
  ({ one }) => ({
    project: one(projects, {
      fields: [projectMemberships.projectId],
      references: [projects.id],
    }),
    user: one(users, {
      fields: [projectMemberships.userId],
      references: [users.id],
    }),
  }),
);

// Internal types
export type ProjectMembership = typeof projectMemberships.$inferSelect;
export type NewProjectMembership = typeof projectMemberships.$inferInsert;

// Public types
export type PublicProjectMembership = Pick<
  ProjectMembership,
  "id" | "projectId" | "userId" | "role" | "createdAt"
>;
