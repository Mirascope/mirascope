import { HttpApi } from "@effect/platform";
import { HealthApi } from "@/api/health.schemas";
import { TracesApi } from "@/api/traces.schemas";
import { DocsApi } from "@/api/docs.schemas";
import { OrganizationsApi } from "@/api/organizations.schemas";
import { ProjectsApi } from "@/api/projects.schemas";

export * from "@/db/errors";
export * from "@/api/health.schemas";
export * from "@/api/traces.schemas";
export * from "@/api/docs.schemas";
export * from "@/api/organizations.schemas";
export * from "@/api/projects.schemas";

export class MirascopeCloudApi extends HttpApi.make("MirascopeCloudApi")
  .add(HealthApi)
  .add(TracesApi)
  .add(DocsApi)
  .add(OrganizationsApi)
  .add(ProjectsApi) {}
