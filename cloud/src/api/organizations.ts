import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Effect } from "effect";
import { eq, ApiClient } from "@/src/api/effect-query";
import type { OrganizationWithRole } from "@/api/api";

export const organizationKeys = {
  all: ["organizations"] as const,
  list: () => [...organizationKeys.all, "list"] as const,
};

export function useOrganizations(options?: { enabled?: boolean }) {
  return useQuery({
    ...eq.queryOptions({
      queryKey: organizationKeys.list(),
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.organizations.list();
        }),
    }),
    select: (data) => data.organizations as OrganizationWithRole[],
    enabled: options?.enabled ?? true,
  });
}

export function useCreateOrganization() {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["organizations", "create"],
      mutationFn: (data: { name: string }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.organizations.create({ payload: data });
        }),
    }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: organizationKeys.all });
    },
  });
}

export function useDeleteOrganization() {
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
      void queryClient.invalidateQueries({ queryKey: organizationKeys.all });
    },
  });
}
