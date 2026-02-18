import { integer, pgTable, text, timestamp, uuid } from "drizzle-orm/pg-core";

export const fleetMacs = pgTable("fleet_macs", {
  id: uuid("id").primaryKey().defaultRandom(),
  hostname: text("hostname").notNull().unique(),
  /** Hardware model: "mini", "macbook", "studio", "pro" */
  model: text("model").notNull().default("mini"),
  tailscaleIp: text("tailscale_ip"),
  agentUrl: text("agent_url").notNull(),
  agentAuthTokenEncrypted: text("agent_auth_token_encrypted"),
  agentAuthTokenKeyId: text("agent_auth_token_key_id"),
  chip: text("chip"),
  ramGb: integer("ram_gb"),
  diskGb: integer("disk_gb"),
  maxClaws: integer("max_claws").notNull().default(12),
  portRangeStart: integer("port_range_start").notNull().default(3001),
  portRangeEnd: integer("port_range_end").notNull().default(3100),
  tunnelHostnameSuffix: text("tunnel_hostname_suffix").notNull(),
  status: text("status").notNull().default("active"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow(),
});

export type Mac = typeof fleetMacs.$inferSelect;
export type NewMac = typeof fleetMacs.$inferInsert;
