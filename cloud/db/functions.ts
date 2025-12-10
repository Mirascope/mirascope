import { Effect } from "effect";
import { and, eq, desc, sql } from "drizzle-orm";
import { DrizzleORM } from "@/db/client";
import { DatabaseError, NotFoundError } from "@/errors";
import {
  functions,
  type NewFunction,
  type PublicFunction,
  type DependencyInfo,
} from "@/db/schema/functions";
import { environments } from "@/db/schema/environments";
import { projects } from "@/db/schema/projects";
import type { EnvironmentContext } from "@/db/traces";

export type RegisterFunctionInput = {
  code: string;
  hash: string;
  signature: string;
  signatureHash: string;
  name: string;
  description?: string | null;
  tags?: string[] | null;
  metadata?: Record<string, string> | null;
  dependencies?: Record<string, DependencyInfo> | null;
};

export type FunctionResponse = PublicFunction & {
  isNew: boolean;
};

/**
 * Functions service for function versioning.
 *
 * Uses Effect-native DrizzleORM dependency injection.
 */
export class Functions {
  /**
   * Get environment context (environment -> project -> organization)
   */
  getEnvironmentContext(
    environmentId: string,
  ): Effect.Effect<
    EnvironmentContext,
    NotFoundError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const result = yield* Effect.tryPromise({
        try: async () => {
          return await client
            .select({
              environmentId: environments.id,
              projectId: projects.id,
              organizationId: projects.organizationId,
            })
            .from(environments)
            .innerJoin(projects, eq(environments.projectId, projects.id))
            .where(eq(environments.id, environmentId))
            .limit(1);
        },
        catch: (error) =>
          new DatabaseError({
            message: `Failed to query environment: ${error instanceof Error ? error.message : "Unknown error"}`,
          }),
      });

