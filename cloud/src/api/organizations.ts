import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Effect } from "effect";
import { ApiClient, eq } from "@/src/api/client";
import type { CreateOrganizationRequest } from "@/api/organizations.schemas";

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
    onSuccess: () => {
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
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["organizations"] });
    },
  });
};
