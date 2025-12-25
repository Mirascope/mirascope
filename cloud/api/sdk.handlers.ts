/**
 * SDK Flat API Handlers
 *
 * These handlers require API key authentication and derive
 * organizationId, projectId, and environmentId from the API key context.
 */
import { Effect, Option } from "effect";
import { AuthenticatedUser, AuthenticatedApiKey } from "@/auth";
import { UnauthorizedError } from "@/errors";
import { createTraceHandler } from "@/api/traces.handlers";
import type { CreateTraceRequest } from "@/api/sdk.schemas";

export * from "@/api/sdk.schemas";

/**
 * Helper to require API key context for SDK endpoints.
 * Validates that the request has both AuthenticatedUser and AuthenticatedApiKey.
 * Uses Effect.serviceOption to make AuthenticatedApiKey optional in context,
 * but fails with UnauthorizedError if not present.
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

/**
 * SDK handler for creating traces.
 * Derives org/project/env from API key context.
 */
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
