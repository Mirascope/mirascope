import { Effect } from "effect";

import type { CreateFunctionRequest } from "@/api/functions.schemas";
import type { PublicFunction } from "@/db/schema/functions";

import { Authentication } from "@/auth";
import { Database } from "@/db/database";

export * from "@/api/functions.schemas";

// Helper to convert Date to ISO string for API response
export const toFunction = (fn: PublicFunction) => ({
  ...fn,
  createdAt: fn.createdAt?.toISOString() ?? null,
  updatedAt: fn.updatedAt?.toISOString() ?? null,
});

/**
 * Handler for listing all functions in an environment.
 * IDs are provided by the router from either API key context or path params.
 */
export const listFunctionsHandler = (
  organizationId: string,
  projectId: string,
  environmentId: string,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const { user } = yield* Authentication;

    const results =
      yield* db.organizations.projects.environments.functions.findAll({
        userId: user.id,
        organizationId,
        projectId,
        environmentId,
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
          language: payload.language,
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
 * IDs are provided by the router from either API key context or path params.
 */
export const getFunctionHandler = (
  organizationId: string,
  projectId: string,
  environmentId: string,
  functionId: string,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const { user } = yield* Authentication;

    const result =
      yield* db.organizations.projects.environments.functions.findById({
        userId: user.id,
        organizationId,
        projectId,
        environmentId,
        functionId,
      });

    return toFunction(result);
  });

/**
 * Handler for deleting a function by ID.
 * IDs are provided by the router from either API key context or path params.
 */
export const deleteFunctionHandler = (
  organizationId: string,
  projectId: string,
  environmentId: string,
  functionId: string,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const { user } = yield* Authentication;

    yield* db.organizations.projects.environments.functions.delete({
      userId: user.id,
      organizationId,
      projectId,
      environmentId,
      functionId,
    });
  });

/**
 * Handler for finding a function by its content hash.
 * IDs are provided by the router from either API key context or path params.
 */
export const findByHashHandler = (
  organizationId: string,
  projectId: string,
  environmentId: string,
  hash: string,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const { user } = yield* Authentication;

    const result =
      yield* db.organizations.projects.environments.functions.findByHash({
        userId: user.id,
        organizationId,
        projectId,
        environmentId,
        hash,
      });

    return toFunction(result);
  });
