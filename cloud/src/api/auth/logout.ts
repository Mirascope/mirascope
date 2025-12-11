import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useServerFn } from "@tanstack/react-start";
import { createServerFn } from "@tanstack/react-start";
import { getRequest } from "@tanstack/react-start/server";
import { Effect } from "effect";
import { DatabaseService } from "@/db";
import { runEffectResponse } from "@/src/lib/effect";
import { getSessionIdFromCookie, clearSessionCookie } from "@/auth/utils";

export const logout = createServerFn({ method: "POST" }).handler(async () => {
  return await runEffectResponse(
    Effect.gen(function* () {
      const request = getRequest();

      if (!request) {
        return new Response(
          JSON.stringify({ success: false, error: "No request available" }),
          { status: 400, headers: { "Content-Type": "application/json" } },
        );
      }

      const sessionId = getSessionIdFromCookie(request);

      if (!sessionId) {
        // Even if no session ID, still clear the cookie in case it exists
        return new Response(JSON.stringify({ success: true }), {
          status: 200,
          headers: {
            "Content-Type": "application/json",
            "Set-Cookie": clearSessionCookie(),
          },
        });
      }

      const db = yield* DatabaseService;
      yield* db.sessions.delete({ id: sessionId }).pipe(
        Effect.catchAll(() => Effect.succeed(undefined)), // Ignore deletion errors
      );

      // Return success response with cleared cookie
      return new Response(JSON.stringify({ success: true }), {
        status: 200,
        headers: {
          "Content-Type": "application/json",
          "Set-Cookie": clearSessionCookie(),
        },
      });
    }),
  );
});

export const useLogout = () => {
  const logoutFn = useServerFn(logout);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      await logoutFn();
    },
    onSuccess: () => {
      // Clear all queries on logout
      queryClient.clear();
    },
  });
};
