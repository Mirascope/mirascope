import { createFileRoute } from "@tanstack/react-router";
import { Effect } from "effect";
import { handleRequest } from "@/api/handler";
import { handleErrors, handleDefects } from "@/api/utils";
import { NotFoundError, InternalError, UnauthorizedError } from "@/errors";
import { authenticate, type PathParameters } from "@/auth";
import { Database } from "@/db";

function extractPathParameters(
  splat: string | undefined,
): PathParameters | undefined {
  if (!splat) return undefined;

  const pathParts = splat.split("/").filter(Boolean);

  // API v0 routes follow pattern: organizations/:id/projects/:id/environments/:id/...
  const pathParams: PathParameters = {};
  let hasParams = false;

  for (let i = 0; i < pathParts.length; i++) {
    if (pathParts[i] === "organizations" && pathParts[i + 1]) {
      pathParams.organizationId = pathParts[i + 1];
      hasParams = true;
    } else if (pathParts[i] === "projects" && pathParts[i + 1]) {
      pathParams.projectId = pathParts[i + 1];
      hasParams = true;
    } else if (pathParts[i] === "environments" && pathParts[i + 1]) {
      pathParams.environmentId = pathParts[i + 1];
      hasParams = true;
    }
  }

  return hasParams ? pathParams : undefined;
}

const API_KEY_REQUIRED_PREFIXES = new Set([
  "traces",
  "functions",
  "annotations",
]);

function requiresApiKey(splat: string | undefined): boolean {
  if (!splat) return false;
  const firstSegment = splat.split("/").filter(Boolean)[0];
  return firstSegment ? API_KEY_REQUIRED_PREFIXES.has(firstSegment) : false;
}

export const Route = createFileRoute("/api/v0/$")({
  server: {
    handlers: {
      ANY: async ({
        request,
        params,
      }: {
        request: Request;
        params: { "*"?: string };
      }) => {
        const databaseUrl = process.env.DATABASE_URL;

        const handler = Effect.gen(function* () {
          if (!databaseUrl) {
            return yield* new InternalError({
              message: "Database not configured",
            });
          }

          const pathParams = extractPathParameters(params["*"]);

          const authResult = yield* authenticate(request, pathParams);

          if (requiresApiKey(params["*"]) && !authResult.apiKeyInfo) {
            return yield* new UnauthorizedError({
              message: "API key required",
            });
          }

          const result = yield* handleRequest(request, {
            prefix: "/api/v0",
            authenticatedUser: authResult.user,
            authenticatedApiKey: authResult.apiKeyInfo,
            environment: process.env.ENVIRONMENT || "development",
          });

          if (!result.matched) {
            return yield* new NotFoundError({ message: "Route not found" });
          }

          return result.response;
        }).pipe(
          Effect.provide(Database.Live({ connectionString: databaseUrl })),
          handleErrors,
          handleDefects,
        );

        return Effect.runPromise(handler);
      },
    },
  },
});
