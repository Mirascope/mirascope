import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Effect } from "effect";

import type { UpdateMemberRoleRequest } from "@/api/organization-memberships.schemas";

import { ApiClient, eq } from "@/app/api/client";

export const useOrganizationMembers = (organizationId: string | null) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: ["organizations", organizationId, "members"],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client["organization-memberships"].list({
            path: { organizationId: organizationId! },
          });
        }),
    }),
    enabled: !!organizationId,
  });
};

export const useUpdateMemberRole = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["organization-memberships", "update"],
      mutationFn: ({
        organizationId,
        memberId,
        data,
      }: {
        organizationId: string;
        memberId: string;
        data: UpdateMemberRoleRequest;
      }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client["organization-memberships"].update({
            path: { organizationId, memberId },
            payload: data,
          });
        }),
    }),
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({
        queryKey: ["organizations", variables.organizationId, "members"],
      });
    },
  });
};

export const useRemoveMember = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["organization-memberships", "delete"],
      mutationFn: ({
        organizationId,
        memberId,
      }: {
        organizationId: string;
        memberId: string;
      }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client["organization-memberships"].delete({
            path: { organizationId, memberId },
          });
        }),
    }),
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({
        queryKey: ["organizations", variables.organizationId, "members"],
      });
    },
  });
};
