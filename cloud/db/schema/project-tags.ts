import { relations } from "drizzle-orm";
import { pgTable, text, timestamp, uuid, unique } from "drizzle-orm/pg-core";
import { projects } from "./projects";
import { organizations } from "./organizations";
import { users } from "./users";

export const projectTags = pgTable(
  "project_tags",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    name: text("name").notNull(),
    projectId: uuid("project_id")
      .references(() => projects.id, { onDelete: "cascade" })
      .notNull(),
    organizationId: uuid("organization_id")
      .references(() => organizations.id, { onDelete: "cascade" })
      .notNull(),
    createdBy: uuid("created_by").references(() => users.id, {
      onDelete: "set null",
    }),
    createdAt: timestamp("created_at").defaultNow(),
    updatedAt: timestamp("updated_at").defaultNow(),
  },
  (table) => ({
    uniqueProjectName: unique().on(table.projectId, table.name),
  }),
);

export const projectTagsRelations = relations(projectTags, ({ one }) => ({
  project: one(projects, {
    fields: [projectTags.projectId],
    references: [projects.id],
  }),
  organization: one(organizations, {
    fields: [projectTags.organizationId],
    references: [organizations.id],
  }),
  createdByUser: one(users, {
    fields: [projectTags.createdBy],
    references: [users.id],
  }),
}));

export type ProjectTag = typeof projectTags.$inferSelect;
export type NewProjectTag = typeof projectTags.$inferInsert;

export type PublicProjectTag = Pick<
  ProjectTag,
  | "id"
  | "name"
  | "projectId"
  | "organizationId"
  | "createdBy"
  | "createdAt"
  | "updatedAt"
>;
