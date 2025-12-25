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
import {
  registerFunctionHandler,
  getFunctionByHashHandler,
  getFunctionHandler,
  listFunctionsHandler,
} from "@/api/functions.handlers";
import type { CreateTraceRequest, RegisterFunctionRequest } from "@/api/sdk.schemas";

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

/**
 * SDK handler for registering functions.
 * Derives org/project/env from API key context.
 */
export const sdkRegisterFunctionHandler = (payload: RegisterFunctionRequest) =>
  Effect.gen(function* () {
    const apiKeyInfo = yield* requireApiKeyContext;
    return yield* registerFunctionHandler(
      apiKeyInfo.organizationId,
      apiKeyInfo.projectId,
      apiKeyInfo.environmentId,
      payload,
    );
  });

/**
 * SDK handler for getting function by hash.
 * Derives org/project/env from API key context.
 */
export const sdkGetFunctionByHashHandler = (hash: string) =>
  Effect.gen(function* () {
    const apiKeyInfo = yield* requireApiKeyContext;
    return yield* getFunctionByHashHandler(
      apiKeyInfo.organizationId,
      apiKeyInfo.projectId,
      apiKeyInfo.environmentId,
      hash,
    );
  });

/**
 * SDK handler for getting function by ID.
 * Derives org/project/env from API key context.
 */
export const sdkGetFunctionHandler = (id: string) =>
  Effect.gen(function* () {
    const apiKeyInfo = yield* requireApiKeyContext;
    return yield* getFunctionHandler(
      apiKeyInfo.organizationId,
      apiKeyInfo.projectId,
      apiKeyInfo.environmentId,
      id,
    );
  });

/**
 * SDK handler for listing functions.
 * Derives org/project/env from API key context.
 */
export const sdkListFunctionsHandler = (params: {
  name?: string;
  tags?: string;
  limit?: number;
  offset?: number;
}) =>
  Effect.gen(function* () {
    const apiKeyInfo = yield* requireApiKeyContext;
    return yield* listFunctionsHandler(
      apiKeyInfo.organizationId,
      apiKeyInfo.projectId,
      apiKeyInfo.environmentId,
      params,
    );
  });
