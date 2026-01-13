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
import { environments } from "./environments";
import { projects } from "./projects";
import { organizations } from "./organizations";

export const traces = pgTable(
  "traces",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    otelTraceId: text("otel_trace_id").notNull(),
    environmentId: uuid("environment_id")
      .references(() => environments.id, { onDelete: "cascade" })
      .notNull(),
    projectId: uuid("project_id")
      .references(() => projects.id, { onDelete: "cascade" })
      .notNull(),
    organizationId: uuid("organization_id")
      .references(() => organizations.id, { onDelete: "cascade" })
      .notNull(),
    serviceName: text("service_name"),
    serviceVersion: text("service_version"),
    resourceAttributes: jsonb("resource_attributes").$type<
      Record<string, unknown>
    >(),
    createdAt: timestamp("created_at").defaultNow(),
  },
  (table) => ({
    uniqueOtelTraceEnvironment: unique().on(
      table.otelTraceId,
      table.environmentId,
    ),
    // Composite unique constraint for spans foreign key reference
    uniqueOtelTraceIdEnvironmentId: unique(
      "traces_id_trace_id_environment_id_unique",
    ).on(table.id, table.otelTraceId, table.environmentId),
    // Composite unique constraint for spans org consistency foreign key
    uniqueOrgProjectTraceId: unique(
      "traces_id_project_id_organization_id_unique",
    ).on(table.organizationId, table.projectId, table.id),
    // Composite unique constraint for annotations otel consistency foreign key
    uniqueOtelTraceId: unique("traces_id_trace_id_unique").on(
      table.id,
      table.otelTraceId,
    ),
    environmentCreatedAtIndex: index("traces_env_created_at_idx").on(
      table.environmentId,
      table.createdAt,
    ),
    environmentServiceNameIndex: index("traces_env_service_name_idx").on(
      table.environmentId,
      table.serviceName,
    ),
  }),
);

export const tracesRelations = relations(traces, ({ one }) => ({
  environment: one(environments, {
    fields: [traces.environmentId],
    references: [environments.id],
  }),
  project: one(projects, {
    fields: [traces.projectId],
    references: [projects.id],
  }),
  organization: one(organizations, {
    fields: [traces.organizationId],
    references: [organizations.id],
  }),
}));

// Internal types
export type Trace = typeof traces.$inferSelect;
export type NewTrace = typeof traces.$inferInsert;

// Public types for API responses
export type PublicTrace = Pick<
  Trace,
  | "id"
  | "otelTraceId"
  | "environmentId"
  | "projectId"
  | "organizationId"
  | "serviceName"
  | "serviceVersion"
  | "resourceAttributes"
  | "createdAt"
>;

// Type for the create response (includes ingestion stats)
export type CreateTraceResponse = {
  acceptedSpans: number;
  rejectedSpans: number;
};
