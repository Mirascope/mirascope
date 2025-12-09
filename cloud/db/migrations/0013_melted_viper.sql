ALTER TABLE "spans" DROP CONSTRAINT "spans_trace_db_id_traces_id_fk";
--> statement-breakpoint
ALTER TABLE "traces" ADD CONSTRAINT "traces_id_trace_id_environment_id_unique" UNIQUE("id","trace_id","environment_id");
--> statement-breakpoint
ALTER TABLE "spans" ADD CONSTRAINT "spans_trace_consistency_fk" FOREIGN KEY ("trace_db_id","trace_id","environment_id") REFERENCES "public"."traces"("id","trace_id","environment_id") ON DELETE cascade ON UPDATE no action;