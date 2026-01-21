import { Effect } from "effect";
import { useQuery } from "@tanstack/react-query";
import { useServerFn } from "@tanstack/react-start";
import { createServerFn } from "@tanstack/react-start";
import { getRequest } from "@tanstack/react-start/server";
import { authenticate } from "@/auth";
import { runEffect } from "@/app/lib/effect";
import type { Result } from "@/app/lib/types";
import type { PublicUser } from "@/db/schema";

const AUTH_STALE_TIME = 5 * 60 * 1000; // 5 minutes

export const getCurrentUser = createServerFn({ method: "GET" }).handler(
  async (): Promise<Result<PublicUser | null>> => {
    const request = getRequest();
    if (!request) {
      return { success: true, data: null };
    }

    return await runEffect(
      authenticate(request).pipe(Effect.map((result) => result.user)),
    );
  },
);

export const useAuthStatus = () => {
  const getCurrentUserFn = useServerFn(getCurrentUser);

  return useQuery({
    queryKey: ["auth", "me"],
    queryFn: async () => {
      const result = await getCurrentUserFn();
      if (!result.success) {
        return null;
      }
      return result.data;
    },
    retry: false,
    staleTime: AUTH_STALE_TIME,
  });
};
