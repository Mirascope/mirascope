import { HttpApiBuilder } from "@effect/platform";
import { Layer } from "effect";
import { checkHealthHandler } from "@/api/health.handlers";
import { createTraceHandler } from "@/api/traces.handlers";
import { getOpenApiSpecHandler } from "@/api/docs.handlers";
import {
  listOrganizationsHandler,
  createOrganizationHandler,
  getOrganizationHandler,
  updateOrganizationHandler,
  deleteOrganizationHandler,
} from "@/api/organizations.handlers";
import {
  listProjectsHandler,
  createProjectHandler,
  getProjectHandler,
  updateProjectHandler,
  deleteProjectHandler,
} from "@/api/projects.handlers";
import { MirascopeCloudApi } from "@/api/api";

export { MirascopeCloudApi };

const HealthHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "health",
  (handlers) => handlers.handle("check", () => checkHealthHandler),
);

const TracesHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "traces",
  (handlers) =>
    handlers.handle("create", ({ payload }) => createTraceHandler(payload)),
);

const DocsHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "docs",
  (handlers) => handlers.handle("openapi", () => getOpenApiSpecHandler),
);

const OrganizationsHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "organizations",
  (handlers) =>
    handlers
      .handle("list", () => listOrganizationsHandler)
      .handle("create", ({ payload }) => createOrganizationHandler(payload))
      .handle("get", ({ path }) => getOrganizationHandler(path.id))
      .handle("update", ({ path, payload }) =>
        updateOrganizationHandler(path.id, payload),
      )
      .handle("delete", ({ path }) => deleteOrganizationHandler(path.id)),
);

const ProjectsHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "projects",
  (handlers) =>
    handlers
      .handle("list", () => listProjectsHandler())
      .handle("create", ({ payload }) => createProjectHandler(payload))
      .handle("get", ({ path }) => getProjectHandler(path.projectId))
      .handle("update", ({ path, payload }) =>
        updateProjectHandler(path.projectId, payload),
      )
      .handle("delete", ({ path }) => deleteProjectHandler(path.projectId)),
);

export const ApiLive = HttpApiBuilder.api(MirascopeCloudApi).pipe(
  Layer.provide(HealthHandlersLive),
  Layer.provide(TracesHandlersLive),
  Layer.provide(DocsHandlersLive),
  Layer.provide(OrganizationsHandlersLive),
  Layer.provide(ProjectsHandlersLive),
);
