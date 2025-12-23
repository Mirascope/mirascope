ALTER TABLE "project_memberships" DROP CONSTRAINT "project_memberships_member_id_users_id_fk";
--> statement-breakpoint
ALTER TABLE "project_memberships" ADD COLUMN "organization_id" uuid NOT NULL;--> statement-breakpoint
ALTER TABLE "project_memberships" ADD CONSTRAINT "project_memberships_member_id_organization_id_organization_memberships_member_id_organization_id_fk" FOREIGN KEY ("member_id","organization_id") REFERENCES "public"."organization_memberships"("member_id","organization_id") ON DELETE cascade ON UPDATE no action;