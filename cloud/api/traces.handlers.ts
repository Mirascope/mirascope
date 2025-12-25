import { Effect, Option } from "effect";
import { Database } from "@/db";
import { AuthenticatedUser, AuthenticatedApiKey } from "@/auth";
import { UnauthorizedError } from "@/errors";
import type {
  CreateTraceRequest,
  CreateTraceResponse,
} from "@/api/traces.schemas";

export * from "@/api/traces.schemas";

export const createTraceHandler = (
  organizationId: string,
  projectId: string,
  environmentId: string,
  payload: CreateTraceRequest,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;

    const result = yield* db.organizations.projects.environments.traces.create({
      userId: user.id,
      organizationId,
      projectId,
      environmentId,
      data: { resourceSpans: payload.resourceSpans },
    });

    const response: CreateTraceResponse = {
      partialSuccess:
        result.rejectedSpans > 0
          ? {
              rejectedSpans: result.rejectedSpans,
              errorMessage: `${result.rejectedSpans} spans were rejected due to errors`,
            }
          : {},
    };

    return response;
  });

// =============================================================================
// SDK Handlers - Flat paths for SDK usage with API key authentication
// =============================================================================

/**
 * Helper to require API key context for SDK endpoints.
 * Validates that the request has both AuthenticatedUser and AuthenticatedApiKey.
 */
export const requireApiKeyContext = Effect.gen(function* () {
  yield* AuthenticatedUser;
  const maybeApiKey = yield* Effect.serviceOption(AuthenticatedApiKey);
  if (Option.isNone(maybeApiKey)) {
    return yield* Effect.fail(
      new UnauthorizedError({ message: "API key required for this endpoint" }),
    );
  }
  return maybeApiKey.value;
});

export const sdkCreateTraceHandler = (payload: CreateTraceRequest) =>
  Effect.gen(function* () {
    const apiKeyInfo = yield* requireApiKeyContext;
    return yield* createTraceHandler(
      apiKeyInfo.organizationId,
      apiKeyInfo.projectId,
      apiKeyInfo.environmentId,
      payload,
    );
  });
