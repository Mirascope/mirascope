import { relations, sql } from "drizzle-orm";
import { check, pgTable, text, timestamp, uuid } from "drizzle-orm/pg-core";
import { users } from "./users";
import { organizations } from "./organizations";
import { projectMemberships } from "@/db/schema/project-memberships";

export const projects = pgTable(
  "projects",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    name: text("name").notNull(),
    userOwnerId: uuid("user_owner_id").references(() => users.id, {
      onDelete: "cascade",
    }),
    orgOwnerId: uuid("org_owner_id").references(() => organizations.id, {
      onDelete: "cascade",
    }),
    createdByUserId: uuid("created_by_user_id")
      .references(() => users.id)
      .notNull(),
    createdAt: timestamp("created_at").defaultNow(),
    updatedAt: timestamp("updated_at").defaultNow(),
  },
  (table) => [
    check(
      "check_one_owner",
      sql`(${table.userOwnerId} IS NOT NULL AND ${table.orgOwnerId} IS NULL) OR (${table.userOwnerId} IS NULL AND ${table.orgOwnerId} IS NOT NULL)`,
    ),
  ],
);

export const projectsRelations = relations(projects, ({ one, many }) => ({
  createdBy: one(users, {
    fields: [projects.createdByUserId],
    references: [users.id],
  }),
  userOwner: one(users, {
    fields: [projects.userOwnerId],
    references: [users.id],
  }),
  orgOwner: one(organizations, {
    fields: [projects.orgOwnerId],
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
  "id" | "name" | "userOwnerId" | "orgOwnerId"
>;
