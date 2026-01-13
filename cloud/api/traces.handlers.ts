import { Effect } from "effect";
import { Database } from "@/db";
import { Authentication } from "@/auth";
import type {
  CreateTraceRequest,
  CreateTraceResponse,
  ListByFunctionHashResponse,
} from "@/api/traces.schemas";
import type { PublicTrace } from "@/db/traces";
import { ClickHouseSearch } from "@/db/clickhouse/search";

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
export const toTrace = (trace: PublicTrace) => ({
  ...trace,
  createdAt: trace.createdAt?.toISOString() ?? null,
});

/**
 * Handler for listing traces by function hash.
 * Finds the function by hash, then searches for traces with that function.
 */
export const listByFunctionHashHandler = (
  hash: string,
  params: { limit?: number; offset?: number },
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const { user, apiKeyInfo } = yield* Authentication.ApiKey;
    const clickHouseSearch = yield* ClickHouseSearch;

    // First, find the function by hash
    const fn =
      yield* db.organizations.projects.environments.functions.findByHash({
        userId: user.id,
        organizationId: apiKeyInfo.organizationId,
        projectId: apiKeyInfo.projectId,
        environmentId: apiKeyInfo.environmentId,
        hash,
      });

    // Search for spans with this function ID
    /* v8 ignore start - Default parameter values */
    const limit = params.limit ?? 100;
    const offset = params.offset ?? 0;
    /* v8 ignore stop */

    // Get current time range (last 30 days for search)
    const endTime = new Date();
    const startTime = new Date(endTime.getTime() - 30 * 24 * 60 * 60 * 1000);

    const searchResult = yield* clickHouseSearch.search({
      environmentId: apiKeyInfo.environmentId,
      startTime,
      endTime,
      functionId: fn.id,
      limit,
      offset,
    });

    // Extract unique traces from search results
    const uniqueTraces = new Map<
      string,
      {
        id: string;
        otelTraceId: string;
        environmentId: string;
        projectId: string;
        organizationId: string;
        serviceName: string | null;
        serviceVersion: string | null;
        resourceAttributes: Record<string, unknown> | null;
        createdAt: string | null;
      }
    >();

    for (const span of searchResult.spans) {
      if (!uniqueTraces.has(span.traceId)) {
        uniqueTraces.set(span.traceId, {
          id: span.id,
          otelTraceId: span.traceId,
          environmentId: apiKeyInfo.environmentId,
          projectId: apiKeyInfo.projectId,
          organizationId: apiKeyInfo.organizationId,
          serviceName: null,
          serviceVersion: null,
          resourceAttributes: null,
          createdAt: span.startTime,
        });
      }
    }

    const traces = Array.from(uniqueTraces.values());

    const response: ListByFunctionHashResponse = {
      traces,
      total: searchResult.total,
    };

    return response;
  });
