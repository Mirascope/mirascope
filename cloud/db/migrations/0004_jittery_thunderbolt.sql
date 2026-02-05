CREATE TYPE "public"."claw_role" AS ENUM('ADMIN', 'DEVELOPER', 'VIEWER', 'ANNOTATOR');--> statement-breakpoint
CREATE TYPE "public"."claw_instance_type" AS ENUM('basic', 'standard-2', 'standard-3', 'standard-4');--> statement-breakpoint
CREATE TYPE "public"."claw_status" AS ENUM('pending', 'provisioning', 'active', 'paused', 'error');--> statement-breakpoint
CREATE TABLE "claw_membership_audit" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"claw_id" uuid NOT NULL,
	"actor_id" uuid NOT NULL,
	"target_id" uuid NOT NULL,
	"action" "audit_action" NOT NULL,
	"previous_role" "claw_role",
	"new_role" "claw_role",
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "claw_memberships" (
	"member_id" uuid NOT NULL,
	"organization_id" uuid NOT NULL,
	"claw_id" uuid NOT NULL,
	"role" "claw_role" NOT NULL,
	"created_at" timestamp with time zone DEFAULT now(),
	"updated_at" timestamp with time zone DEFAULT now(),
	CONSTRAINT "claw_memberships_member_id_claw_id_pk" PRIMARY KEY("member_id","claw_id")
);
--> statement-breakpoint
CREATE TABLE "claws" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"slug" text NOT NULL,
	"display_name" text,
	"description" text,
	"organization_id" uuid NOT NULL,
	"created_by_user_id" uuid NOT NULL,
	"home_project_id" uuid,
	"status" "claw_status" DEFAULT 'pending' NOT NULL,
	"instance_type" "claw_instance_type" DEFAULT 'basic' NOT NULL,
	"last_deployed_at" timestamp with time zone,
	"last_error" text,
	"secrets_encrypted" text,
	"secrets_key_id" text,
	"bucket_name" text,
	"weekly_spending_guardrail_centicents" bigint,
	"weekly_window_start" timestamp with time zone,
	"weekly_usage_centicents" bigint,
	"burst_window_start" timestamp with time zone,
	"burst_usage_centicents" bigint,
	"created_at" timestamp with time zone DEFAULT now(),
	"updated_at" timestamp with time zone DEFAULT now(),
	CONSTRAINT "claws_organization_id_slug_unique" UNIQUE("organization_id","slug"),
	CONSTRAINT "claws_id_organization_id_unique" UNIQUE("id","organization_id")
);
--> statement-breakpoint
ALTER TABLE "claw_membership_audit" ADD CONSTRAINT "claw_membership_audit_claw_id_claws_id_fk" FOREIGN KEY ("claw_id") REFERENCES "public"."claws"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "claw_membership_audit" ADD CONSTRAINT "claw_membership_audit_actor_id_users_id_fk" FOREIGN KEY ("actor_id") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "claw_membership_audit" ADD CONSTRAINT "claw_membership_audit_target_id_users_id_fk" FOREIGN KEY ("target_id") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "claw_memberships" ADD CONSTRAINT "claw_memberships_member_id_organization_id_organization_memberships_member_id_organization_id_fk" FOREIGN KEY ("member_id","organization_id") REFERENCES "public"."organization_memberships"("member_id","organization_id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "claw_memberships" ADD CONSTRAINT "claw_memberships_claw_id_organization_id_claws_id_organization_id_fk" FOREIGN KEY ("claw_id","organization_id") REFERENCES "public"."claws"("id","organization_id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "claws" ADD CONSTRAINT "claws_organization_id_organizations_id_fk" FOREIGN KEY ("organization_id") REFERENCES "public"."organizations"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "claws" ADD CONSTRAINT "claws_created_by_user_id_users_id_fk" FOREIGN KEY ("created_by_user_id") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "claws" ADD CONSTRAINT "claws_home_project_id_projects_id_fk" FOREIGN KEY ("home_project_id") REFERENCES "public"."projects"("id") ON DELETE set null ON UPDATE no action;