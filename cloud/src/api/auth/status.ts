import { useQuery } from "@tanstack/react-query";
import { useServerFn } from "@tanstack/react-start";
import { createServerFn } from "@tanstack/react-start";
import { getRequest } from "@tanstack/react-start/server";
import { Effect } from "effect";
import { DatabaseService } from "@/db";
import { runHandler } from "@/src/lib/effect";
import { getSessionIdFromCookie } from "@/auth/utils";

const AUTH_STALE_TIME = 5 * 60 * 1000; // 5 minutes

export const getCurrentUser = createServerFn({ method: "GET" }).handler(
  async () => {
    return await runHandler(
      Effect.gen(function* () {
        const request = getRequest();

        if (!request) {
          return null;
        }

        const sessionId = getSessionIdFromCookie(request);

        if (!sessionId) {
          return null;
        }

        const db = yield* DatabaseService;
        return yield* db.sessions
          .findUserBySessionId(sessionId)
          .pipe(Effect.catchAll(() => Effect.succeed(null)));
      }),
    );
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
