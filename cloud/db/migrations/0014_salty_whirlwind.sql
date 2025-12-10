CREATE TABLE "annotations" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"span_db_id" uuid NOT NULL,
	"trace_db_id" uuid NOT NULL,
	"span_id" text NOT NULL,
	"trace_id" text NOT NULL,
	"label" text,
	"reasoning" text,
	"data" jsonb,
	"environment_id" uuid NOT NULL,
	"project_id" uuid NOT NULL,
	"organization_id" uuid NOT NULL,
	"created_by" uuid,
	"created_at" timestamp DEFAULT now(),
	"updated_at" timestamp DEFAULT now(),
	CONSTRAINT "annotations_span_id_trace_id_environment_id_unique" UNIQUE("span_id","trace_id","environment_id"),
	CONSTRAINT "annotations_span_db_id_environment_id_unique" UNIQUE("span_db_id","environment_id")
);
--> statement-breakpoint
ALTER TABLE "annotations" ADD CONSTRAINT "annotations_span_db_id_spans_id_fk" FOREIGN KEY ("span_db_id") REFERENCES "public"."spans"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "annotations" ADD CONSTRAINT "annotations_trace_db_id_traces_id_fk" FOREIGN KEY ("trace_db_id") REFERENCES "public"."traces"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "annotations" ADD CONSTRAINT "annotations_environment_id_environments_id_fk" FOREIGN KEY ("environment_id") REFERENCES "public"."environments"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "annotations" ADD CONSTRAINT "annotations_project_id_projects_id_fk" FOREIGN KEY ("project_id") REFERENCES "public"."projects"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "annotations" ADD CONSTRAINT "annotations_organization_id_organizations_id_fk" FOREIGN KEY ("organization_id") REFERENCES "public"."organizations"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "annotations" ADD CONSTRAINT "annotations_created_by_users_id_fk" FOREIGN KEY ("created_by") REFERENCES "public"."users"("id") ON DELETE set null ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "annotations_trace_idx" ON "annotations" USING btree ("trace_db_id");--> statement-breakpoint
CREATE INDEX "annotations_env_created_at_idx" ON "annotations" USING btree ("environment_id","created_at");