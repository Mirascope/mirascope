CREATE TYPE "public"."audit_action" AS ENUM('GRANT', 'REVOKE', 'CHANGE');--> statement-breakpoint
CREATE TABLE "organization_membership_audit" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"organization_id" uuid NOT NULL,
	"actor_id" uuid NOT NULL,
	"target_id" uuid NOT NULL,
	"action" "audit_action" NOT NULL,
	"previous_role" "role",
	"new_role" "role",
	"created_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
ALTER TABLE "organization_membership_audit" ADD CONSTRAINT "organization_membership_audit_organization_id_organizations_id_fk" FOREIGN KEY ("organization_id") REFERENCES "public"."organizations"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "organization_membership_audit" ADD CONSTRAINT "organization_membership_audit_actor_id_users_id_fk" FOREIGN KEY ("actor_id") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "organization_membership_audit" ADD CONSTRAINT "organization_membership_audit_target_id_users_id_fk" FOREIGN KEY ("target_id") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;