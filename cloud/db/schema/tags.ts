import { relations } from "drizzle-orm";
import { pgTable, text, timestamp, uuid, unique } from "drizzle-orm/pg-core";
import { projects } from "./projects";
import { organizations } from "./organizations";
import { users } from "./users";

export const tags = pgTable(
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

export const tagsRelations = relations(tags, ({ one }) => ({
  project: one(projects, {
    fields: [tags.projectId],
    references: [projects.id],
  }),
  organization: one(organizations, {
    fields: [tags.organizationId],
    references: [organizations.id],
  }),
  createdByUser: one(users, {
    fields: [tags.createdBy],
    references: [users.id],
  }),
}));

export type Tag = typeof tags.$inferSelect;
export type NewTag = typeof tags.$inferInsert;

export type PublicTag = Pick<
  Tag,
  | "id"
  | "name"
  | "projectId"
  | "organizationId"
  | "createdBy"
  | "createdAt"
  | "updatedAt"
>;
