import { relations } from "drizzle-orm";
import {
  pgTable,
  text,
  timestamp,
  uuid,
  unique,
  jsonb,
  integer,
  index,
  bigint,
  foreignKey,
} from "drizzle-orm/pg-core";
import { traces } from "./traces";
import { environments } from "./environments";
import { projects } from "./projects";
import { organizations } from "./organizations";

export const spans = pgTable(
  "spans",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    traceDbId: uuid("trace_db_id").notNull(),
    traceId: text("trace_id").notNull(),
    spanId: text("span_id").notNull(),
    parentSpanId: text("parent_span_id"),
    environmentId: uuid("environment_id")
      .references(() => environments.id, { onDelete: "cascade" })
      .notNull(),
    projectId: uuid("project_id")
      .references(() => projects.id, { onDelete: "cascade" })
      .notNull(),
    organizationId: uuid("organization_id")
      .references(() => organizations.id, { onDelete: "cascade" })
      .notNull(),
    name: text("name").notNull(),
    kind: integer("kind"),
    startTimeUnixNano: bigint("start_time_unix_nano", { mode: "bigint" }),
    endTimeUnixNano: bigint("end_time_unix_nano", { mode: "bigint" }),
    attributes: jsonb("attributes"),
    status: jsonb("status"),
    events: jsonb("events"),
    links: jsonb("links"),
    droppedAttributesCount: integer("dropped_attributes_count"),
    droppedEventsCount: integer("dropped_events_count"),
    droppedLinksCount: integer("dropped_links_count"),
    createdAt: timestamp("created_at").defaultNow(),
  },
  (table) => ({
    spanTraceEnvUnique: unique().on(
      table.spanId,
      table.traceId,
      table.environmentId,
    ),
    // Composite foreign key to ensure trace_id and environment_id match the referenced trace
    traceConsistencyFk: foreignKey({
      columns: [table.traceDbId, table.traceId, table.environmentId],
      foreignColumns: [traces.id, traces.traceId, traces.environmentId],
      name: "spans_trace_consistency_fk",
    }).onDelete("cascade"),
    // Composite foreign key to ensure project_id and organization_id match the referenced trace
    traceOrgConsistencyFk: foreignKey({
      columns: [table.traceDbId, table.projectId, table.organizationId],
      foreignColumns: [traces.id, traces.projectId, traces.organizationId],
      name: "spans_trace_org_consistency_fk",
    }).onDelete("cascade"),
    envCreatedAtIdx: index("spans_env_created_at_idx").on(
      table.environmentId,
      table.createdAt,
    ),
    traceDbIdIdx: index("spans_trace_db_id_idx").on(table.traceDbId),
    startTimeIdx: index("spans_start_time_idx").on(table.startTimeUnixNano),
    envStartTimeIdx: index("spans_env_start_time_idx").on(
      table.environmentId,
      table.startTimeUnixNano,
    ),
  }),
);

export const spansRelations = relations(spans, ({ one }) => ({
  trace: one(traces, {
    fields: [spans.traceDbId],
    references: [traces.id],
  }),
  environment: one(environments, {
    fields: [spans.environmentId],
    references: [environments.id],
  }),
  project: one(projects, {
    fields: [spans.projectId],
    references: [projects.id],
  }),
  organization: one(organizations, {
    fields: [spans.organizationId],
    references: [organizations.id],
  }),
}));

// Internal types
export type Span = typeof spans.$inferSelect;
export type NewSpan = typeof spans.$inferInsert;

// Public types for API responses
export type PublicSpan = Pick<
  Span,
  | "id"
  | "traceDbId"
  | "traceId"
  | "spanId"
  | "parentSpanId"
  | "environmentId"
  | "projectId"
  | "organizationId"
  | "name"
  | "kind"
  | "startTimeUnixNano"
  | "endTimeUnixNano"
  | "attributes"
  | "status"
  | "events"
  | "links"
  | "droppedAttributesCount"
  | "droppedEventsCount"
  | "droppedLinksCount"
  | "createdAt"
>;
