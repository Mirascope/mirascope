import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Effect } from "effect";

import type {
  CreateOrganizationRequest,
  CreatePaymentIntentRequest,
  PreviewSubscriptionChangeRequest,
  UpdateSubscriptionRequest,
  UpdateAutoReloadSettingsRequest,
} from "@/api/organizations.schemas";
import type { PublicOrganizationWithMembership } from "@/db/schema";

import { ApiClient, eq } from "@/app/api/client";

export const useOrganizations = () => {
  return useQuery(
    eq.queryOptions({
      queryKey: ["organizations"],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.organizations.list();
        }),
    }),
  );
};

export const useOrganization = (id: string) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: ["organizations", id],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.organizations.get({ path: { id } });
        }),
    }),
    enabled: !!id,
  });
};

export const useCreateOrganization = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["organizations", "create"],
      mutationFn: (data: CreateOrganizationRequest) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.organizations.create({ payload: data });
        }),
    }),
    onSuccess: (organization) => {
      // Cancel in-flight queries so they don't overwrite our optimistic insert
      void queryClient.cancelQueries({ queryKey: ["organizations"] });

      // Optimistically insert into cache to prevent "not found" flash on navigation
      queryClient.setQueryData(
        ["organizations"],
        (old: unknown[] | undefined) =>
          old ? [...old, organization] : [organization],
      );
      void queryClient.invalidateQueries({ queryKey: ["organizations"] });
    },
  });
};

export const useDeleteOrganization = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["organizations", "delete"],
      mutationFn: (id: string) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.organizations.delete({ path: { id } });
        }),
    }),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: ["organizations"] });

      const previousOrgs = queryClient.getQueryData<
        readonly PublicOrganizationWithMembership[]
      >(["organizations"]);

      queryClient.setQueryData<readonly PublicOrganizationWithMembership[]>(
        ["organizations"],
        (old) => old?.filter((o) => o.id !== id) ?? [],
      );

      return { previousOrgs };
    },
    onError: (_err, _id, context) => {
      if (context?.previousOrgs) {
        queryClient.setQueryData(["organizations"], context.previousOrgs);
      }
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: ["organizations"] });
    },
  });
};

export const useOrganizationRouterBalance = (
  organizationId: string | undefined,
) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: ["organizations", organizationId, "router-balance"],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.organizations.routerBalance({
            path: { id: organizationId! },
          });
        }),
    }),
    enabled: !!organizationId,
  });
};

export const useCreatePaymentIntent = () => {
  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["organizations", "createPaymentIntent"],
      mutationFn: ({
        organizationId,
        data,
      }: {
        organizationId: string;
        data: CreatePaymentIntentRequest;
      }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.organizations.createPaymentIntent({
            path: { id: organizationId },
            payload: data,
          });
        }),
    }),
    // NOTE: no `onSuccess` handler since we need to invalidate in the dialogue.
    // If we do query invalidation here, we invalidate after creating intent, not
    // after confirmation of a successful payment (which require the webhook)
  });
};

export const useSubscription = (organizationId: string | undefined) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: ["organizations", organizationId, "subscription"],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.organizations.subscription({
            path: { id: organizationId! },
          });
        }),
    }),
    enabled: !!organizationId,
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });
};

export const usePreviewSubscriptionChange = () => {
  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["organizations", "previewSubscriptionChange"],
      mutationFn: ({
        organizationId,
        data,
      }: {
        organizationId: string;
        data: PreviewSubscriptionChangeRequest;
      }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.organizations.previewSubscriptionChange({
            path: { id: organizationId },
            payload: data,
          });
        }),
    }),
  });
};

export const useUpdateSubscription = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["organizations", "updateSubscription"],
      mutationFn: ({
        organizationId,
        data,
      }: {
        organizationId: string;
        data: UpdateSubscriptionRequest;
      }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.organizations.updateSubscription({
            path: { id: organizationId },
            payload: data,
          });
        }),
    }),
    onSuccess: (_data, variables) => {
      // Invalidate subscription query to refresh the UI
      void queryClient.invalidateQueries({
        queryKey: ["organizations", variables.organizationId, "subscription"],
      });
    },
  });
};

export const useCancelScheduledDowngrade = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["organizations", "cancelScheduledDowngrade"],
      mutationFn: (organizationId: string) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.organizations.cancelScheduledDowngrade({
            path: { id: organizationId },
          });
        }),
    }),
    onSuccess: (_data, organizationId) => {
      // Invalidate subscription query to refresh the UI
      void queryClient.invalidateQueries({
        queryKey: ["organizations", organizationId, "subscription"],
      });
    },
  });
};

export const usePaymentMethod = (organizationId: string | undefined) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: ["organizations", organizationId, "payment-method"],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.organizations.getPaymentMethod({
            path: { id: organizationId! },
          });
        }),
    }),
    enabled: !!organizationId,
    staleTime: 5 * 60 * 1000,
  });
};

export const useCreateSetupIntent = () => {
  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["organizations", "createSetupIntent"],
      mutationFn: (organizationId: string) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.organizations.createSetupIntent({
            path: { id: organizationId },
          });
        }),
    }),
  });
};

export const useRemovePaymentMethod = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["organizations", "removePaymentMethod"],
      mutationFn: (organizationId: string) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.organizations.removePaymentMethod({
            path: { id: organizationId },
          });
        }),
    }),
    onSuccess: (_data, organizationId) => {
      void queryClient.invalidateQueries({
        queryKey: ["organizations", organizationId, "payment-method"],
      });
    },
  });
};

export const useAutoReloadSettings = (organizationId: string | undefined) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: ["organizations", organizationId, "auto-reload"],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.organizations.getAutoReloadSettings({
            path: { id: organizationId! },
          });
        }),
    }),
    enabled: !!organizationId,
    staleTime: 5 * 60 * 1000,
  });
};

export const useUpdateAutoReloadSettings = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["organizations", "updateAutoReloadSettings"],
      mutationFn: ({
        organizationId,
        data,
      }: {
        organizationId: string;
        data: UpdateAutoReloadSettingsRequest;
      }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.organizations.updateAutoReloadSettings({
            path: { id: organizationId },
            payload: data,
          });
        }),
    }),
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({
        queryKey: ["organizations", variables.organizationId, "auto-reload"],
      });
    },
  });
};
