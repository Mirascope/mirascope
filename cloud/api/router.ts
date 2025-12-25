import { HttpApiBuilder } from "@effect/platform";
import { Layer } from "effect";
import { checkHealthHandler } from "@/api/health.handlers";
import { createTraceHandler, sdkCreateTraceHandler } from "@/api/traces.handlers";
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
  updateEnvironmentHandler,
  deleteEnvironmentHandler,
} from "@/api/environments.handlers";
import {
  listApiKeysHandler,
  createApiKeyHandler,
  getApiKeyHandler,
  deleteApiKeyHandler,
} from "@/api/api-keys.handlers";
import {
  registerFunctionHandler,
  getFunctionHandler,
  getFunctionByHashHandler,
  listFunctionsHandler,
  sdkRegisterFunctionHandler,
  sdkGetFunctionHandler,
  sdkGetFunctionByHashHandler,
  sdkListFunctionsHandler,
} from "@/api/functions.handlers";
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
    handlers.handle("create", ({ path, payload }) =>
      createTraceHandler(
        path.organizationId,
        path.projectId,
        path.environmentId,
        payload,
      ),
    ),
);

const SdkTracesHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "sdkTraces",
  (handlers) =>
    handlers.handle("create", ({ payload }) => sdkCreateTraceHandler(payload)),
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
      .handle("list", ({ path }) => listProjectsHandler(path.organizationId))
      .handle("create", ({ path, payload }) =>
        createProjectHandler(path.organizationId, payload),
      )
      .handle("get", ({ path }) =>
        getProjectHandler(path.organizationId, path.projectId),
      )
      .handle("update", ({ path, payload }) =>
        updateProjectHandler(path.organizationId, path.projectId, payload),
      )
      .handle("delete", ({ path }) =>
        deleteProjectHandler(path.organizationId, path.projectId),
      ),
);

const EnvironmentsHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "environments",
  (handlers) =>
    handlers
      .handle("list", ({ path }) =>
        listEnvironmentsHandler(path.organizationId, path.projectId),
      )
      .handle("create", ({ path, payload }) =>
        createEnvironmentHandler(path.organizationId, path.projectId, payload),
      )
      .handle("get", ({ path }) =>
        getEnvironmentHandler(
          path.organizationId,
          path.projectId,
          path.environmentId,
        ),
      )
      .handle("update", ({ path, payload }) =>
        updateEnvironmentHandler(
          path.organizationId,
          path.projectId,
          path.environmentId,
          payload,
        ),
      )
      .handle("delete", ({ path }) =>
        deleteEnvironmentHandler(
          path.organizationId,
          path.projectId,
          path.environmentId,
        ),
      ),
);

const ApiKeysHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "apiKeys",
  (handlers) =>
    handlers
      .handle("list", ({ path }) =>
        listApiKeysHandler(
          path.organizationId,
          path.projectId,
          path.environmentId,
        ),
      )
      .handle("create", ({ path, payload }) =>
        createApiKeyHandler(
          path.organizationId,
          path.projectId,
          path.environmentId,
          payload,
        ),
      )
      .handle("get", ({ path }) =>
        getApiKeyHandler(
          path.organizationId,
          path.projectId,
          path.environmentId,
          path.apiKeyId,
        ),
      )
      .handle("delete", ({ path }) =>
        deleteApiKeyHandler(
          path.organizationId,
          path.projectId,
          path.environmentId,
          path.apiKeyId,
        ),
      ),
);

<<<<<<< HEAD
=======
const FunctionsHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "functions",
  (handlers) =>
    handlers
      .handle("register", ({ path, payload }) =>
        registerFunctionHandler(
          path.organizationId,
          path.projectId,
          path.environmentId,
          payload,
        ),
      )
      .handle("get", ({ path }) =>
        getFunctionHandler(
          path.organizationId,
          path.projectId,
          path.environmentId,
          path.id,
        ),
      )
      .handle("getByHash", ({ path }) =>
        getFunctionByHashHandler(
          path.organizationId,
          path.projectId,
          path.environmentId,
          path.hash,
        ),
      )
      .handle("list", ({ path, urlParams }) =>
        listFunctionsHandler(
          path.organizationId,
          path.projectId,
          path.environmentId,
          urlParams,
        ),
      ),
);

const SdkFunctionsHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "sdkFunctions",
  (handlers) =>
    handlers
      .handle("register", ({ payload }) => sdkRegisterFunctionHandler(payload))
      .handle("get", ({ path }) => sdkGetFunctionHandler(path.id))
      .handle("getByHash", ({ path }) => sdkGetFunctionByHashHandler(path.hash))
      .handle("list", ({ urlParams }) => sdkListFunctionsHandler(urlParams)),
);

>>>>>>> 0edae451b (feat(api): add SDK functions flat endpoint with tests)
export const ApiLive = HttpApiBuilder.api(MirascopeCloudApi).pipe(
  Layer.provide(HealthHandlersLive),
  Layer.provide(TracesHandlersLive),
  Layer.provide(SdkTracesHandlersLive),
  Layer.provide(DocsHandlersLive),
  Layer.provide(OrganizationsHandlersLive),
  Layer.provide(ProjectsHandlersLive),
  Layer.provide(EnvironmentsHandlersLive),
  Layer.provide(ApiKeysHandlersLive),
<<<<<<< HEAD
=======
  Layer.provide(FunctionsHandlersLive),
  Layer.provide(SdkFunctionsHandlersLive),
>>>>>>> 0edae451b (feat(api): add SDK functions flat endpoint with tests)
);