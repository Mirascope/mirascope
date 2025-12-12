ALTER TABLE
    "organization_memberships"
ALTER COLUMN
    "role"
SET
    DATA TYPE text;

--> statement-breakpoint
UPDATE
    "organization_memberships"
SET
    "role" = 'VIEWER'
WHERE
    "role" = 'ANNOTATOR';

--> statement-breakpoint
DROP TYPE "public"."role";

--> statement-breakpoint
CREATE TYPE "public"."role" AS ENUM('OWNER', 'ADMIN', 'DEVELOPER', 'VIEWER');

--> statement-breakpoint
ALTER TABLE
    "organization_memberships"
ALTER COLUMN
    "role"
SET
    DATA TYPE "public"."role" USING "role" :: "public"."role";
