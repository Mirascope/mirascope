import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useServerFn } from "@tanstack/react-start";
import { createServerFn } from "@tanstack/react-start";
import { Effect } from "effect";
import { DatabaseService } from "@/db";
import { AuthenticatedUser } from "@/auth/context";
import { runAuthenticatedEffect } from "@/src/lib/effect";
import type { Result } from "@/src/lib/types";
import type { PublicOrganizationWithMembership } from "@/db/schema/organization-memberships";
import type { CreateOrganizationRequest } from "@/api/organizations.schemas";

export const listOrganizations = createServerFn({ method: "GET" }).handler(
  async (): Promise<Result<PublicOrganizationWithMembership[]>> => {
    return await runAuthenticatedEffect(
      Effect.gen(function* () {
        const db = yield* DatabaseService;
        const { id: userId } = yield* AuthenticatedUser;
        return yield* db.organizations.findAll(userId);
      }),
    );
  },
);

export const getOrganization = createServerFn({ method: "GET" })
  .inputValidator((data: { id: string }) => data)
  .handler(async (ctx): Promise<Result<PublicOrganizationWithMembership>> => {
    return await runAuthenticatedEffect(
      Effect.gen(function* () {
        const db = yield* DatabaseService;
        const { id: userId } = yield* AuthenticatedUser;
        return yield* db.organizations.findById(ctx.data.id, userId);
      }),
    );
  });

export const createOrganization = createServerFn({ method: "POST" })
  .inputValidator((data: CreateOrganizationRequest) => data)
  .handler(async (ctx): Promise<Result<PublicOrganizationWithMembership>> => {
    return await runAuthenticatedEffect(
      Effect.gen(function* () {
        const db = yield* DatabaseService;
        const { id: userId } = yield* AuthenticatedUser;
        return yield* db.organizations.create({ name: ctx.data.name }, userId);
      }),
    );
  });

export const deleteOrganization = createServerFn({ method: "POST" })
  .inputValidator((data: { id: string }) => data)
  .handler(async (ctx): Promise<Result<void>> => {
    return await runAuthenticatedEffect(
      Effect.gen(function* () {
        const db = yield* DatabaseService;
        const { id: userId } = yield* AuthenticatedUser;
        return yield* db.organizations.delete(ctx.data.id, userId);
      }),
    );
  });

export const useOrganizations = () => {
  const listOrganizationsFn = useServerFn(listOrganizations);

  return useQuery({
    queryKey: ["organizations"],
    queryFn: async () => {
      const result = await listOrganizationsFn();
      if (!result.success) {
        throw new Error(result.error);
      }
      return result.data;
    },
  });
};

export const useOrganization = (id: string) => {
  const getOrganizationFn = useServerFn(getOrganization);

  return useQuery({
    queryKey: ["organizations", id],
    queryFn: async () => {
      const result = await getOrganizationFn({ data: { id } });
      if (!result.success) {
        throw new Error(result.error);
      }
      return result.data;
    },
    enabled: !!id,
  });
};

export const useCreateOrganization = () => {
  const createOrganizationFn = useServerFn(createOrganization);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CreateOrganizationRequest) => {
      const result = await createOrganizationFn({ data });
      if (!result.success) {
        throw new Error(result.error);
      }
      return result.data;
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["organizations"] });
    },
  });
};

export const useDeleteOrganization = () => {
  const deleteOrganizationFn = useServerFn(deleteOrganization);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const result = await deleteOrganizationFn({ data: { id } });
      if (!result.success) {
        throw new Error(result.error);
      }
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["organizations"] });
    },
  });
};
