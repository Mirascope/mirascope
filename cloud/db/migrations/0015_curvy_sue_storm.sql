CREATE TABLE "functions" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"hash" text NOT NULL,
	"signature_hash" text NOT NULL,
	"name" text NOT NULL,
	"description" text,
	"version" text NOT NULL,
	"tags" jsonb,
	"metadata" jsonb,
	"code" text NOT NULL,
	"signature" text NOT NULL,
	"dependencies" jsonb,
	"environment_id" uuid NOT NULL,
	"project_id" uuid NOT NULL,
	"organization_id" uuid NOT NULL,
	"created_at" timestamp DEFAULT now(),
	"updated_at" timestamp DEFAULT now(),
	CONSTRAINT "functions_environment_id_hash_unique" UNIQUE("environment_id","hash")
);
--> statement-breakpoint
ALTER TABLE "functions" ADD CONSTRAINT "functions_environment_id_environments_id_fk" FOREIGN KEY ("environment_id") REFERENCES "public"."environments"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "functions" ADD CONSTRAINT "functions_project_id_projects_id_fk" FOREIGN KEY ("project_id") REFERENCES "public"."projects"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "functions" ADD CONSTRAINT "functions_organization_id_organizations_id_fk" FOREIGN KEY ("organization_id") REFERENCES "public"."organizations"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "functions_env_name_idx" ON "functions" USING btree ("environment_id","name");--> statement-breakpoint
CREATE INDEX "functions_env_sig_hash_idx" ON "functions" USING btree ("environment_id","signature_hash");--> statement-breakpoint
ALTER TABLE "environments" ADD CONSTRAINT "environments_project_id_id_unique" UNIQUE("project_id","id");--> statement-breakpoint
ALTER TABLE "projects" ADD CONSTRAINT "projects_organization_id_id_unique" UNIQUE("organization_id","id");