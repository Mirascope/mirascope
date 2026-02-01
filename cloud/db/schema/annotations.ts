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
} from "drizzle-orm/pg-core";

import { environments } from "./environments";
import { organizations } from "./organizations";
import { projects } from "./projects";
import { users } from "./users";

export const labelEnum = pgEnum("annotation_label", ["pass", "fail"]);

export const annotations = pgTable(
  "annotations",
  {
    id: uuid("id").primaryKey().defaultRandom(),

    otelSpanId: text("otel_span_id").notNull(),
    otelTraceId: text("otel_trace_id").notNull(),

    label: labelEnum("label"),
    reasoning: text("reasoning"),
    metadata: jsonb("metadata").$type<Record<string, unknown>>(),
    tags: jsonb("tags").$type<string[]>(),
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
    createdAt: timestamp("created_at", { withTimezone: true }).defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow(),
  },
  (table) => ({
    uniqueOtelSpanTraceEnvironment: unique().on(
      table.otelSpanId,
      table.otelTraceId,
      table.environmentId,
    ),
    otelTraceIdIndex: index("annotations_otel_trace_id_idx").on(
      table.otelTraceId,
    ),
  }),
);

export const annotationsRelations = relations(annotations, ({ one }) => ({
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
  | "tags"
>;
