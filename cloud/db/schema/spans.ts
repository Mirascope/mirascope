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
    traceId: uuid("trace_id").notNull(),
    otelTraceId: text("otel_trace_id").notNull(),
    otelSpanId: text("otel_span_id").notNull(),
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
    uniqueOtelSpanTraceEnvironment: unique().on(
      table.otelSpanId,
      table.otelTraceId,
      table.environmentId,
    ),
    // Composite unique constraints for annotations foreign key references
    uniqueOtelSpanId: unique("spans_id_span_id_unique").on(
      table.id,
      table.otelSpanId,
    ),
    uniqueOrgProjectSpanId: unique(
      "spans_id_project_id_organization_id_unique",
    ).on(table.organizationId, table.projectId, table.id),
    // Composite foreign key to ensure otel_trace_id and environment_id match the referenced trace
    traceConsistencyFk: foreignKey({
      columns: [table.traceId, table.otelTraceId, table.environmentId],
      foreignColumns: [traces.id, traces.otelTraceId, traces.environmentId],
      name: "spans_trace_consistency_fk",
    }).onDelete("cascade"),
    // Composite foreign key to ensure project_id and organization_id match the referenced trace
    traceOrgConsistencyFk: foreignKey({
      columns: [table.organizationId, table.projectId, table.traceId],
      foreignColumns: [traces.organizationId, traces.projectId, traces.id],
      name: "spans_trace_org_consistency_fk",
    }).onDelete("cascade"),
    environmentCreatedAtIndex: index("spans_env_created_at_idx").on(
      table.environmentId,
      table.createdAt,
    ),
    traceIdIndex: index("spans_trace_id_idx").on(table.traceId),
    startTimeIndex: index("spans_start_time_idx").on(table.startTimeUnixNano),
    environmentStartTimeIndex: index("spans_env_start_time_idx").on(
      table.environmentId,
      table.startTimeUnixNano,
    ),
  }),
);

export const spansRelations = relations(spans, ({ one }) => ({
  trace: one(traces, {
    fields: [spans.traceId],
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
  | "traceId"
  | "otelTraceId"
  | "otelSpanId"
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
