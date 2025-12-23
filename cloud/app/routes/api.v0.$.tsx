import { createFileRoute } from "@tanstack/react-router";
import { Effect } from "effect";
import { handleRequest } from "@/api/handler";
import { handleErrors, handleDefects } from "@/api/utils";
import { NotFoundError, InternalError } from "@/errors";
import { getAuthenticatedUser, type PathParameters } from "@/auth";
import { Database } from "@/db";

/**
 * Extract path parameters from the splat path for API key validation.
 * Parses organizationId, projectId, and environmentId from the path.
 *
 * @param splat - The wildcard path captured by TanStack Router (e.g., "organizations/123/projects/456/environments/789")
 */
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

          // Extract path parameters from TanStack Router's splat for API key validation
          const pathParams = extractPathParameters(params["*"]);

          // getAuthenticatedUser now returns UnauthorizedError if authentication fails
          const authenticatedUser = yield* getAuthenticatedUser(
            request,
            pathParams,
          );

          const result = yield* handleRequest(request, {
            prefix: "/api/v0",
            authenticatedUser,
            environment: process.env.ENVIRONMENT || "development",
          });

          if (!result.matched) {
            return yield* new NotFoundError({ message: "Route not found" });
          }

          return result.response;
        }).pipe(
          Effect.provide(
            Database.Live({
              database: { connectionString: databaseUrl },
              stripe: {
                apiKey: process.env.STRIPE_SECRET_KEY || "",
                routerPriceId: process.env.STRIPE_ROUTER_PRICE_ID || "",
              },
            }),
          ),
          handleErrors,
          handleDefects,
        );

        return Effect.runPromise(handler);
      },
    },
  },
});
