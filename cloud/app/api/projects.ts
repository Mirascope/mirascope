import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Effect } from "effect";

import { ApiClient, eq } from "@/app/api/client";
import { generateSlug } from "@/db/slug";

export const useProjects = (organizationId: string | null) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: ["projects", organizationId],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.projects.list({
            path: { organizationId: organizationId! },
          });
        }),
    }),
    enabled: !!organizationId,
  });
};

export const useProject = (organizationId: string, projectId: string) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: ["projects", organizationId, projectId],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.projects.get({
            path: { organizationId, projectId },
          });
        }),
    }),
    enabled: !!organizationId && !!projectId,
  });
};

export const useCreateProject = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["projects", "create"],
      mutationFn: (data: { organizationId: string; name: string }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.projects.create({
            path: { organizationId: data.organizationId },
            payload: { name: data.name, slug: generateSlug(data.name) },
          });
        }),
    }),
    onSuccess: (project) => {
      // Optimistically insert into cache to prevent "not found" flash on navigation
      queryClient.setQueryData(
        ["projects", project.organizationId],
        (old: unknown[] | undefined) => (old ? [...old, project] : [project]),
      );
      void queryClient.invalidateQueries({
        queryKey: ["projects", project.organizationId],
      });
    },
  });
};

export const useDeleteProject = () => {
  const queryClient = useQueryClient();

  return useMutation({
    ...eq.mutationOptions({
      mutationKey: ["projects", "delete"],
      mutationFn: (data: { organizationId: string; projectId: string }) =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.projects.delete({
            path: {
              organizationId: data.organizationId,
              projectId: data.projectId,
            },
          });
        }),
    }),
    onSuccess: (_, variables) => {
      void queryClient.invalidateQueries({
        queryKey: ["projects", variables.organizationId],
      });
    },
  });
};
