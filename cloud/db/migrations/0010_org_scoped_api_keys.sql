-- Add org-scoped API key support
-- Org-scoped keys have organization_id set and environment_id null.
-- Environment-scoped keys (existing) have environment_id set and organization_id null.

-- Make environment_id nullable (was NOT NULL)
ALTER TABLE "api_keys" ALTER COLUMN "environment_id" DROP NOT NULL;

-- Add organization_id column
ALTER TABLE "api_keys" ADD COLUMN "organization_id" uuid REFERENCES "organizations"("id") ON DELETE CASCADE;

-- Add check constraint: exactly one of environment_id or organization_id must be set
ALTER TABLE "api_keys" ADD CONSTRAINT "api_key_scope_check"
  CHECK (
    (environment_id IS NOT NULL AND organization_id IS NULL)
    OR (environment_id IS NULL AND organization_id IS NOT NULL)
  );

-- Add unique constraint for org-scoped key names
ALTER TABLE "api_keys" ADD CONSTRAINT "api_keys_organization_id_name_unique" UNIQUE ("organization_id", "name");
