import { pgEnum, pgTable, text, timestamp, uuid } from "drizzle-orm/pg-core";

export const accountTypeEnum = pgEnum("account_type", ["user", "claw"]);

export const users = pgTable("users", {
  id: uuid("id").primaryKey().defaultRandom(),
  email: text("email").notNull().unique(),
  name: text("name"),
  accountType: accountTypeEnum("account_type").notNull().default("user"),
  deletedAt: timestamp("deleted_at", { withTimezone: true }), // null = active, non-null = soft-deleted
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow(),
});

// Internal types
export type User = typeof users.$inferSelect;
export type NewUser = typeof users.$inferInsert;
export type AccountType = (typeof accountTypeEnum.enumValues)[number];

// Public types for API responses
export type PublicUser = Pick<
  User,
  "id" | "email" | "name" | "accountType" | "deletedAt"
>;
