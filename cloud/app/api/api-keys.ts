import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Effect } from "effect";

import type { CreateApiKeyRequest } from "@/api/api-keys.schemas";

import { ApiClient, eq } from "@/app/api/client";

export const useAllApiKeys = (organizationId: string | null) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: ["api-keys", "all", organizationId],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.apiKeys.listAllForOrg({
            path: { organizationId: organizationId! },
          });
        }),
    }),
    enabled: !!organizationId,
  });
};

export const useApiKeys = (
  organizationId: string | null,
  projectId: string | null,
  environmentId: string | null,
) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: ["api-keys", organizationId, projectId, environmentId],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.apiKeys.list({
            path: {
              organizationId: organizationId!,
              projectId: projectId!,
              environmentId: environmentId!,
            },
          });
        }),
    }),
    enabled: !!organizationId && !!projectId && !!environmentId,
  });
};

export const useApiKey = (
  organizationId: string,
  projectId: string,
  environmentId: string,
  apiKeyId: string,
) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: [
        "api-keys",
        organizationId,
        projectId,
        environmentId,
        apiKeyId,
      ],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.apiKeys.get({
            path: { organizationId, projectId, environmentId, apiKeyId },
          });
        }),
    }),
    enabled: !!organizationId && !!projectId && !!environmentId && !!apiKeyId,
  });
};

export const useCreateApiKey = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["api-keys", "create"],
      mutationFn: ({
        organizationId,
        projectId,
        environmentId,
        data,
      }: {
        organizationId: string;
        projectId: string;
        environmentId: string;
        data: CreateApiKeyRequest;
      }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.apiKeys.create({
            path: { organizationId, projectId, environmentId },
            payload: data,
          });
        }),
    }),
    onSuccess: (_, { organizationId, projectId, environmentId }) => {
      void queryClient.invalidateQueries({
        queryKey: ["api-keys", organizationId, projectId, environmentId],
      });
      // Also invalidate the "all" query for the organization
      void queryClient.invalidateQueries({
        queryKey: ["api-keys", "all", organizationId],
      });
    },
  });
};

export const useDeleteApiKey = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["api-keys", "delete"],
      mutationFn: ({
        organizationId,
        projectId,
        environmentId,
        apiKeyId,
      }: {
        organizationId: string;
        projectId: string;
        environmentId: string;
        apiKeyId: string;
      }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.apiKeys.delete({
            path: { organizationId, projectId, environmentId, apiKeyId },
          });
        }),
    }),
    onSuccess: (_, { organizationId, projectId, environmentId }) => {
      void queryClient.invalidateQueries({
        queryKey: ["api-keys", organizationId, projectId, environmentId],
      });
      // Also invalidate the "all" query for the organization
      void queryClient.invalidateQueries({
        queryKey: ["api-keys", "all", organizationId],
      });
    },
  });
};
