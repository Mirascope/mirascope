CREATE TYPE "public"."account_type" AS ENUM('user', 'claw');--> statement-breakpoint
ALTER TYPE "public"."organization_role" ADD VALUE 'BOT';--> statement-breakpoint
ALTER TABLE "claws" ADD COLUMN "bot_user_id" uuid;--> statement-breakpoint
ALTER TABLE "claws" ADD COLUMN "home_project_id" uuid;--> statement-breakpoint
ALTER TABLE "claws" ADD COLUMN "home_environment_id" uuid;--> statement-breakpoint
ALTER TABLE "users" ADD COLUMN "account_type" "account_type" DEFAULT 'user' NOT NULL;--> statement-breakpoint
ALTER TABLE "claws" ADD CONSTRAINT "claws_bot_user_id_users_id_fk" FOREIGN KEY ("bot_user_id") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "claws" ADD CONSTRAINT "claws_home_project_id_projects_id_fk" FOREIGN KEY ("home_project_id") REFERENCES "public"."projects"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "claws" ADD CONSTRAINT "claws_home_environment_id_environments_id_fk" FOREIGN KEY ("home_environment_id") REFERENCES "public"."environments"("id") ON DELETE no action ON UPDATE no action;