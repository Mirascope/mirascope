import { Effect, Option } from "effect";
import { Database } from "@/db";
import { AuthenticatedUser, AuthenticatedApiKey } from "@/auth";
import { UnauthorizedError } from "@/errors";
import type { PublicFunction as DbPublicFunction } from "@/db/schema/functions";
import type { FunctionResponse as DbFunctionResponse } from "@/db/functions";
import type {
  RegisterFunctionRequest,
  FunctionResponse,
  PublicFunction,
} from "@/api/functions.schemas";

export * from "@/api/functions.schemas";

export const toPublicFunction = (fn: DbPublicFunction): PublicFunction => ({
  ...fn,
  createdAt: fn.createdAt?.toISOString() ?? null,
  updatedAt: fn.updatedAt?.toISOString() ?? null,
});

export const toFunctionResponse = (
  fn: DbFunctionResponse,
): FunctionResponse => ({
  ...fn,
  createdAt: fn.createdAt?.toISOString() ?? null,
  updatedAt: fn.updatedAt?.toISOString() ?? null,
});

export const registerFunctionHandler = (
  organizationId: string,
  projectId: string,
  environmentId: string,
  payload: RegisterFunctionRequest,
) =>
  Effect.gen(function* () {
    const user = yield* AuthenticatedUser;
    const db = yield* Database;

    const tags = payload.tags ? [...payload.tags] : null;
    const metadata = payload.metadata ? { ...payload.metadata } : null;
    const dependencies = payload.dependencies
      ? Object.fromEntries(
          Object.entries(payload.dependencies).map(([k, v]) => [
            k,
            { version: v.version, extras: v.extras ? [...v.extras] : null },
          ]),
        )
      : null;

    const result =
      yield* db.organizations.projects.environments.functions.create({
        userId: user.id,
        organizationId,
        projectId,
        environmentId,
        data: {
          code: payload.code,
          hash: payload.hash,
          signature: payload.signature,
          signatureHash: payload.signatureHash,
          name: payload.name,
          description: payload.description ?? null,
          tags,
          metadata,
          dependencies,
        },
      });

    return toFunctionResponse(result);
  });

export const getFunctionByHashHandler = (
  organizationId: string,
  projectId: string,
  environmentId: string,
  hash: string,
) =>
  Effect.gen(function* () {
    const user = yield* AuthenticatedUser;
    const db = yield* Database;

    const result =
      yield* db.organizations.projects.environments.functions.getByHash({
        userId: user.id,
        organizationId,
        projectId,
        environmentId,
        hash,
      });

    return toPublicFunction(result);
  });

export const getFunctionHandler = (
  organizationId: string,
  projectId: string,
  environmentId: string,
  id: string,
) =>
  Effect.gen(function* () {
    const user = yield* AuthenticatedUser;
    const db = yield* Database;

    const result =
      yield* db.organizations.projects.environments.functions.getById({
        userId: user.id,
        organizationId,
        projectId,
        environmentId,
        id,
      });

    return toPublicFunction(result);
  });

export const listFunctionsHandler = (
  organizationId: string,
  projectId: string,
  environmentId: string,
  params: {
    name?: string;
    tags?: string;
    limit?: number;
    offset?: number;
  },
) =>
  Effect.gen(function* () {
    const user = yield* AuthenticatedUser;
    const db = yield* Database;

    const tags = params.tags?.split(",").filter(Boolean);

    const result = yield* db.organizations.projects.environments.functions.list(
      {
        userId: user.id,
        organizationId,
        projectId,
        environmentId,
        filters: {
          name: params.name,
          tags,
          limit: params.limit,
          offset: params.offset,
        },
      },
    );

    return {
      functions: result.functions.map(toPublicFunction),
      total: result.total,
    };
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
