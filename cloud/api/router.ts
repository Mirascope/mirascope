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
import {
  listEnvironmentsHandler,
  createEnvironmentHandler,
  getEnvironmentHandler,
  deleteEnvironmentHandler,
} from "@/api/environments.handlers";
import {
  listApiKeysHandler,
  createApiKeyHandler,
  getApiKeyHandler,
  deleteApiKeyHandler,
} from "@/api/api-keys.handlers";
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

const EnvironmentsHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "environments",
  (handlers) =>
    handlers
      .handle("list", ({ path }) => listEnvironmentsHandler(path.projectId))
      .handle("create", ({ path, payload }) =>
        createEnvironmentHandler(path.projectId, payload),
      )
      .handle("get", ({ path }) => getEnvironmentHandler(path.environmentId))
      .handle("delete", ({ path }) =>
        deleteEnvironmentHandler(path.environmentId),
      ),
);

const ApiKeysHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "apiKeys",
  (handlers) =>
    handlers
      .handle("list", ({ path }) => listApiKeysHandler(path.environmentId))
      .handle("create", ({ path, payload }) =>
        createApiKeyHandler(path.environmentId, payload),
      )
      .handle("get", ({ path }) => getApiKeyHandler(path.apiKeyId))
      .handle("delete", ({ path }) => deleteApiKeyHandler(path.apiKeyId)),
);

export const ApiLive = HttpApiBuilder.api(MirascopeCloudApi).pipe(
  Layer.provide(HealthHandlersLive),
  Layer.provide(TracesHandlersLive),
  Layer.provide(DocsHandlersLive),
  Layer.provide(OrganizationsHandlersLive),
  Layer.provide(ProjectsHandlersLive),
  Layer.provide(EnvironmentsHandlersLive),
  Layer.provide(ApiKeysHandlersLive),
);
