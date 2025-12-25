import { HttpApi } from "@effect/platform";
import { HealthApi } from "@/api/health.schemas";
import { TracesApi } from "@/api/traces.schemas";
import { SdkTracesApi } from "@/api/sdk.schemas";
import { DocsApi } from "@/api/docs.schemas";
import { OrganizationsApi } from "@/api/organizations.schemas";
import { ProjectsApi } from "@/api/projects.schemas";
import { EnvironmentsApi } from "@/api/environments.schemas";
import { ApiKeysApi } from "@/api/api-keys.schemas";

export * from "@/errors";
export * from "@/api/health.schemas";
export * from "@/api/traces.schemas";
export * from "@/api/sdk.schemas";
export * from "@/api/docs.schemas";
export * from "@/api/organizations.schemas";
export * from "@/api/projects.schemas";
export * from "@/api/environments.schemas";
export * from "@/api/api-keys.schemas";

export class MirascopeCloudApi extends HttpApi.make("MirascopeCloudApi")
  .add(HealthApi)
  .add(TracesApi)
  .add(SdkTracesApi)
  .add(DocsApi)
  .add(OrganizationsApi)
  .add(ProjectsApi)
  .add(EnvironmentsApi)
  .add(ApiKeysApi) {}
