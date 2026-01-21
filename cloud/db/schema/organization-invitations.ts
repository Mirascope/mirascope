import { relations, sql } from "drizzle-orm";
import {
  check,
  pgEnum,
  pgTable,
  text,
  timestamp,
  uuid,
} from "drizzle-orm/pg-core";
import { organizations } from "@/db/schema/organizations";
import { users } from "@/db/schema/users";

export const invitationStatusEnum = pgEnum("invitation_status", [
  "pending",
  "accepted",
  "revoked",
]);

export const invitationRoleEnum = pgEnum("invitation_role", [
  "ADMIN",
  "MEMBER",
]);

export const organizationInvitations = pgTable(
  "organization_invitations",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    organizationId: uuid("organization_id")
      .references(() => organizations.id, { onDelete: "cascade" })
      .notNull(),
    senderId: uuid("sender_id")
      .references(() => users.id)
      .notNull(),
    recipientEmail: text("recipient_email").notNull(),
    role: invitationRoleEnum("role").notNull(),
    token: text("token").notNull().unique(),
    status: invitationStatusEnum("status").notNull().default("pending"),
    expiresAt: timestamp("expires_at").notNull(),
    createdAt: timestamp("created_at").defaultNow().notNull(),
    updatedAt: timestamp("updated_at").defaultNow().notNull(),
    acceptedAt: timestamp("accepted_at"),
    revokedAt: timestamp("revoked_at"),
  },
  (table) => ({
    validExpiration: check(
      "valid_expiration",
      sql`${table.expiresAt} > ${table.createdAt}`,
    ),
  }),
);

export const organizationInvitationsRelations = relations(
  organizationInvitations,
  ({ one }) => ({
    organization: one(organizations, {
      fields: [organizationInvitations.organizationId],
      references: [organizations.id],
    }),
    sender: one(users, {
      fields: [organizationInvitations.senderId],
      references: [users.id],
    }),
  }),
);

// Internal types
export type OrganizationInvitation =
  typeof organizationInvitations.$inferSelect;
export type NewOrganizationInvitation =
  typeof organizationInvitations.$inferInsert;
export type InvitationStatus = (typeof invitationStatusEnum.enumValues)[number];
export type InvitationRole = (typeof invitationRoleEnum.enumValues)[number];

// Public types (excludes sensitive token field)
export type PublicOrganizationInvitation = Omit<
  OrganizationInvitation,
  "token"
>;
