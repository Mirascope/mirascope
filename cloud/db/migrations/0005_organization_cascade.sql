-- Ensure organization deletion cascades to memberships + membership audits.
-- This migration intentionally touches ONLY organization-related foreign keys.

ALTER TABLE "organization_memberships"
DROP CONSTRAINT "organization_memberships_organization_id_organizations_id_fk";
--> statement-breakpoint

ALTER TABLE "organization_membership_audit"
DROP CONSTRAINT "organization_membership_audit_organization_id_organizations_id_fk";
--> statement-breakpoint

ALTER TABLE "organization_memberships"
ADD CONSTRAINT "organization_memberships_organization_id_organizations_id_fk"
FOREIGN KEY ("organization_id") REFERENCES "public"."organizations"("id")
ON DELETE cascade ON UPDATE no action;
--> statement-breakpoint

ALTER TABLE "organization_membership_audit"
ADD CONSTRAINT "organization_membership_audit_organization_id_organizations_id_fk"
FOREIGN KEY ("organization_id") REFERENCES "public"."organizations"("id")
ON DELETE cascade ON UPDATE no action;

