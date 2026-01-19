import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Effect } from "effect";
import { ApiClient, eq } from "@/app/api/client";
import type {
  AddProjectMemberRequest,
  UpdateProjectMemberRoleRequest,
} from "@/api/project-memberships.schemas";

export const useProjectMembers = (
  organizationId: string | null,
  projectId: string | null,
) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: ["projects", organizationId, projectId, "members"],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client["project-memberships"].list({
            path: {
              organizationId: organizationId!,
              projectId: projectId!,
            },
          });
        }),
    }),
    enabled: !!organizationId && !!projectId,
  });
};

export const useAddProjectMember = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["project-memberships", "create"],
      mutationFn: ({
        organizationId,
        projectId,
        data,
      }: {
        organizationId: string;
        projectId: string;
        data: AddProjectMemberRequest;
      }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client["project-memberships"].create({
            path: { organizationId, projectId },
            payload: data,
          });
        }),
    }),
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({
        queryKey: [
          "projects",
          variables.organizationId,
          variables.projectId,
          "members",
        ],
      });
    },
  });
};

export const useUpdateProjectMemberRole = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["project-memberships", "update"],
      mutationFn: ({
        organizationId,
        projectId,
        memberId,
        data,
      }: {
        organizationId: string;
        projectId: string;
        memberId: string;
        data: UpdateProjectMemberRoleRequest;
      }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client["project-memberships"].update({
            path: { organizationId, projectId, memberId },
            payload: data,
          });
        }),
    }),
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({
        queryKey: [
          "projects",
          variables.organizationId,
          variables.projectId,
          "members",
        ],
      });
    },
  });
};

export const useRemoveProjectMember = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["project-memberships", "delete"],
      mutationFn: ({
        organizationId,
        projectId,
        memberId,
      }: {
        organizationId: string;
        projectId: string;
        memberId: string;
      }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client["project-memberships"].delete({
            path: { organizationId, projectId, memberId },
          });
        }),
    }),
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({
        queryKey: [
          "projects",
          variables.organizationId,
          variables.projectId,
          "members",
        ],
      });
    },
  });
};
