-- Organization roles: move from legacy "public.role" values (OWNER/ADMIN/DEVELOPER/VIEWER/ANNOTATOR)
-- to org-specific "public.organization_role" values (OWNER/ADMIN/MEMBER).
--
-- This migration intentionally touches ONLY organization tables.

ALTER TABLE "organization_memberships" ALTER COLUMN "role" SET DATA TYPE text;
--> statement-breakpoint
ALTER TABLE "organization_membership_audit" ALTER COLUMN "previous_role" SET DATA TYPE text;
--> statement-breakpoint
ALTER TABLE "organization_membership_audit" ALTER COLUMN "new_role" SET DATA TYPE text;
--> statement-breakpoint

UPDATE "organization_memberships"
SET "role" = 'MEMBER'
WHERE "role" IN ('DEVELOPER', 'VIEWER', 'ANNOTATOR');
--> statement-breakpoint

UPDATE "organization_membership_audit"
SET "previous_role" = 'MEMBER'
WHERE "previous_role" IN ('DEVELOPER', 'VIEWER', 'ANNOTATOR');
--> statement-breakpoint

UPDATE "organization_membership_audit"
SET "new_role" = 'MEMBER'
WHERE "new_role" IN ('DEVELOPER', 'VIEWER', 'ANNOTATOR');
--> statement-breakpoint

DROP TYPE IF EXISTS "public"."organization_role";
--> statement-breakpoint
CREATE TYPE "public"."organization_role" AS ENUM('OWNER', 'ADMIN', 'MEMBER');
--> statement-breakpoint

ALTER TABLE "organization_memberships"
ALTER COLUMN "role"
SET DATA TYPE "public"."organization_role" USING "role"::"public"."organization_role";
--> statement-breakpoint

ALTER TABLE "organization_membership_audit"
ALTER COLUMN "previous_role"
SET DATA TYPE "public"."organization_role" USING "previous_role"::"public"."organization_role";
--> statement-breakpoint

ALTER TABLE "organization_membership_audit"
ALTER COLUMN "new_role"
SET DATA TYPE "public"."organization_role" USING "new_role"::"public"."organization_role";
--> statement-breakpoint

DROP TYPE "public"."role";

