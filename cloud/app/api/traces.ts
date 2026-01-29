import { useQuery, keepPreviousData } from "@tanstack/react-query";
import { Effect } from "effect";

import type { SearchRequest } from "@/api/traces-search.schemas";

import { ApiClient, eq } from "@/app/api/client";

export const useTracesSearch = (
  organizationId: string | null,
  projectId: string | null,
  environmentId: string | null,
  params: SearchRequest,
  enabled = true,
) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: [
        "traces",
        "search",
        organizationId,
        projectId,
        environmentId,
        params,
      ],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.traces.searchByEnv({
            path: {
              organizationId: organizationId!,
              projectId: projectId!,
              environmentId: environmentId!,
            },
            payload: params,
          });
        }),
    }),
    // Keep showing previous data while fetching new data (prevents flash on refresh)
    placeholderData: keepPreviousData,
    enabled: enabled && !!organizationId && !!projectId && !!environmentId,
  });
};

export const useTraceDetail = (
  organizationId: string | null,
  projectId: string | null,
  environmentId: string | null,
  traceId: string | null,
) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: ["traces", organizationId, projectId, environmentId, traceId],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.traces.getTraceDetailByEnv({
            path: {
              organizationId: organizationId!,
              projectId: projectId!,
              environmentId: environmentId!,
              traceId: traceId!,
            },
          });
        }),
    }),
    enabled: !!organizationId && !!projectId && !!environmentId && !!traceId,
  });
};
