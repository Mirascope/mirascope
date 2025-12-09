import { useQuery } from "@tanstack/react-query";
import { useServerFn } from "@tanstack/react-start";
import { createServerFn } from "@tanstack/react-start";
import { getRequest } from "@tanstack/react-start/server";
import { getAuthenticatedUser } from "@/auth";
import { runHandler } from "@/src/lib/effect";

const AUTH_STALE_TIME = 5 * 60 * 1000; // 5 minutes

export const getCurrentUser = createServerFn({ method: "GET" }).handler(
  async () => {
    const request = getRequest();
    if (!request) {
      return null;
    }

    return await runHandler(getAuthenticatedUser(request));
  },
);

export const useAuthStatus = () => {
  const getCurrentUserFn = useServerFn(getCurrentUser);

  return useQuery({
    queryKey: ["auth", "me"],
    queryFn: async () => {
      try {
        return await getCurrentUserFn();
      } catch {
        // Server function returns null for unauthenticated users
        return null;
      }
    },
    retry: false,
    staleTime: AUTH_STALE_TIME,
  });
};
