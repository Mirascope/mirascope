import { useQuery, keepPreviousData } from "@tanstack/react-query";
import { Effect } from "effect";

import { ApiClient, eq } from "@/app/api/client";

export const useFunctionsList = (
  organizationId: string | null,
  projectId: string | null,
  environmentId: string | null,
) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: ["functions", "list", organizationId, projectId, environmentId],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.functions.listByEnv({
            path: {
              organizationId: organizationId!,
              projectId: projectId!,
              environmentId: environmentId!,
            },
          });
        }),
    }),
    placeholderData: keepPreviousData,
    enabled: !!organizationId && !!projectId && !!environmentId,
  });
};

export const useFunctionDetail = (
  organizationId: string | null,
  projectId: string | null,
  environmentId: string | null,
  functionId: string | null,
) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: [
        "functions",
        organizationId,
        projectId,
        environmentId,
        functionId,
      ],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.functions.getByEnv({
            path: {
              organizationId: organizationId!,
              projectId: projectId!,
              environmentId: environmentId!,
              functionId: functionId!,
            },
          });
        }),
    }),
    enabled: !!organizationId && !!projectId && !!environmentId && !!functionId,
  });
};
