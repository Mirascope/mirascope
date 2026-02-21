-- Add organization_id column for org-scoped API keys.
-- Environment-scoped keys have environment_id set (existing behavior).
-- Org-scoped keys have organization_id set and environment_id NULL.
-- Exactly one of environment_id or organization_id must be set.

ALTER TABLE "api_keys" ALTER COLUMN "environment_id" DROP NOT NULL;
ALTER TABLE "api_keys" ADD COLUMN "organization_id" uuid REFERENCES "organizations"("id") ON DELETE CASCADE;
ALTER TABLE "api_keys" ADD CONSTRAINT "api_keys_scope_check" CHECK (
  (environment_id IS NOT NULL AND organization_id IS NULL) OR
  (environment_id IS NULL AND organization_id IS NOT NULL)
);
-- Unique name within org for org-scoped keys (mirrors env-scoped unique constraint)
ALTER TABLE "api_keys" ADD CONSTRAINT "api_keys_organization_id_name_unique" UNIQUE ("organization_id", "name");
