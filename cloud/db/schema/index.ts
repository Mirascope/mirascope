export * from "@/db/schema/sessions";
export * from "@/db/schema/users";
export * from "@/db/schema/organizations";
export * from "@/db/schema/organization-memberships";
export * from "@/db/schema/organization-membership-audit";

export type { PublicSession } from "@/db/schema/sessions";
export type { PublicUser } from "@/db/schema/users";
export type { PublicOrganization } from "@/db/schema/organizations";
export type {
  PublicOrganizationMembership,
  PublicOrganizationWithMembership,
  OrganizationRole,
} from "@/db/schema/organization-memberships";
export type {
  PublicOrganizationMembershipAudit,
  AuditAction,
} from "@/db/schema/organization-membership-audit";

import { users } from "@/db/schema/users";
import { sessions } from "@/db/schema/sessions";
import { organizations } from "@/db/schema/organizations";
import { organizationMemberships } from "@/db/schema/organization-memberships";
import { organizationMembershipAudit } from "@/db/schema/organization-membership-audit";

export type DatabaseTable =
  | typeof users
  | typeof sessions
  | typeof organizations
  | typeof organizationMemberships
  | typeof organizationMembershipAudit;
