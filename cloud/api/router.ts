import { HttpApiBuilder } from "@effect/platform";
import { Layer } from "effect";
import { checkHealthHandler } from "@/api/health.handlers";
import {
  createTraceHandler,
  listByFunctionHashHandler,
} from "@/api/traces.handlers";
import { getOpenApiSpecHandler } from "@/api/docs.handlers";
import {
  listOrganizationsHandler,
  createOrganizationHandler,
  getOrganizationHandler,
  updateOrganizationHandler,
  deleteOrganizationHandler,
  getOrganizationRouterBalanceHandler,
  createPaymentIntentHandler,
  getSubscriptionHandler,
  previewSubscriptionChangeHandler,
  updateSubscriptionHandler,
  cancelScheduledDowngradeHandler,
} from "@/api/organizations.handlers";
import {
  listInvitationsHandler,
  createInvitationHandler,
  getInvitationHandler,
  resendInvitationHandler,
  revokeInvitationHandler,
  acceptInvitationHandler,
} from "@/api/organization-invitations.handlers";
import {
  listMembersHandler,
  updateMemberRoleHandler,
  removeMemberHandler,
} from "@/api/organization-memberships.handlers";
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
  listFunctionsHandler,
  createFunctionHandler,
  getFunctionHandler,
  findByHashHandler,
  deleteFunctionHandler,
} from "@/api/functions.handlers";
import {
  listAnnotationsHandler,
  createAnnotationHandler,
  getAnnotationHandler,
  updateAnnotationHandler,
  deleteAnnotationHandler,
} from "@/api/annotations.handlers";
import {
  searchHandler,
  getTraceDetailHandler,
  getAnalyticsSummaryHandler,
} from "@/api/traces-search.handlers";
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
    handlers
      .handle("create", ({ payload }) => createTraceHandler(payload))
      .handle("search", ({ payload }) => searchHandler(payload))
      .handle("getTraceDetail", ({ path }) =>
        getTraceDetailHandler(path.traceId),
      )
      .handle("getAnalyticsSummary", ({ urlParams }) =>
        getAnalyticsSummaryHandler(urlParams),
      )
      .handle("listByFunctionHash", ({ path, urlParams }) =>
        listByFunctionHashHandler(path.hash, urlParams),
      ),
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
      .handle("delete", ({ path }) => deleteOrganizationHandler(path.id))
      .handle("routerBalance", ({ path }) =>
        getOrganizationRouterBalanceHandler(path.id),
      )
      .handle("createPaymentIntent", ({ path, payload }) =>
        createPaymentIntentHandler(path.id, payload),
      )
      .handle("subscription", ({ path }) => getSubscriptionHandler(path.id))
      .handle("previewSubscriptionChange", ({ path, payload }) =>
        previewSubscriptionChangeHandler(path.id, payload),
      )
      .handle("updateSubscription", ({ path, payload }) =>
        updateSubscriptionHandler(path.id, payload),
      )
      .handle("cancelScheduledDowngrade", ({ path }) =>
        cancelScheduledDowngradeHandler(path.id),
      ),
);

const OrganizationInvitationsHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "organization-invitations",
  (handlers) =>
    handlers
      .handle("list", ({ path }) => listInvitationsHandler(path.organizationId))
      .handle("create", ({ path, payload }) =>
        createInvitationHandler(path.organizationId, payload),
      )
      .handle("get", ({ path }) =>
        getInvitationHandler(path.organizationId, path.invitationId),
      )
      .handle("resend", ({ path }) =>
        resendInvitationHandler(path.organizationId, path.invitationId),
      )
      .handle("revoke", ({ path }) =>
        revokeInvitationHandler(path.organizationId, path.invitationId),
      )
      .handle("accept", ({ payload }) => acceptInvitationHandler(payload)),
);

const OrganizationMembershipsHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "organization-memberships",
  (handlers) =>
    handlers
      .handle("list", ({ path }) => listMembersHandler(path.organizationId))
      .handle("update", ({ path, payload }) =>
        updateMemberRoleHandler(path.organizationId, path.memberId, payload),
      )
      .handle("delete", ({ path }) =>
        removeMemberHandler(path.organizationId, path.memberId),
      ),
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

const FunctionsHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "functions",
  (handlers) =>
    handlers
      .handle("list", () => listFunctionsHandler())
      .handle("create", ({ payload }) => createFunctionHandler(payload))
      .handle("get", ({ path }) => getFunctionHandler(path.id))
      .handle("delete", ({ path }) => deleteFunctionHandler(path.id))
      .handle("findByHash", ({ path }) => findByHashHandler(path.hash)),
);

const AnnotationsHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "annotations",
  (handlers) =>
    handlers
      .handle("list", ({ urlParams }) => listAnnotationsHandler(urlParams))
      .handle("create", ({ payload }) => createAnnotationHandler(payload))
      .handle("get", ({ path }) => getAnnotationHandler(path.id))
      .handle("update", ({ path, payload }) =>
        updateAnnotationHandler(path.id, payload),
      )
      .handle("delete", ({ path }) => deleteAnnotationHandler(path.id)),
);

export const ApiLive = HttpApiBuilder.api(MirascopeCloudApi).pipe(
  Layer.provide(HealthHandlersLive),
  Layer.provide(TracesHandlersLive),
  Layer.provide(DocsHandlersLive),
  Layer.provide(OrganizationsHandlersLive),
  Layer.provide(OrganizationInvitationsHandlersLive),
  Layer.provide(OrganizationMembershipsHandlersLive),
  Layer.provide(ProjectsHandlersLive),
  Layer.provide(EnvironmentsHandlersLive),
  Layer.provide(ApiKeysHandlersLive),
  Layer.provide(FunctionsHandlersLive),
  Layer.provide(AnnotationsHandlersLive),
);
