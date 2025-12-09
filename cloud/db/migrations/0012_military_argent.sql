CREATE TABLE "traces" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"trace_id" text NOT NULL,
	"environment_id" uuid NOT NULL,
	"project_id" uuid NOT NULL,
	"organization_id" uuid NOT NULL,
	"service_name" text,
	"service_version" text,
	"resource_attributes" jsonb,
	"created_at" timestamp DEFAULT now(),
	CONSTRAINT "traces_trace_id_environment_id_unique" UNIQUE("trace_id","environment_id"),
	CONSTRAINT "traces_id_trace_id_environment_id_unique" UNIQUE("id","trace_id","environment_id")
);
--> statement-breakpoint
CREATE TABLE "spans" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"trace_db_id" uuid NOT NULL,
	"trace_id" text NOT NULL,
	"span_id" text NOT NULL,
	"parent_span_id" text,
	"environment_id" uuid NOT NULL,
	"project_id" uuid NOT NULL,
	"organization_id" uuid NOT NULL,
	"name" text NOT NULL,
	"kind" integer,
	"start_time_unix_nano" bigint,
	"end_time_unix_nano" bigint,
	"attributes" jsonb,
	"status" jsonb,
	"events" jsonb,
	"links" jsonb,
	"dropped_attributes_count" integer,
	"dropped_events_count" integer,
	"dropped_links_count" integer,
	"created_at" timestamp DEFAULT now(),
	CONSTRAINT "spans_span_id_trace_id_environment_id_unique" UNIQUE("span_id","trace_id","environment_id")
);
--> statement-breakpoint
ALTER TABLE "traces" ADD CONSTRAINT "traces_environment_id_environments_id_fk" FOREIGN KEY ("environment_id") REFERENCES "public"."environments"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "traces" ADD CONSTRAINT "traces_project_id_projects_id_fk" FOREIGN KEY ("project_id") REFERENCES "public"."projects"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "traces" ADD CONSTRAINT "traces_organization_id_organizations_id_fk" FOREIGN KEY ("organization_id") REFERENCES "public"."organizations"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "spans" ADD CONSTRAINT "spans_environment_id_environments_id_fk" FOREIGN KEY ("environment_id") REFERENCES "public"."environments"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "spans" ADD CONSTRAINT "spans_project_id_projects_id_fk" FOREIGN KEY ("project_id") REFERENCES "public"."projects"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "spans" ADD CONSTRAINT "spans_organization_id_organizations_id_fk" FOREIGN KEY ("organization_id") REFERENCES "public"."organizations"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "spans" ADD CONSTRAINT "spans_trace_consistency_fk" FOREIGN KEY ("trace_db_id","trace_id","environment_id") REFERENCES "public"."traces"("id","trace_id","environment_id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "traces_env_created_at_idx" ON "traces" USING btree ("environment_id","created_at");--> statement-breakpoint
CREATE INDEX "traces_env_service_name_idx" ON "traces" USING btree ("environment_id","service_name");--> statement-breakpoint
CREATE INDEX "spans_env_created_at_idx" ON "spans" USING btree ("environment_id","created_at");--> statement-breakpoint
CREATE INDEX "spans_trace_db_id_idx" ON "spans" USING btree ("trace_db_id");--> statement-breakpoint
CREATE INDEX "spans_start_time_idx" ON "spans" USING btree ("start_time_unix_nano");--> statement-breakpoint
CREATE INDEX "spans_env_start_time_idx" ON "spans" USING btree ("environment_id","start_time_unix_nano");