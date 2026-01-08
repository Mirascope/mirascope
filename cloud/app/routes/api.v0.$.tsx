import { createFileRoute } from "@tanstack/react-router";
import { Effect, Layer } from "effect";
import { handleRequest } from "@/api/handler";
import { handleErrors, handleDefects } from "@/api/utils";
import { NotFoundError, InternalError } from "@/errors";
import { authenticate, type PathParameters } from "@/auth";
import { Database } from "@/db";
import { ClickHouse } from "@/clickhouse/client";
import { ClickHouseSearch } from "@/clickhouse/search";
import { SettingsService, getSettings } from "@/settings";

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

          const pathParams = extractPathParameters(params["*"]);
          const authResult = yield* authenticate(request, pathParams);

          const clickHouseSearch = yield* ClickHouseSearch;

          const result = yield* handleRequest(request, {
            prefix: "/api/v0",
            user: authResult.user,
            apiKeyInfo: authResult.apiKeyInfo,
            environment: process.env.ENVIRONMENT || "development",
            clickHouseSearch,
          });

          if (!result.matched) {
            return yield* new NotFoundError({ message: "Route not found" });
          }

          return result.response;
        }).pipe(
          Effect.provide(
            Layer.mergeAll(
              Database.Live({
                database: { connectionString: databaseUrl },
                payments: {
                  apiKey: process.env.STRIPE_SECRET_KEY || "",
                  routerPriceId: process.env.STRIPE_ROUTER_PRICE_ID || "",
                },
              }),
              ClickHouseSearch.Default.pipe(
                Layer.provide(ClickHouse.Default),
                Layer.provide(
                  Layer.succeed(SettingsService, {
                    ...getSettings(),
                    env: process.env.ENVIRONMENT || "development",
                  }),
                ),
              ),
            ),
          ),
          handleErrors,
          handleDefects,
        );

        return Effect.runPromise(handler);
      },
    },
  },
});
