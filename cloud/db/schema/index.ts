export * from "@/db/schema/sessions";
export * from "@/db/schema/users";
export * from "@/db/schema/organizations";
export * from "@/db/schema/organization-memberships";
export * from "@/db/schema/project-memberships";
export * from "@/db/schema/projects";
export * from "@/db/schema/environments";
export * from "@/db/schema/api-keys";

export type { PublicSession } from "@/db/schema/sessions";
export type { PublicUser } from "@/db/schema/users";
export type { PublicOrganization } from "@/db/schema/organizations";
export type {
  PublicOrganizationMembership,
  PublicOrganizationWithMembership,
  Role,
} from "@/db/schema/organization-memberships";
export type { PublicProjectMembership } from "@/db/schema/project-memberships";
export type { PublicProject } from "@/db/schema/projects";
export type { PublicEnvironment, NewEnvironment } from "@/db/schema/environments";
export type { PublicApiKey, ApiKeyCreateResponse } from "@/db/schema/api-keys";

import { users } from "@/db/schema/users";
import { sessions } from "@/db/schema/sessions";
import { organizations } from "@/db/schema/organizations";
import { organizationMemberships } from "@/db/schema/organization-memberships";
import { projectMemberships } from "@/db/schema/project-memberships";
import { projects } from "@/db/schema/projects";
import { environments } from "@/db/schema/environments";
import { apiKeys } from "@/db/schema/api-keys";

export type DatabaseTable =
  | typeof users
  | typeof sessions
  | typeof organizations
  | typeof organizationMemberships
  | typeof projectMemberships
  | typeof projects
  | typeof environments
  | typeof apiKeys;
