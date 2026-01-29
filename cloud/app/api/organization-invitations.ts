import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Effect } from "effect";

import type { CreateInvitationRequest } from "@/api/organization-invitations.schemas";

import { ApiClient, eq } from "@/app/api/client";

export const useOrganizationInvitations = (organizationId: string) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: ["organizations", organizationId, "invitations"],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client["organization-invitations"].list({
            path: { organizationId },
          });
        }),
    }),
    enabled: !!organizationId,
  });
};

export const useCreateInvitation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["organization-invitations", "create"],
      mutationFn: ({
        organizationId,
        data,
      }: {
        organizationId: string;
        data: CreateInvitationRequest;
      }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client["organization-invitations"].create({
            path: { organizationId },
            payload: data,
          });
        }),
    }),
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({
        queryKey: ["organizations", variables.organizationId, "invitations"],
      });
    },
  });
};

export const useResendInvitation = () => {
  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["organization-invitations", "resend"],
      mutationFn: ({
        organizationId,
        invitationId,
      }: {
        organizationId: string;
        invitationId: string;
      }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client["organization-invitations"].resend({
            path: { organizationId, invitationId },
          });
        }),
    }),
  });
};

export const useRevokeInvitation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["organization-invitations", "revoke"],
      mutationFn: ({
        organizationId,
        invitationId,
      }: {
        organizationId: string;
        invitationId: string;
      }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client["organization-invitations"].revoke({
            path: { organizationId, invitationId },
          });
        }),
    }),
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({
        queryKey: ["organizations", variables.organizationId, "invitations"],
      });
    },
  });
};

export const useAcceptInvitation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["organization-invitations", "accept"],
      mutationFn: (token: string) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client["organization-invitations"].accept({
            payload: { token },
          });
        }),
    }),
    onSuccess: () => {
      // Invalidate organizations list so the new membership appears
      void queryClient.invalidateQueries({
        queryKey: ["organizations"],
      });
    },
  });
};
