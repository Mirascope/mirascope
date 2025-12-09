import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Effect } from "effect";
import { ApiClient, eq } from "@/src/api/client";
import type { CreateEnvironmentRequest } from "@/api/environments.schemas";

export const useEnvironments = (
  organizationId: string | null,
  projectId: string | null,
) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: ["environments", organizationId, projectId],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.environments.list({
            path: { organizationId: organizationId!, projectId: projectId! },
          });
        }),
    }),
    enabled: !!organizationId && !!projectId,
  });
};

export const useEnvironment = (
  organizationId: string,
  projectId: string,
  environmentId: string,
) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: ["environments", organizationId, projectId, environmentId],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.environments.get({
            path: { organizationId, projectId, environmentId },
          });
        }),
    }),
    enabled: !!organizationId && !!projectId && !!environmentId,
  });
};

export const useCreateEnvironment = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["environments", "create"],
      mutationFn: ({
        organizationId,
        projectId,
        data,
      }: {
        organizationId: string;
        projectId: string;
        data: CreateEnvironmentRequest;
      }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.environments.create({
            path: { organizationId, projectId },
            payload: data,
          });
        }),
    }),
    onSuccess: (_, { organizationId, projectId }) => {
      void queryClient.invalidateQueries({
        queryKey: ["environments", organizationId, projectId],
      });
    },
  });
};

export const useDeleteEnvironment = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["environments", "delete"],
      mutationFn: ({
        organizationId,
        projectId,
        environmentId,
      }: {
        organizationId: string;
        projectId: string;
        environmentId: string;
      }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.environments.delete({
            path: { organizationId, projectId, environmentId },
          });
        }),
    }),
    onSuccess: (_, { organizationId, projectId }) => {
      void queryClient.invalidateQueries({
        queryKey: ["environments", organizationId, projectId],
      });
    },
  });
};
