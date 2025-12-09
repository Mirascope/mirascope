import { HttpApi } from "@effect/platform";
import { HealthApi } from "@/api/health.schemas";
import { TracesApi } from "@/api/traces.schemas";
import { DocsApi } from "@/api/docs.schemas";

export * from "@/api/health.schemas";
export * from "@/api/traces.schemas";
export * from "@/api/docs.schemas";

export class MirascopeCloudApi extends HttpApi.make("MirascopeCloudApi")
  .add(HealthApi)
  .add(TracesApi)
  .add(DocsApi) {}
