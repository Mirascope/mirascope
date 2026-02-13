import { HttpApiBuilder } from "@effect/platform";
import { Effect, Layer } from "effect";

import {
  listAnnotationsHandler,
  createAnnotationHandler,
  getAnnotationHandler,
  updateAnnotationHandler,
  deleteAnnotationHandler,
} from "@/api/annotations.handlers";
import { MirascopeCloudApi } from "@/api/api";
import {
  listAllApiKeysHandler,
  listApiKeysHandler,
  createApiKeyHandler,
  getApiKeyHandler,
  deleteApiKeyHandler,
} from "@/api/api-keys.handlers";
import {
  listClawMembersHandler,
  addClawMemberHandler,
  getClawMembershipHandler,
  updateClawMemberRoleHandler,
  removeClawMemberHandler,
} from "@/api/claw-memberships.handlers";
import {
  listClawsHandler,
  createClawHandler,
  getClawHandler,
  updateClawHandler,
  deleteClawHandler,
  getClawUsageHandler,
  getSecretsHandler,
  updateSecretsHandler,
  restartClawHandler,
} from "@/api/claws.handlers";
import { getOpenApiSpecHandler } from "@/api/docs.handlers";
import {
  listEnvironmentsHandler,
  createEnvironmentHandler,
  getEnvironmentHandler,
  updateEnvironmentHandler,
  deleteEnvironmentHandler,
  getEnvironmentAnalyticsHandler,
} from "@/api/environments.handlers";
import {
  listFunctionsHandler,
  createFunctionHandler,
  getFunctionHandler,
  findByHashHandler,
  deleteFunctionHandler,
} from "@/api/functions.handlers";
import { checkHealthHandler } from "@/api/health.handlers";
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
  listOrganizationsHandler,
  createOrganizationHandler,
  createOrgSetupIntentHandler,
  getOrganizationHandler,
  updateOrganizationHandler,
  deleteOrganizationHandler,
  getOrganizationRouterBalanceHandler,
  createPaymentIntentHandler,
  getSubscriptionHandler,
  previewSubscriptionChangeHandler,
  updateSubscriptionHandler,
  cancelScheduledDowngradeHandler,
  createSetupIntentHandler,
  getPaymentMethodHandler,
  removePaymentMethodHandler,
  getAutoReloadSettingsHandler,
  updateAutoReloadSettingsHandler,
} from "@/api/organizations.handlers";
import {
  listProjectMembersHandler,
  addProjectMemberHandler,
  updateProjectMemberRoleHandler,
  removeProjectMemberHandler,
  getProjectMembershipHandler,
} from "@/api/project-memberships.handlers";
import {
  listProjectsHandler,
  createProjectHandler,
  getProjectHandler,
  updateProjectHandler,
  deleteProjectHandler,
} from "@/api/projects.handlers";
import {
  listTagsHandler,
  createTagHandler,
  getTagHandler,
  updateTagHandler,
  deleteTagHandler,
} from "@/api/tags.handlers";
import { tokenCostHandler } from "@/api/token-cost.handlers";
import {
  searchHandler,
  getTraceDetailHandler,
  getAnalyticsSummaryHandler,
} from "@/api/traces-search.handlers";
import {
  createTraceHandler,
  listByFunctionHashHandler,
} from "@/api/traces.handlers";
import { Authentication } from "@/auth";

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
      // OTEL-compatible endpoint at /api/v2/v1/traces
      .handle("createOtel", ({ payload }) => createTraceHandler(payload))
      // API key route - extracts environmentId from apiKeyInfo
      .handle("search", ({ payload }) =>
        Effect.gen(function* () {
          const { apiKeyInfo } = yield* Authentication.ApiKey;
          return yield* searchHandler(apiKeyInfo.environmentId, payload);
        }),
      )
      // Session route - extracts environmentId from path
      .handle("searchByEnv", ({ payload, path }) =>
        searchHandler(path.environmentId, payload),
      )
      // API key route - extracts environmentId from apiKeyInfo
      .handle("getTraceDetail", ({ path }) =>
        Effect.gen(function* () {
          const { apiKeyInfo } = yield* Authentication.ApiKey;
          return yield* getTraceDetailHandler(
            apiKeyInfo.environmentId,
            path.traceId,
          );
        }),
      )
      // Session route - extracts environmentId from path
      .handle("getTraceDetailByEnv", ({ path }) =>
        getTraceDetailHandler(path.environmentId, path.traceId),
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
      .handle("createOrgSetupIntent", () => createOrgSetupIntentHandler)
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
      )
      .handle("createSetupIntent", ({ path }) =>
        createSetupIntentHandler(path.id),
      )
      .handle("getPaymentMethod", ({ path }) =>
        getPaymentMethodHandler(path.id),
      )
      .handle("removePaymentMethod", ({ path }) =>
        removePaymentMethodHandler(path.id),
      )
      .handle("getAutoReloadSettings", ({ path }) =>
        getAutoReloadSettingsHandler(path.id),
      )
      .handle("updateAutoReloadSettings", ({ path, payload }) =>
        updateAutoReloadSettingsHandler(path.id, payload),
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

const ProjectMembershipsHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "project-memberships",
  (handlers) =>
    handlers
      .handle("list", ({ path }) =>
        listProjectMembersHandler(path.organizationId, path.projectId),
      )
      .handle("create", ({ path, payload }) =>
        addProjectMemberHandler(path.organizationId, path.projectId, payload),
      )
      .handle("get", ({ path }) =>
        getProjectMembershipHandler(
          path.organizationId,
          path.projectId,
          path.memberId,
        ),
      )
      .handle("update", ({ path, payload }) =>
        updateProjectMemberRoleHandler(
          path.organizationId,
          path.projectId,
          path.memberId,
          payload,
        ),
      )
      .handle("delete", ({ path }) =>
        removeProjectMemberHandler(
          path.organizationId,
          path.projectId,
          path.memberId,
        ),
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
      )
      .handle("getAnalytics", ({ path, urlParams }) =>
        getEnvironmentAnalyticsHandler(
          path.organizationId,
          path.projectId,
          path.environmentId,
          urlParams,
        ),
      ),
);

const ApiKeysHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "apiKeys",
  (handlers) =>
    handlers
      .handle("listAllForOrg", ({ path }) =>
        listAllApiKeysHandler(path.organizationId),
      )
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
      // API key route - extracts IDs from apiKeyInfo
      .handle("list", () =>
        Effect.gen(function* () {
          const { apiKeyInfo } = yield* Authentication.ApiKey;
          return yield* listFunctionsHandler(
            apiKeyInfo.organizationId,
            apiKeyInfo.projectId,
            apiKeyInfo.environmentId,
          );
        }),
      )
      .handle("create", ({ payload }) => createFunctionHandler(payload))
      // API key route - extracts IDs from apiKeyInfo
      .handle("get", ({ path }) =>
        Effect.gen(function* () {
          const { apiKeyInfo } = yield* Authentication.ApiKey;
          return yield* getFunctionHandler(
            apiKeyInfo.organizationId,
            apiKeyInfo.projectId,
            apiKeyInfo.environmentId,
            path.id,
          );
        }),
      )
      // API key route - extracts IDs from apiKeyInfo
      .handle("delete", ({ path }) =>
        Effect.gen(function* () {
          const { apiKeyInfo } = yield* Authentication.ApiKey;
          return yield* deleteFunctionHandler(
            apiKeyInfo.organizationId,
            apiKeyInfo.projectId,
            apiKeyInfo.environmentId,
            path.id,
          );
        }),
      )
      // API key route - extracts IDs from apiKeyInfo
      .handle("findByHash", ({ path }) =>
        Effect.gen(function* () {
          const { apiKeyInfo } = yield* Authentication.ApiKey;
          return yield* findByHashHandler(
            apiKeyInfo.organizationId,
            apiKeyInfo.projectId,
            apiKeyInfo.environmentId,
            path.hash,
          );
        }),
      )
      // Session route - extracts IDs from path
      .handle("getByEnv", ({ path }) =>
        getFunctionHandler(
          path.organizationId,
          path.projectId,
          path.environmentId,
          path.functionId,
        ),
      )
      // Session route - list all functions in an environment
      .handle("listByEnv", ({ path }) =>
        listFunctionsHandler(
          path.organizationId,
          path.projectId,
          path.environmentId,
        ),
      ),
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

const TagsHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "tags",
  (handlers) =>
    handlers
      .handle("list", ({ path }) =>
        listTagsHandler(path.organizationId, path.projectId),
      )
      .handle("create", ({ path, payload }) =>
        createTagHandler(path.organizationId, path.projectId, payload),
      )
      .handle("get", ({ path }) =>
        getTagHandler(path.organizationId, path.projectId, path.tagId),
      )
      .handle("update", ({ path, payload }) =>
        updateTagHandler(
          path.organizationId,
          path.projectId,
          path.tagId,
          payload,
        ),
      )
      .handle("delete", ({ path }) =>
        deleteTagHandler(path.organizationId, path.projectId, path.tagId),
      ),
);

const ClawsHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "claws",
  (handlers) =>
    handlers
      .handle("list", ({ path }) => listClawsHandler(path.organizationId))
      .handle("create", ({ path, payload }) =>
        createClawHandler(path.organizationId, payload),
      )
      .handle("get", ({ path }) =>
        getClawHandler(path.organizationId, path.clawId),
      )
      .handle("update", ({ path, payload }) =>
        updateClawHandler(path.organizationId, path.clawId, payload),
      )
      .handle("delete", ({ path }) =>
        deleteClawHandler(path.organizationId, path.clawId),
      )
      .handle("getUsage", ({ path }) =>
        getClawUsageHandler(path.organizationId, path.clawId),
      )
      .handle("getSecrets", ({ path }) =>
        getSecretsHandler(path.organizationId, path.clawId),
      )
      .handle("updateSecrets", ({ path, payload }) =>
        updateSecretsHandler(path.organizationId, path.clawId, payload),
      )
      .handle("restart", ({ path }) =>
        restartClawHandler(path.organizationId, path.clawId),
      ),
);

const ClawMembershipsHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "claw-memberships",
  (handlers) =>
    handlers
      .handle("list", ({ path }) =>
        listClawMembersHandler(path.organizationId, path.clawId),
      )
      .handle("create", ({ path, payload }) =>
        addClawMemberHandler(path.organizationId, path.clawId, payload),
      )
      .handle("get", ({ path }) =>
        getClawMembershipHandler(
          path.organizationId,
          path.clawId,
          path.memberId,
        ),
      )
      .handle("update", ({ path, payload }) =>
        updateClawMemberRoleHandler(
          path.organizationId,
          path.clawId,
          path.memberId,
          payload,
        ),
      )
      .handle("delete", ({ path }) =>
        removeClawMemberHandler(
          path.organizationId,
          path.clawId,
          path.memberId,
        ),
      ),
);

const TokenCostHandlersLive = HttpApiBuilder.group(
  MirascopeCloudApi,
  "token-cost",
  (handlers) =>
    handlers.handle("calculate", ({ payload }) =>
      Effect.gen(function* () {
        // Require API key authentication
        yield* Authentication.ApiKey;
        return yield* tokenCostHandler(payload);
      }),
    ),
);

export const ApiLive = HttpApiBuilder.api(MirascopeCloudApi).pipe(
  Layer.provide(HealthHandlersLive),
  Layer.provide(TracesHandlersLive),
  Layer.provide(DocsHandlersLive),
  Layer.provide(OrganizationsHandlersLive),
  Layer.provide(OrganizationInvitationsHandlersLive),
  Layer.provide(OrganizationMembershipsHandlersLive),
  Layer.provide(ProjectsHandlersLive),
  Layer.provide(ProjectMembershipsHandlersLive),
  Layer.provide(EnvironmentsHandlersLive),
  Layer.provide(ApiKeysHandlersLive),
  Layer.provide(FunctionsHandlersLive),
  Layer.provide(AnnotationsHandlersLive),
  Layer.provide(ClawsHandlersLive),
  Layer.provide(ClawMembershipsHandlersLive),
  Layer.provide(TagsHandlersLive),
  Layer.provide(TokenCostHandlersLive),
);
