import { relations } from "drizzle-orm";
import { pgTable, text, timestamp, uuid, unique } from "drizzle-orm/pg-core";

import { projectMemberships } from "@/db/schema/project-memberships";

import { organizations } from "./organizations";
import { users } from "./users";

export const projects = pgTable(
  "projects",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    name: text("name").notNull(),
    slug: text("slug").notNull(),
    organizationId: uuid("organization_id")
      .references(() => organizations.id, { onDelete: "cascade" })
      .notNull(),
    createdByUserId: uuid("created_by_user_id")
      .references(() => users.id)
      .notNull(),
    type: text("type").notNull().default("standard"),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow(),
  },
  (table) => ({
    uniqueOrgSlug: unique().on(table.organizationId, table.slug),
    uniqueOrgProjectId: unique().on(table.organizationId, table.id),
  }),
);

export const projectsRelations = relations(projects, ({ one, many }) => ({
  createdBy: one(users, {
    fields: [projects.createdByUserId],
    references: [users.id],
  }),
  organization: one(organizations, {
    fields: [projects.organizationId],
    references: [organizations.id],
  }),
  memberships: many(projectMemberships),
}));

// Internal types
export type Project = typeof projects.$inferSelect;
export type NewProject = typeof projects.$inferInsert;

// Public types for API responses
export type PublicProject = Pick<
  Project,
  "id" | "name" | "slug" | "organizationId" | "createdByUserId" | "type"
>;
