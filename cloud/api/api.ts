import { HttpApi } from "@effect/platform";

import { AnnotationsApi } from "@/api/annotations.schemas";
import { ApiKeysApi } from "@/api/api-keys.schemas";
import { ClawsApi } from "@/api/claws.schemas";
import { DocsApi } from "@/api/docs.schemas";
import { EnvironmentsApi } from "@/api/environments.schemas";
import { FunctionsApi } from "@/api/functions.schemas";
import { HealthApi } from "@/api/health.schemas";
import { OrganizationInvitationsApi } from "@/api/organization-invitations.schemas";
import { OrganizationMembershipsApi } from "@/api/organization-memberships.schemas";
import { OrganizationsApi } from "@/api/organizations.schemas";
import { ProjectMembershipsApi } from "@/api/project-memberships.schemas";
import { ProjectsApi } from "@/api/projects.schemas";
import { TagsApi } from "@/api/tags.schemas";
import { TokenCostApi } from "@/api/token-cost.schemas";
import { TracesApi } from "@/api/traces.schemas";
import { RateLimitError, ServiceUnavailableError } from "@/errors";

export * from "@/errors";
export * from "@/api/health.schemas";
export * from "@/api/traces.schemas";
export * from "@/api/docs.schemas";
export * from "@/api/organizations.schemas";
export * from "@/api/organization-invitations.schemas";
export * from "@/api/organization-memberships.schemas";
export * from "@/api/projects.schemas";
export * from "@/api/project-memberships.schemas";
export * from "@/api/environments.schemas";
export * from "@/api/api-keys.schemas";
export * from "@/api/functions.schemas";
export * from "@/api/annotations.schemas";
export * from "@/api/claws.schemas";
export * from "@/api/tags.schemas";
export * from "@/api/token-cost.schemas";
export * from "@/api/traces-search.schemas";

export class MirascopeCloudApi extends HttpApi.make("MirascopeCloudApi")
  .add(HealthApi)
  .add(TracesApi)
  .add(DocsApi)
  .add(OrganizationsApi)
  .add(OrganizationInvitationsApi)
  .add(OrganizationMembershipsApi)
  .add(ProjectsApi)
  .add(ProjectMembershipsApi)
  .add(EnvironmentsApi)
  .add(ApiKeysApi)
  .add(FunctionsApi)
  .add(AnnotationsApi)
  .add(ClawsApi)
  .add(TagsApi)
  .add(TokenCostApi)
  .addError(RateLimitError, { status: RateLimitError.status })
  .addError(ServiceUnavailableError, {
    status: ServiceUnavailableError.status,
  }) {}