      const row = result[0];
      if (!row) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Environment ${environmentId} not found`,
            resource: "environment",
          }),
        );
      }

      return {
        environmentId: row.environmentId,
        projectId: row.projectId,
        organizationId: row.organizationId,
      };
    });
  }

  /**
   * Register or retrieve a function version.
   * - If hash exists in environment, return existing
   * - If new, compute version based on signature_hash history
   */
  registerOrGet(
    data: RegisterFunctionInput,
    context: EnvironmentContext,
  ): Effect.Effect<FunctionResponse, DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      return yield* Effect.tryPromise({
        try: async () => {
          // First, check if function with same hash already exists
          const existing = await client
            .select()
            .from(functions)
            .where(
              and(
                eq(functions.hash, data.hash),
                eq(functions.environmentId, context.environmentId),
              ),
            )
            .limit(1);

          if (existing[0]) {
            return {
              ...existing[0],
              isNew: false,
            };
          }

          // Compute version and insert in same transaction to prevent race conditions
          return await client.transaction(async (tx) => {
            // Get the latest version for this function name with lock
            const latestVersions = await tx
              .select({
                version: functions.version,
                signatureHash: functions.signatureHash,
              })
              .from(functions)
              .where(
                and(
                  eq(functions.name, data.name),
                  eq(functions.environmentId, context.environmentId),
                ),
              )
              .orderBy(desc(functions.createdAt))
              .limit(1)
              .for("update");

            let version: string;
            if (latestVersions.length === 0) {
              // No existing version for this name, start at 1.0
              version = "1.0";
            } else {
              const latest = latestVersions[0];
              const [major, minor] = latest.version.split(".").map(Number);

              if (latest.signatureHash !== data.signatureHash) {
                // Signature changed -> major version bump
                version = `${major + 1}.0`;
              } else {
                // Same signature, different implementation -> minor version bump
                version = `${major}.${minor + 1}`;
              }
            }

            // Insert new function within the same transaction
            const newFunction: NewFunction = {
              hash: data.hash,
              signatureHash: data.signatureHash,
              name: data.name,
              description: data.description ?? null,
              version,
              tags: data.tags ?? null,
              metadata: data.metadata ?? null,
              code: data.code,
              signature: data.signature,
              dependencies: data.dependencies ?? null,
              environmentId: context.environmentId,
              projectId: context.projectId,
              organizationId: context.organizationId,
            };

            const [inserted] = await tx
              .insert(functions)
              .values(newFunction)
              .onConflictDoNothing({
                target: [functions.hash, functions.environmentId],
              })
              .returning();

            // If conflict occurred (race condition on hash), fetch the existing one
            if (!inserted) {
              const [existingAfterConflict] = await tx
                .select()
                .from(functions)
                .where(
                  and(
                    eq(functions.hash, data.hash),
                    eq(functions.environmentId, context.environmentId),
                  ),
                )
                .limit(1);

              return {
                ...existingAfterConflict,
                isNew: false,
              };
            }

            return {
              ...inserted,
              isNew: true,
            };
          });
        },
        catch: (error) =>
          new DatabaseError({
            message: `Failed to register function: ${error instanceof Error ? error.message : "Unknown error"}`,
          }),
      });
    });
  }

  /**
   * Get function by hash within environment scope
   */
  getByHash(
    hash: string,
    environmentId: string,
  ): Effect.Effect<PublicFunction, NotFoundError | DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const result = yield* Effect.tryPromise({
        try: async () => {
          return await client
            .select()
            .from(functions)
            .where(
              and(
                eq(functions.hash, hash),
                eq(functions.environmentId, environmentId),
              ),
            )
            .limit(1);
        },
        catch: (error) =>
          new DatabaseError({
            message: `Failed to get function by hash: ${error instanceof Error ? error.message : "Unknown error"}`,
          }),
      });

      const row = result[0];
      if (!row) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Function with hash ${hash} not found`,
            resource: "function",
          }),
        );
      }

      return row;
    });
  }

  /**
   * Get function by ID
   */
  getById(
    id: string,
    environmentId: string,
  ): Effect.Effect<PublicFunction, NotFoundError | DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const result = yield* Effect.tryPromise({
        try: async () => {
          return await client
            .select()
            .from(functions)
            .where(
              and(
                eq(functions.id, id),
                eq(functions.environmentId, environmentId),
              ),
            )
            .limit(1);
        },
        catch: (error) =>
          new DatabaseError({
            message: `Failed to get function by id: ${error instanceof Error ? error.message : "Unknown error"}`,
          }),
      });

      const row = result[0];
      if (!row) {
        return yield* Effect.fail(
          new NotFoundError({
            message: `Function with id ${id} not found`,
            resource: "function",
          }),
        );
      }

      return row;
    });
  }

  /**
   * List functions with filters
   */
  list(
    environmentId: string,
    filters?: {
      name?: string;
      tags?: string[];
      limit?: number;
      offset?: number;
    },
  ): Effect.Effect<
    { functions: PublicFunction[]; total: number },
    DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      return yield* Effect.tryPromise({
        try: async () => {
          const conditions = [eq(functions.environmentId, environmentId)];

          if (filters?.name) {
            conditions.push(eq(functions.name, filters.name));
          }

          if (filters?.tags && filters.tags.length > 0) {
            // Check if all requested tags are present in the function's tags array
            conditions.push(
              sql`${functions.tags} @> ${JSON.stringify(filters.tags)}::jsonb`,
            );
          }

          const whereClause = and(...conditions);

          // Get total count
          const countResult = await client
            .select({ count: sql<number>`count(*)::int` })
            .from(functions)
            .where(whereClause);

          const total = countResult[0]?.count ?? 0;

          // Get paginated results
          let query = client
            .select()
            .from(functions)
            .where(whereClause)
            .orderBy(desc(functions.createdAt));

          if (filters?.limit) {
            query = query.limit(filters.limit) as typeof query;
          }

          if (filters?.offset) {
            query = query.offset(filters.offset) as typeof query;
          }

          const results = await query;

          return {
            functions: results,
            total,
          };
        },
        catch: (error) =>
          new DatabaseError({
            message: `Failed to list functions: ${error instanceof Error ? error.message : "Unknown error"}`,
          }),
      });
    });
  }
}
