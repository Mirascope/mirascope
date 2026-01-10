import { Effect } from "effect";
import { Database } from "@/db";
import { Authentication } from "@/auth";
import type {
  CreateTraceRequest,
  CreateTraceResponse,
  ListByFunctionHashResponse,
} from "@/api/traces.schemas";
import type { PublicTrace } from "@/db/traces";

export * from "@/api/traces.schemas";

/**
 * Handler for creating traces from OTLP trace data.
 * Accepts OpenTelemetry trace data and stores it in the database.
 */
export const createTraceHandler = (payload: CreateTraceRequest) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const { user, apiKeyInfo } = yield* Authentication.ApiKey;

    const result = yield* db.organizations.projects.environments.traces.create({
      userId: user.id,
      organizationId: apiKeyInfo.organizationId,
      projectId: apiKeyInfo.projectId,
      environmentId: apiKeyInfo.environmentId,
      data: { resourceSpans: payload.resourceSpans },
    });

    const response: CreateTraceResponse = {
      partialSuccess:
        result.rejectedSpans > 0
          ? {
              rejectedSpans: result.rejectedSpans,
              errorMessage: `${result.rejectedSpans} spans were rejected due to errors`,
            }
          : {},
    };

    return response;
  });

// Convert Date to ISO string for API response
const toTrace = (trace: PublicTrace) => ({
  ...trace,
  createdAt: trace.createdAt?.toISOString() ?? null,
});

/**
 * Handler for listing traces by function version hash.
 * Queries traces containing spans with the specified mirascope.version.hash attribute.
 */
export const listByFunctionHashHandler = (
  hash: string,
  params: { limit?: number; offset?: number },
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const { user, apiKeyInfo } = yield* Authentication.ApiKey;

    const { traces, total } =
      yield* db.organizations.projects.environments.traces.findByFunctionHash({
        userId: user.id,
        organizationId: apiKeyInfo.organizationId,
        projectId: apiKeyInfo.projectId,
        environmentId: apiKeyInfo.environmentId,
        functionHash: hash,
        limit: params.limit ?? 100,
        offset: params.offset ?? 0,
      });

    const response: ListByFunctionHashResponse = {
      traces: traces.map(toTrace),
      total,
    };

    return response;
  });
