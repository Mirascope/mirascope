ALTER TABLE "traces" ADD CONSTRAINT "traces_id_project_id_organization_id_unique" UNIQUE("id","project_id","organization_id");--> statement-breakpoint
ALTER TABLE "spans" ADD CONSTRAINT "spans_trace_org_consistency_fk" FOREIGN KEY ("trace_db_id","project_id","organization_id") REFERENCES "public"."traces"("id","project_id","organization_id") ON DELETE cascade ON UPDATE no action;
