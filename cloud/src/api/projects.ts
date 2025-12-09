import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Effect } from "effect";
import { ApiClient, eq } from "@/src/api/client";
import type { CreateProjectRequest } from "@/api/projects.schemas";

export const useProjects = (organizationId: string | null) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: ["projects", organizationId],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          const allProjects = yield* client.projects.list();
          // Filter to projects owned by this organization
          if (organizationId) {
            return allProjects.filter((p) => p.orgOwnerId === organizationId);
          }
          return allProjects;
        }),
    }),
    enabled: !!organizationId,
  });
};

export const useProject = (projectId: string) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: ["projects", projectId],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.projects.get({
            path: { projectId },
          });
        }),
    }),
    enabled: !!projectId,
  });
};

export const useCreateProject = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["projects", "create"],
      mutationFn: (data: CreateProjectRequest) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.projects.create({
            payload: data,
          });
        }),
    }),
    onSuccess: (project) => {
      void queryClient.invalidateQueries({
        queryKey: ["projects", project.orgOwnerId],
      });
    },
  });
};

export const useDeleteProject = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["projects", "delete"],
      mutationFn: (projectId: string) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.projects.delete({
            path: { projectId },
          });
        }),
    }),
    onSuccess: () => {
      // Invalidate all project queries since we don't know the orgOwnerId
      void queryClient.invalidateQueries({
        queryKey: ["projects"],
      });
    },
  });
};
