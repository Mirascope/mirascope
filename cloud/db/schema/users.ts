import { pgTable, text, timestamp, uuid } from "drizzle-orm/pg-core";

export const users = pgTable("users", {
  id: uuid("id").primaryKey().defaultRandom(),
  email: text("email").notNull().unique(),
  name: text("name"),
  deletedAt: timestamp("deleted_at"), // null = active, non-null = soft-deleted
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
});

// Internal types
export type User = typeof users.$inferSelect;
export type NewUser = typeof users.$inferInsert;

// Public types for API responses
export type PublicUser = Pick<User, "id" | "email" | "name" | "deletedAt">;
