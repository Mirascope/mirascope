import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Effect } from "effect";

import type {
  Claw,
  CreateClawRequest,
  UpdateClawRequest,
} from "@/api/claws.schemas";

import { ApiClient, eq } from "@/app/api/client";
import { generateSlug } from "@/db/slug";

export const useClaws = (organizationId: string | null) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: ["claws", organizationId],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.claws.list({
            path: { organizationId: organizationId! },
          });
        }),
    }),
    enabled: !!organizationId,
  });
};

export const useClaw = (
  organizationId: string | null,
  clawId: string | null,
) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: ["claws", organizationId, clawId],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.claws.get({
            path: { organizationId: organizationId!, clawId: clawId! },
          });
        }),
    }),
    enabled: !!organizationId && !!clawId,
  });
};

export const useCreateClaw = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["claws", "create"],
      mutationFn: (data: {
        organizationId: string;
        name: string;
        description?: string;
        model?: CreateClawRequest["model"];
        weeklySpendingGuardrailCenticents?: bigint | null;
        homeProjectId?: string;
      }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.claws.create({
            path: { organizationId: data.organizationId },
            payload: {
              name: data.name,
              slug: generateSlug(data.name),
              description: data.description,
              model: data.model,
              weeklySpendingGuardrailCenticents:
                data.weeklySpendingGuardrailCenticents,
              homeProjectId: data.homeProjectId,
            },
          });
        }),
    }),
    onSuccess: (claw) => {
      // Insert the server-returned claw into cache to prevent "not found" flash
      // on navigation. We intentionally skip invalidateQueries here — the server
      // response is authoritative, and an immediate refetch can return stale data
      // from Hyperdrive's query cache that doesn't yet include the new claw.
      queryClient.setQueryData(
        ["claws", claw.organizationId],
        (old: unknown[] | undefined) => (old ? [...old, claw] : [claw]),
      );
    },
  });
};

export const useUpdateClaw = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["claws", "update"],
      mutationFn: (data: {
        organizationId: string;
        clawId: string;
        updates: UpdateClawRequest;
      }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.claws.update({
            path: {
              organizationId: data.organizationId,
              clawId: data.clawId,
            },
            payload: data.updates,
          });
        }),
    }),
    // Optimistic update: apply changes to cache immediately
    onMutate: async (variables) => {
      await queryClient.cancelQueries({
        queryKey: ["claws", variables.organizationId],
      });

      const previousClaws = queryClient.getQueryData<readonly Claw[]>([
        "claws",
        variables.organizationId,
      ]);

      // Optimistically merge updates into the cached claw
      queryClient.setQueryData<readonly Claw[]>(
        ["claws", variables.organizationId],
        (old) =>
          old?.map((c) =>
            c.id === variables.clawId ? { ...c, ...variables.updates } : c,
          ) ?? [],
      );

      return { previousClaws };
    },
    onError: (_err, variables, context) => {
      if (context?.previousClaws) {
        queryClient.setQueryData(
          ["claws", variables.organizationId],
          context.previousClaws,
        );
      }
    },
    // Only refetch on error to re-sync cache with server.
    // On success, the optimistic merge is sufficient — an immediate refetch can
    // return stale data from Hyperdrive's query cache that reverts the update.
    onSettled: (_data, err, variables) => {
      if (err) {
        void queryClient.invalidateQueries({
          queryKey: ["claws", variables.organizationId],
        });
      }
    },
  });
};

export const useDeleteClaw = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["claws", "delete"],
      mutationFn: (data: { organizationId: string; clawId: string }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.claws.delete({
            path: {
              organizationId: data.organizationId,
              clawId: data.clawId,
            },
          });
        }),
    }),
    // Optimistic update: remove claw from cache immediately
    onMutate: async (variables) => {
      // Cancel in-flight queries so they don't overwrite our optimistic update
      await queryClient.cancelQueries({
        queryKey: ["claws", variables.organizationId],
      });

      // Snapshot previous cache for rollback
      const previousClaws = queryClient.getQueryData<readonly Claw[]>([
        "claws",
        variables.organizationId,
      ]);

      // Optimistically remove the claw from the list
      queryClient.setQueryData<readonly Claw[]>(
        ["claws", variables.organizationId],
        (old) => old?.filter((c) => c.id !== variables.clawId) ?? [],
      );

      // Also remove the individual claw query
      queryClient.removeQueries({
        queryKey: ["claws", variables.organizationId, variables.clawId],
      });

      return { previousClaws };
    },
    // Rollback on error
    onError: (_err, variables, context) => {
      if (context?.previousClaws) {
        queryClient.setQueryData(
          ["claws", variables.organizationId],
          context.previousClaws,
        );
      }
    },
    // Only refetch on error to re-sync cache with server.
    // On success, we trust the optimistic update — refetching immediately can
    // return stale data from Hyperdrive's query cache (the SELECT hits a cached
    // result that still includes the just-deleted claw).
    onSettled: (_data, err, variables) => {
      if (err) {
        void queryClient.invalidateQueries({
          queryKey: ["claws", variables.organizationId],
        });
      }
    },
  });
};

export const useClawUsage = (
  organizationId: string | null,
  clawId: string | null,
) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: ["claws", organizationId, clawId, "usage"],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.claws.getUsage({
            path: { organizationId: organizationId!, clawId: clawId! },
          });
        }),
    }),
    enabled: !!organizationId && !!clawId,
  });
};

export const useClawSecrets = (
  organizationId: string | null,
  clawId: string | null,
) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: ["claws", organizationId, clawId, "secrets"],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.claws.getSecrets({
            path: { organizationId: organizationId!, clawId: clawId! },
          });
        }),
    }),
    enabled: !!organizationId && !!clawId,
  });
};

export const useUpdateClawSecrets = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["claws", "updateSecrets"],
      mutationFn: (data: {
        organizationId: string;
        clawId: string;
        secrets: Record<string, string>;
      }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.claws.updateSecrets({
            path: {
              organizationId: data.organizationId,
              clawId: data.clawId,
            },
            payload: data.secrets,
          });
        }),
    }),
    onSuccess: (_, variables) => {
      void queryClient.invalidateQueries({
        queryKey: [
          "claws",
          variables.organizationId,
          variables.clawId,
          "secrets",
        ],
      });
    },
  });
};

export const useRestartClaw = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["claws", "restart"],
      mutationFn: (data: { organizationId: string; clawId: string }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.claws.restart({
            path: {
              organizationId: data.organizationId,
              clawId: data.clawId,
            },
          });
        }),
    }),
    onSuccess: (_, variables) => {
      // Refetch claws to pick up status changes (e.g. provisioning)
      void queryClient.invalidateQueries({
        queryKey: ["claws", variables.organizationId],
      });
    },
  });
};
