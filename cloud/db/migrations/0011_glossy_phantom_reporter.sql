ALTER TABLE "environments" DROP CONSTRAINT "environments_project_id_name_unique";--> statement-breakpoint
ALTER TABLE "organizations" DROP CONSTRAINT "organizations_name_unique";--> statement-breakpoint
ALTER TABLE "environments" ADD COLUMN "slug" text NOT NULL;--> statement-breakpoint
ALTER TABLE "organizations" ADD COLUMN "slug" text NOT NULL;--> statement-breakpoint
ALTER TABLE "projects" ADD COLUMN "slug" text NOT NULL;--> statement-breakpoint
ALTER TABLE "environments" ADD CONSTRAINT "environments_project_id_slug_unique" UNIQUE("project_id","slug");--> statement-breakpoint
ALTER TABLE "organizations" ADD CONSTRAINT "organizations_slug_unique" UNIQUE("slug");--> statement-breakpoint
ALTER TABLE "projects" ADD CONSTRAINT "projects_organization_id_slug_unique" UNIQUE("organization_id","slug");