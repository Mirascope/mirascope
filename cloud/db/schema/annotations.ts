import { relations } from "drizzle-orm";
import {
  pgTable,
  text,
  timestamp,
  uuid,
  unique,
  jsonb,
  index,
} from "drizzle-orm/pg-core";
import { spans } from "./spans";
import { traces } from "./traces";
import { environments } from "./environments";
import { projects } from "./projects";
import { organizations } from "./organizations";
import { users } from "./users";

export const annotations = pgTable(
  "annotations",
  {
    id: uuid("id").primaryKey().defaultRandom(),

    // Target (span or trace level) - FK references
    spanDbId: uuid("span_db_id")
      .references(() => spans.id, { onDelete: "cascade" })
      .notNull(),
    traceDbId: uuid("trace_db_id")
      .references(() => traces.id, { onDelete: "cascade" })
      .notNull(),

    // Raw OTLP identifiers (for idempotent requests / backward compatibility)
    spanId: text("span_id").notNull(),
    traceId: text("trace_id").notNull(),

    // Annotation content
    label: text("label"), // "pass" | "fail" | custom
    reasoning: text("reasoning"), // Human explanation
    data: jsonb("data").$type<Record<string, unknown>>(), // Arbitrary structured data

    // Scope
    environmentId: uuid("environment_id")
      .references(() => environments.id, { onDelete: "cascade" })
      .notNull(),
    projectId: uuid("project_id")
      .references(() => projects.id, { onDelete: "cascade" })
      .notNull(),
    organizationId: uuid("organization_id")
      .references(() => organizations.id, { onDelete: "cascade" })
      .notNull(),

    // Audit
    createdBy: uuid("created_by").references(() => users.id, {
      onDelete: "set null",
    }),
    createdAt: timestamp("created_at").defaultNow(),
    updatedAt: timestamp("updated_at").defaultNow(),
  },
  (table) => ({
    // Unique annotation per span+trace+environment (using raw OTLP IDs)
    spanEnvUnique: unique().on(
      table.spanId,
      table.traceId,
      table.environmentId,
    ),
    // Also unique by DB IDs
    spanDbUnique: unique().on(table.spanDbId, table.environmentId),
    // Query annotations by trace
    traceIdx: index("annotations_trace_idx").on(table.traceDbId),
    // Query by environment and time
    envCreatedAtIdx: index("annotations_env_created_at_idx").on(
      table.environmentId,
      table.createdAt,
    ),
  }),
);

export const annotationsRelations = relations(annotations, ({ one }) => ({
  span: one(spans, {
    fields: [annotations.spanDbId],
    references: [spans.id],
  }),
  trace: one(traces, {
    fields: [annotations.traceDbId],
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

// Internal types
export type Annotation = typeof annotations.$inferSelect;
export type NewAnnotation = typeof annotations.$inferInsert;

// Public types for API responses
export type PublicAnnotation = Pick<
  Annotation,
  | "id"
  | "spanDbId"
  | "traceDbId"
  | "spanId"
  | "traceId"
  | "label"
  | "reasoning"
  | "data"
  | "environmentId"
  | "projectId"
  | "organizationId"
  | "createdBy"
  | "createdAt"
  | "updatedAt"
>;
