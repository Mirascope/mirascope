/** Effect-native Functions service for function versioning. */

import { Effect } from "effect";
import { and, eq, desc, sql } from "drizzle-orm";
import {
  BaseAuthenticatedEffectService,
  type PermissionTable,
} from "@/db/base";
import { DrizzleORM } from "@/db/client";
import { ProjectMemberships } from "@/db/project-memberships";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/errors";
import {
  functions,
  type NewFunction,
  type PublicFunction,
  type DependencyInfo,
} from "@/db/schema/functions";
import type { ProjectRole } from "@/db/schema";

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

type FunctionPath =
  "organizations/:organizationId/projects/:projectId/environments/:environmentId/functions/:functionId";

export class Functions extends BaseAuthenticatedEffectService<
  FunctionResponse,
  FunctionPath,
  RegisterFunctionInput,
  never,
  ProjectRole
> {
  private readonly projectMemberships: ProjectMemberships;

  constructor(projectMemberships: ProjectMemberships) {
    super();
    this.projectMemberships = projectMemberships;
  }

  protected getResourceName(): string {
    return "function";
  }

  protected getPermissionTable(): PermissionTable<ProjectRole> {
    return {
      create: ["ADMIN", "DEVELOPER"],
      read: ["ADMIN", "DEVELOPER", "VIEWER", "ANNOTATOR"],
      update: ["ADMIN", "DEVELOPER"],
      delete: ["ADMIN"],
    };
  }

  getRole({
    userId,
    organizationId,
    projectId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId?: string;
    functionId?: string;
  }): Effect.Effect<
    ProjectRole,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return this.projectMemberships.getRole({
      userId,
      organizationId,
      projectId,
    });
  }

  create({
    userId,
    organizationId,
    projectId,
    environmentId,
    data,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    data: RegisterFunctionInput;
  }): Effect.Effect<
    FunctionResponse,
    AlreadyExistsError | NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({
        userId,
        action: "create",
        organizationId,
        projectId,
        environmentId,
        functionId: "",
      });

      return yield* this.registerOrGet({
        environmentId,
        projectId,
        organizationId,
        data,
      });
    });
  }

  findAll({
    userId,
    organizationId,
    projectId,
    environmentId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
  }): Effect.Effect<
    FunctionResponse[],
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        functionId: "",
      });

      const result = yield* this.listInternal(environmentId);
      return result.functions.map((f) => ({ ...f, isNew: false }));
    });
  }

  findById({
    userId,
    organizationId,
    projectId,
    environmentId,
    functionId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    functionId: string;
  }): Effect.Effect<
    FunctionResponse,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        functionId,
      });

      const fn = yield* this.getByIdInternal(functionId, environmentId);
      return { ...fn, isNew: false };
    });
  }

  update({
    userId,
    organizationId,
    projectId,
    environmentId,
    functionId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    functionId: string;
    data: never;
  }): Effect.Effect<
    FunctionResponse,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({
        userId,
        action: "update",
        organizationId,
        projectId,
        environmentId,
        functionId,
      });

      return yield* Effect.fail(
        new PermissionDeniedError({
          message:
            "Functions are immutable. Register a new version instead of updating.",
          resource: "function",
        }),
      );
    });
  }

  delete({
    userId,
    organizationId,
    projectId,
    environmentId,
    functionId,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    functionId: string;
  }): Effect.Effect<
    void,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({
        userId,
        action: "delete",
        organizationId,
        projectId,
        environmentId,
        functionId,
      });

      const client = yield* DrizzleORM;

      yield* this.getByIdInternal(functionId, environmentId);

      yield* client
        .delete(functions)
        .where(
          and(
            eq(functions.id, functionId),
            eq(functions.environmentId, environmentId),
          ),
        )
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to delete function",
                cause: e,
              }),
          ),
        );
    });
  }

  private registerOrGet({
    organizationId,
    projectId,
    environmentId,
    data,
  }: {
    organizationId: string;
    projectId: string;
    environmentId: string;
    data: RegisterFunctionInput;
  }): Effect.Effect<FunctionResponse, DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const existing: PublicFunction[] = yield* client
        .select()
        .from(functions)
        .where(
          and(
            eq(functions.hash, data.hash),
            eq(functions.environmentId, environmentId),
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to check existing function",
                cause: e,
              }),
          ),
        );

      const [existingFunction] = existing;
      if (existingFunction) {
        return {
          ...existingFunction,
          isNew: false,
        };
      }

      return yield* client.withTransaction(
        Effect.gen(function* () {
          const latestVersions: { version: string; signatureHash: string }[] =
            yield* client
              .select({
                version: functions.version,
                signatureHash: functions.signatureHash,
              })
              .from(functions)
              .where(
                and(
                  eq(functions.name, data.name),
                  eq(functions.environmentId, environmentId),
                ),
              )
              .orderBy(desc(functions.createdAt))
              .limit(1)
              .for("update")
              .pipe(
                Effect.mapError(
                  (e) =>
                    new DatabaseError({
                      message: "Failed to get latest version",
                      cause: e,
                    }),
                ),
              );

          let version: string;
          const [latest] = latestVersions;
          if (!latest) {
            version = "1.0";
          } else {
            const [major, minor] = latest.version.split(".").map(Number);

            if (latest.signatureHash !== data.signatureHash) {
              version = `${major + 1}.0`;
            } else {
              version = `${major}.${minor + 1}`;
            }
          }

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
            environmentId,
            projectId,
            organizationId,
          };

          const insertResult: PublicFunction[] = yield* client
            .insert(functions)
            .values(newFunction)
            .onConflictDoNothing({
              target: [functions.hash, functions.environmentId],
            })
            .returning()
            .pipe(
              Effect.mapError(
                (e) =>
                  new DatabaseError({
                    message: "Failed to insert function",
                    cause: e,
                  }),
              ),
            );

          const [inserted] = insertResult;

          if (!inserted) {
            const existingAfterConflict: PublicFunction[] = yield* client
              .select()
              .from(functions)
              .where(
                and(
                  eq(functions.hash, data.hash),
                  eq(functions.environmentId, environmentId),
                ),
              )
              .limit(1)
              .pipe(
                Effect.mapError(
                  (e) =>
                    new DatabaseError({
                      message: "Failed to fetch after conflict",
                      cause: e,
                    }),
                ),
              );

            const [existingAfterConflictRow] = existingAfterConflict;
            return {
              ...existingAfterConflictRow,
              isNew: false,
            };
          }

          return {
            ...inserted,
            isNew: true,
          };
        }),
      );
    });
  }

  getByHash({
    userId,
    organizationId,
    projectId,
    environmentId,
    hash,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    hash: string;
  }): Effect.Effect<
    PublicFunction,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        functionId: "",
      });

      return yield* this.getByHashInternal(hash, environmentId);
    });
  }

  private getByHashInternal(
    hash: string,
    environmentId: string,
  ): Effect.Effect<PublicFunction, NotFoundError | DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const result: PublicFunction[] = yield* client
        .select()
        .from(functions)
        .where(
          and(
            eq(functions.hash, hash),
            eq(functions.environmentId, environmentId),
          ),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to get function by hash",
                cause: e,
              }),
          ),
        );

      const [row] = result;
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

  getById({
    userId,
    organizationId,
    projectId,
    environmentId,
    id,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    id: string;
  }): Effect.Effect<
    PublicFunction,
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        functionId: "",
      });

      return yield* this.getByIdInternal(id, environmentId);
    });
  }

  private getByIdInternal(
    id: string,
    environmentId: string,
  ): Effect.Effect<PublicFunction, NotFoundError | DatabaseError, DrizzleORM> {
    return Effect.gen(function* () {
      const client = yield* DrizzleORM;

      const result: PublicFunction[] = yield* client
        .select()
        .from(functions)
        .where(
          and(eq(functions.id, id), eq(functions.environmentId, environmentId)),
        )
        .limit(1)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to get function by id",
                cause: e,
              }),
          ),
        );

      const [row] = result;
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

  list({
    userId,
    organizationId,
    projectId,
    environmentId,
    filters,
  }: {
    userId: string;
    organizationId: string;
    projectId: string;
    environmentId: string;
    filters?: {
      name?: string;
      tags?: string[];
      limit?: number;
      offset?: number;
    };
  }): Effect.Effect<
    { functions: PublicFunction[]; total: number },
    NotFoundError | PermissionDeniedError | DatabaseError,
    DrizzleORM
  > {
    return Effect.gen(this, function* () {
      yield* this.authorize({
        userId,
        action: "read",
        organizationId,
        projectId,
        environmentId,
        functionId: "",
      });

      return yield* this.listInternal(environmentId, filters);
    });
  }

  private listInternal(
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

      const conditions = [eq(functions.environmentId, environmentId)];

      if (filters?.name) {
        conditions.push(eq(functions.name, filters.name));
      }

      if (filters?.tags && filters.tags.length > 0) {
        conditions.push(
          sql`${functions.tags} @> ${JSON.stringify(filters.tags)}::jsonb`,
        );
      }

      const whereClause = and(...conditions);

      const countResult: { count: number }[] = yield* client
        .select({ count: sql<number>`count(*)::int` })
        .from(functions)
        .where(whereClause)
        .pipe(
          Effect.mapError(
            (e) =>
              new DatabaseError({
                message: "Failed to count functions",
                cause: e,
              }),
          ),
        );

      const total = countResult[0].count;

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

      const results: PublicFunction[] = yield* query.pipe(
        Effect.mapError(
          (e) =>
            new DatabaseError({
              message: "Failed to list functions",
              cause: e,
            }),
        ),
      );

      return {
        functions: results,
        total,
      };
    });
  }
}
