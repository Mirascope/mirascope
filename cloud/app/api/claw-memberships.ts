import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Effect } from "effect";

import type {
  AddClawMemberRequest,
  UpdateClawMemberRoleRequest,
} from "@/api/claw-memberships.schemas";

import { ApiClient, eq } from "@/app/api/client";

export const useClawMembers = (
  organizationId: string | null,
  clawId: string | null,
) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: ["claws", organizationId, clawId, "members"],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client["claw-memberships"].list({
            path: {
              organizationId: organizationId!,
              clawId: clawId!,
            },
          });
        }),
    }),
    enabled: !!organizationId && !!clawId,
  });
};

export const useAddClawMember = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["claw-memberships", "create"],
      mutationFn: ({
        organizationId,
        clawId,
        data,
      }: {
        organizationId: string;
        clawId: string;
        data: AddClawMemberRequest;
      }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client["claw-memberships"].create({
            path: { organizationId, clawId },
            payload: data,
          });
        }),
    }),
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({
        queryKey: [
          "claws",
          variables.organizationId,
          variables.clawId,
          "members",
        ],
      });
    },
  });
};

export const useUpdateClawMemberRole = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["claw-memberships", "update"],
      mutationFn: ({
        organizationId,
        clawId,
        memberId,
        data,
      }: {
        organizationId: string;
        clawId: string;
        memberId: string;
        data: UpdateClawMemberRoleRequest;
      }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client["claw-memberships"].update({
            path: { organizationId, clawId, memberId },
            payload: data,
          });
        }),
    }),
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({
        queryKey: [
          "claws",
          variables.organizationId,
          variables.clawId,
          "members",
        ],
      });
    },
  });
};

export const useRemoveClawMember = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["claw-memberships", "delete"],
      mutationFn: ({
        organizationId,
        clawId,
        memberId,
      }: {
        organizationId: string;
        clawId: string;
        memberId: string;
      }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client["claw-memberships"].delete({
            path: { organizationId, clawId, memberId },
          });
        }),
    }),
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({
        queryKey: [
          "claws",
          variables.organizationId,
          variables.clawId,
          "members",
        ],
      });
    },
  });
};
