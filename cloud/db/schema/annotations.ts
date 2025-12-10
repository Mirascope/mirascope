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

    spanDbId: uuid("span_db_id")
      .references(() => spans.id, { onDelete: "cascade" })
      .notNull(),
    traceDbId: uuid("trace_db_id")
      .references(() => traces.id, { onDelete: "cascade" })
      .notNull(),

    spanId: text("span_id").notNull(),
    traceId: text("trace_id").notNull(),

    label: text("label"),
    reasoning: text("reasoning"),
    data: jsonb("data").$type<Record<string, unknown>>(),
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
    spanEnvUnique: unique().on(
      table.spanId,
      table.traceId,
      table.environmentId,
    ),
    spanDbUnique: unique().on(table.spanDbId, table.environmentId),
    traceIdx: index("annotations_trace_idx").on(table.traceDbId),
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

export type Annotation = typeof annotations.$inferSelect;
export type NewAnnotation = typeof annotations.$inferInsert;

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
