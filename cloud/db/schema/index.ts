export * from "@/db/schema/sessions";
export * from "@/db/schema/users";
export * from "@/db/schema/organizations";
export * from "@/db/schema/organization-memberships";
export * from "@/db/schema/organization-membership-audit";
export * from "@/db/schema/projects";
export * from "@/db/schema/project-memberships";
export * from "@/db/schema/project-membership-audit";
export * from "@/db/schema/environments";
export * from "@/db/schema/api-keys";
export * from "@/db/schema/functions";
export * from "@/db/schema/annotations";
export * from "@/db/schema/traces";
export * from "@/db/schema/spans";
export * from "@/db/schema/router-requests";
export * from "@/db/schema/credit-reservations";
export * from "@/db/schema/spansOutbox";

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
export type {
  PublicEnvironment,
  NewEnvironment,
} from "@/db/schema/environments";
export type { PublicApiKey, ApiKeyCreateResponse } from "@/db/schema/api-keys";
export type { PublicFunction } from "@/db/schema/functions";
export type { PublicAnnotation } from "@/db/schema/annotations";
export type { PublicTrace } from "@/db/schema/traces";
export type { PublicSpan } from "@/db/schema/spans";
export type {
  RouterRequest,
  NewRouterRequest,
  RequestStatus,
} from "@/db/schema/router-requests";
export type {
  CreditReservation,
  NewCreditReservation,
  ReservationStatus,
} from "@/db/schema/credit-reservations";
export type { PublicSpansOutbox } from "@/db/schema/spansOutbox";

import { users } from "@/db/schema/users";
import { sessions } from "@/db/schema/sessions";
import { organizations } from "@/db/schema/organizations";
import { organizationMemberships } from "@/db/schema/organization-memberships";
import { organizationMembershipAudit } from "@/db/schema/organization-membership-audit";
import { projects } from "@/db/schema/projects";
import { projectMemberships } from "@/db/schema/project-memberships";
import { projectMembershipAudit } from "@/db/schema/project-membership-audit";
import { environments } from "@/db/schema/environments";
import { apiKeys } from "@/db/schema/api-keys";
import { functions } from "@/db/schema/functions";
import { annotations } from "@/db/schema/annotations";
import { traces } from "@/db/schema/traces";
import { spans } from "@/db/schema/spans";
import { routerRequests } from "@/db/schema/router-requests";
import { creditReservations } from "@/db/schema/credit-reservations";
import { spansOutbox } from "@/db/schema/spansOutbox";

export type DatabaseTable =
  | typeof users
  | typeof sessions
  | typeof organizations
  | typeof organizationMemberships
  | typeof organizationMembershipAudit
  | typeof projects
  | typeof projectMemberships
  | typeof projectMembershipAudit
  | typeof environments
  | typeof apiKeys
  | typeof functions
  | typeof annotations
  | typeof traces
  | typeof spans
  | typeof routerRequests
  | typeof routerRequests
  | typeof creditReservations
  | typeof spansOutbox;
