ALTER TYPE "public"."claw_instance_type" ADD VALUE 'lite' BEFORE 'basic';--> statement-breakpoint
ALTER TYPE "public"."claw_instance_type" ADD VALUE 'standard-1' BEFORE 'standard-2';--> statement-breakpoint
ALTER TABLE "claws" DROP CONSTRAINT "claws_home_project_id_projects_id_fk";
--> statement-breakpoint
ALTER TABLE "claws" DROP COLUMN "home_project_id";