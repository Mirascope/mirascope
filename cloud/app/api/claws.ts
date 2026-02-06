import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Effect } from "effect";

import type { CreateClawRequest, UpdateClawRequest } from "@/api/claws.schemas";

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
      void queryClient.invalidateQueries({
        queryKey: ["claws", claw.organizationId],
      });
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
    onSuccess: (claw) => {
      void queryClient.invalidateQueries({
        queryKey: ["claws", claw.organizationId],
      });
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
    onSuccess: (_, variables) => {
      void queryClient.invalidateQueries({
        queryKey: ["claws", variables.organizationId],
      });
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
