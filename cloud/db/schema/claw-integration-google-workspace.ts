import { relations } from "drizzle-orm";
import { pgTable, text, timestamp, unique, uuid } from "drizzle-orm/pg-core";

import { claws } from "./claws";
import { users } from "./users";

export const clawIntegrationGoogleWorkspace = pgTable(
  "claw_integration_google_workspace",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    clawId: uuid("claw_id")
      .references(() => claws.id, { onDelete: "cascade" })
      .notNull(),
    userId: uuid("user_id")
      .references(() => users.id)
      .notNull(),
    encryptedRefreshToken: text("encrypted_refresh_token").notNull(),
    refreshTokenKeyId: text("refresh_token_key_id").notNull(),
    scopes: text("scopes").notNull(),
    connectedEmail: text("connected_email").notNull(),
    tokenExpiresAt: timestamp("token_expires_at", { withTimezone: true }),
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow(),
  },
  (table) => ({
    uniqueClaw: unique().on(table.clawId),
  }),
);

export const clawIntegrationGoogleWorkspaceRelations = relations(
  clawIntegrationGoogleWorkspace,
  ({ one }) => ({
    claw: one(claws, {
      fields: [clawIntegrationGoogleWorkspace.clawId],
      references: [claws.id],
    }),
    user: one(users, {
      fields: [clawIntegrationGoogleWorkspace.userId],
      references: [users.id],
    }),
  }),
);

// Internal types
export type ClawIntegrationGoogleWorkspace =
  typeof clawIntegrationGoogleWorkspace.$inferSelect;
export type NewClawIntegrationGoogleWorkspace =
  typeof clawIntegrationGoogleWorkspace.$inferInsert;

// Public types for API responses (excludes encrypted token)
export type PublicClawIntegrationGoogleWorkspace = Pick<
  ClawIntegrationGoogleWorkspace,
  | "id"
  | "clawId"
  | "userId"
  | "scopes"
  | "connectedEmail"
  | "tokenExpiresAt"
  | "createdAt"
  | "updatedAt"
>;
