import { Effect } from "effect";
import { Database } from "@/db";
import {
  UnauthorizedError,
  NotFoundError,
  PermissionDeniedError,
  DatabaseError,
  AlreadyExistsError,
} from "@/errors";
import { requireApiKeyAuth } from "@/auth";
import type { PublicFunction as DbPublicFunction } from "@/db/schema/functions";
import type { FunctionResponse as DbFunctionResponse } from "@/db/functions";
import type {
  RegisterFunctionRequest,
  FunctionResponse,
  PublicFunction,
  ListFunctionsResponse,
} from "@/api/functions.schemas";

export * from "@/api/functions.schemas";

const toPublicFunction = (fn: DbPublicFunction): PublicFunction => ({
  ...fn,
  createdAt: fn.createdAt?.toISOString() ?? null,
  updatedAt: fn.updatedAt?.toISOString() ?? null,
});

const toFunctionResponse = (fn: DbFunctionResponse): FunctionResponse => ({
  ...fn,
  createdAt: fn.createdAt?.toISOString() ?? null,
  updatedAt: fn.updatedAt?.toISOString() ?? null,
});

export const registerFunctionHandler = (
  payload: RegisterFunctionRequest,
): Effect.Effect<
  FunctionResponse,
  | UnauthorizedError
  | NotFoundError
  | PermissionDeniedError
  | DatabaseError
  | AlreadyExistsError,
  Database
> =>
  Effect.gen(function* () {
    const apiKeyInfo = yield* requireApiKeyAuth;
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

    const result = yield* db.functions.create({
      userId: apiKeyInfo.ownerId,
      organizationId: apiKeyInfo.organizationId,
      projectId: apiKeyInfo.projectId,
      environmentId: apiKeyInfo.environmentId,
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
  hash: string,
): Effect.Effect<
  PublicFunction,
  UnauthorizedError | NotFoundError | PermissionDeniedError | DatabaseError,
  Database
> =>
  Effect.gen(function* () {
    const apiKeyInfo = yield* requireApiKeyAuth;
    const db = yield* Database;

    const result = yield* db.functions.getByHash({
      userId: apiKeyInfo.ownerId,
      organizationId: apiKeyInfo.organizationId,
      projectId: apiKeyInfo.projectId,
      environmentId: apiKeyInfo.environmentId,
      hash,
    });

    return toPublicFunction(result);
  });

export const getFunctionHandler = (
  id: string,
): Effect.Effect<
  PublicFunction,
  UnauthorizedError | NotFoundError | PermissionDeniedError | DatabaseError,
  Database
> =>
  Effect.gen(function* () {
    const apiKeyInfo = yield* requireApiKeyAuth;
    const db = yield* Database;

    const result = yield* db.functions.getById({
      userId: apiKeyInfo.ownerId,
      organizationId: apiKeyInfo.organizationId,
      projectId: apiKeyInfo.projectId,
      environmentId: apiKeyInfo.environmentId,
      id,
    });

    return toPublicFunction(result);
  });

export const listFunctionsHandler = (params: {
  name?: string;
  tags?: string;
  limit?: number;
  offset?: number;
}): Effect.Effect<
  ListFunctionsResponse,
  UnauthorizedError | NotFoundError | PermissionDeniedError | DatabaseError,
  Database
> =>
  Effect.gen(function* () {
    const apiKeyInfo = yield* requireApiKeyAuth;
    const db = yield* Database;

    const tags = params.tags?.split(",").filter(Boolean);

    const result = yield* db.functions.list({
      userId: apiKeyInfo.ownerId,
      organizationId: apiKeyInfo.organizationId,
      projectId: apiKeyInfo.projectId,
      environmentId: apiKeyInfo.environmentId,
      filters: {
        name: params.name,
        tags,
        limit: params.limit,
        offset: params.offset,
      },
    });

    return {
      functions: result.functions.map(toPublicFunction),
      total: result.total,
    };
  });
