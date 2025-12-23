export * from "@/db/schema/sessions";
export * from "@/db/schema/users";
export * from "@/db/schema/organizations";
export * from "@/db/schema/organization-memberships";
export * from "@/db/schema/organization-membership-audit";
export * from "@/db/schema/projects";
export * from "@/db/schema/project-memberships";
export * from "@/db/schema/project-membership-audit";
export * from "@/db/schema/environments";

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
export type { PublicProject } from "@/db/schema/projects";
export type {
  PublicProjectMembership,
  ProjectRole,
} from "@/db/schema/project-memberships";
export type { PublicProjectMembershipAudit } from "@/db/schema/project-membership-audit";
export type { PublicEnvironment, NewEnvironment } from "@/db/schema/environments";

import { users } from "@/db/schema/users";
import { sessions } from "@/db/schema/sessions";
import { organizations } from "@/db/schema/organizations";
import { organizationMemberships } from "@/db/schema/organization-memberships";
import { organizationMembershipAudit } from "@/db/schema/organization-membership-audit";
import { projects } from "@/db/schema/projects";
import { projectMemberships } from "@/db/schema/project-memberships";
import { projectMembershipAudit } from "@/db/schema/project-membership-audit";
import { environments } from "@/db/schema/environments";

export type DatabaseTable =
  | typeof users
  | typeof sessions
  | typeof organizations
  | typeof organizationMemberships
  | typeof organizationMembershipAudit
  | typeof projects
  | typeof projectMemberships
  | typeof projectMembershipAudit
  | typeof environments;
