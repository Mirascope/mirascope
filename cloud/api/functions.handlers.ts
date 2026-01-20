import { Effect } from "effect";
import { Database } from "@/db";
import { Authentication } from "@/auth";
import type { PublicFunction } from "@/db/schema/functions";
import type { CreateFunctionRequest } from "@/api/functions.schemas";

export * from "@/api/functions.schemas";

// Helper to convert Date to ISO string for API response
export const toFunction = (fn: PublicFunction) => ({
  ...fn,
  createdAt: fn.createdAt?.toISOString() ?? null,
  updatedAt: fn.updatedAt?.toISOString() ?? null,
});

/**
 * Handler for listing all functions in an environment.
 * Returns all functions accessible to the authenticated user and API key.
 */
export const listFunctionsHandler = () =>
  Effect.gen(function* () {
    const db = yield* Database;
    const { user, apiKeyInfo } = yield* Authentication.ApiKey;

    const results =
      yield* db.organizations.projects.environments.functions.findAll({
        userId: user.id,
        organizationId: apiKeyInfo.organizationId,
        projectId: apiKeyInfo.projectId,
        environmentId: apiKeyInfo.environmentId,
      });

    return {
      functions: results.map(toFunction),
      total: results.length,
    };
  });

/**
 * Handler for listing all versions of a function by name.
 * Returns functions accessible to the authenticated user and API key.
 */
export const listByNameHandler = (name: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const { user, apiKeyInfo } = yield* Authentication.ApiKey;

    const results =
      yield* db.organizations.projects.environments.functions.findByName({
        userId: user.id,
        organizationId: apiKeyInfo.organizationId,
        projectId: apiKeyInfo.projectId,
        environmentId: apiKeyInfo.environmentId,
        name,
      });

    return {
      functions: results.map(toFunction),
      total: results.length,
    };
  });

/**
 * Handler for listing the latest function version for each name.
 * Returns functions accessible to the authenticated user and API key.
 */
export const listLatestByNameHandler = () =>
  Effect.gen(function* () {
    const db = yield* Database;
    const { user, apiKeyInfo } = yield* Authentication.ApiKey;

    const results =
      yield* db.organizations.projects.environments.functions.findLatestByName({
        userId: user.id,
        organizationId: apiKeyInfo.organizationId,
        projectId: apiKeyInfo.projectId,
        environmentId: apiKeyInfo.environmentId,
      });

    return {
      functions: results.map(toFunction),
      total: results.length,
    };
  });

/**
 * Handler for creating a new function.
 * Accepts function code, signature, and metadata, and stores it in the database.
 */
export const createFunctionHandler = (payload: CreateFunctionRequest) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const { user, apiKeyInfo } = yield* Authentication.ApiKey;

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

    return toFunction(result);
  });

/**
 * Handler for retrieving a specific function by ID.
 * Returns the function if accessible to the authenticated user and API key.
 */
export const getFunctionHandler = (id: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const { user, apiKeyInfo } = yield* Authentication.ApiKey;

    const result =
      yield* db.organizations.projects.environments.functions.findById({
        userId: user.id,
        organizationId: apiKeyInfo.organizationId,
        projectId: apiKeyInfo.projectId,
        environmentId: apiKeyInfo.environmentId,
        functionId: id,
      });

    return toFunction(result);
  });

/**
 * Handler for deleting a function by ID.
 * Removes the function if accessible to the authenticated user and API key.
 */
export const deleteFunctionHandler = (id: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const { user, apiKeyInfo } = yield* Authentication.ApiKey;

    yield* db.organizations.projects.environments.functions.delete({
      userId: user.id,
      organizationId: apiKeyInfo.organizationId,
      projectId: apiKeyInfo.projectId,
      environmentId: apiKeyInfo.environmentId,
      functionId: id,
    });
  });

/**
 * Handler for deleting all function versions by name.
 * Removes all matching functions if accessible to the authenticated user and API key.
 */
export const deleteByNameHandler = (name: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const { user, apiKeyInfo } = yield* Authentication.ApiKey;

    yield* db.organizations.projects.environments.functions.deleteByName({
      userId: user.id,
      organizationId: apiKeyInfo.organizationId,
      projectId: apiKeyInfo.projectId,
      environmentId: apiKeyInfo.environmentId,
      name,
    });
  });

/**
 * Handler for finding a function by its content hash.
 * Returns the function if a matching hash is found and accessible to the authenticated user and API key.
 */
export const findByHashHandler = (hash: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const { user, apiKeyInfo } = yield* Authentication.ApiKey;

    const result =
      yield* db.organizations.projects.environments.functions.findByHash({
        userId: user.id,
        organizationId: apiKeyInfo.organizationId,
        projectId: apiKeyInfo.projectId,
        environmentId: apiKeyInfo.environmentId,
        hash,
      });

    return toFunction(result);
  });
