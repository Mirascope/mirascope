import { relations } from "drizzle-orm";
import {
  pgTable,
  text,
  timestamp,
  uuid,
  unique,
  jsonb,
  index,
  pgEnum,
  foreignKey,
} from "drizzle-orm/pg-core";
import { spans } from "./spans";
import { traces } from "./traces";
import { environments } from "./environments";
import { projects } from "./projects";
import { organizations } from "./organizations";
import { users } from "./users";

export const labelEnum = pgEnum("annotation_label", ["pass", "fail"]);

export const annotations = pgTable(
  "annotations",
  {
    id: uuid("id").primaryKey().defaultRandom(),

    spanId: uuid("span_id")
      .references(() => spans.id, { onDelete: "cascade" })
      .notNull(),
    traceId: uuid("trace_id")
      .references(() => traces.id, { onDelete: "cascade" })
      .notNull(),

    otelSpanId: text("otel_span_id").notNull(),
    otelTraceId: text("otel_trace_id").notNull(),

    label: labelEnum("label"),
    reasoning: text("reasoning"),
    metadata: jsonb("metadata").$type<Record<string, unknown>>(),
    environmentId: uuid("environment_id")
      .references(() => environments.id, { onDelete: "cascade" })
      .notNull(),
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
    uniqueOtelSpanTraceEnvironment: unique().on(
      table.otelSpanId,
      table.otelTraceId,
      table.environmentId,
    ),
    uniqueSpanEnvironment: unique().on(table.spanId, table.environmentId),
    spanOtelConsistencyFk: foreignKey({
      columns: [table.spanId, table.otelSpanId],
      foreignColumns: [spans.id, spans.otelSpanId],
      name: "annotations_span_otel_consistency_fk",
    }).onDelete("cascade"),
    traceOtelConsistencyFk: foreignKey({
      columns: [table.traceId, table.otelTraceId],
      foreignColumns: [traces.id, traces.otelTraceId],
      name: "annotations_trace_otel_consistency_fk",
    }).onDelete("cascade"),
    spanConsistencyFk: foreignKey({
      columns: [table.organizationId, table.projectId, table.spanId],
      foreignColumns: [spans.organizationId, spans.projectId, spans.id],
      name: "annotations_span_consistency_fk",
    }).onDelete("cascade"),
    traceConsistencyFk: foreignKey({
      columns: [table.organizationId, table.projectId, table.traceId],
      foreignColumns: [traces.organizationId, traces.projectId, traces.id],
      name: "annotations_trace_consistency_fk",
    }).onDelete("cascade"),
    traceIdIndex: index("annotations_trace_id_idx").on(table.traceId),
  }),
);

export const annotationsRelations = relations(annotations, ({ one }) => ({
  span: one(spans, {
    fields: [annotations.spanId],
    references: [spans.id],
  }),
  trace: one(traces, {
    fields: [annotations.traceId],
    references: [traces.id],
  }),
  environment: one(environments, {
    fields: [annotations.environmentId],
    references: [environments.id],
  }),
  project: one(projects, {
    fields: [annotations.projectId],
    references: [projects.id],
  }),
  organization: one(organizations, {
    fields: [annotations.organizationId],
    references: [organizations.id],
  }),
  createdByUser: one(users, {
    fields: [annotations.createdBy],
    references: [users.id],
  }),
}));

export type Annotation = typeof annotations.$inferSelect;
export type NewAnnotation = typeof annotations.$inferInsert;

export type PublicAnnotation = Pick<
  Annotation,
  | "id"
  | "spanId"
  | "traceId"
  | "otelSpanId"
  | "otelTraceId"
  | "label"
  | "reasoning"
  | "metadata"
  | "environmentId"
  | "projectId"
  | "organizationId"
  | "createdBy"
  | "createdAt"
  | "updatedAt"
>;
