import { Effect } from "effect";
import { eq } from "drizzle-orm";
import type { PostgresJsDatabase } from "drizzle-orm/postgres-js";
import {
  BaseService,
  BaseAuthenticatedService,
  type PermissionTable,
} from "@/db/services/base";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/db/errors";
import { isUniqueConstraintError } from "@/db/utils";
import {
  environments,
  projects,
  organizationMemberships,
  type NewEnvironment,
  type PublicEnvironment,
  type Role,
} from "@/db/schema";
import type * as schema from "@/db/schema";
import type { ProjectService } from "@/db/services/projects";

class EnvironmentBaseService extends BaseService<
  PublicEnvironment,
  string,
  typeof environments
> {
  protected getTable() {
    return environments;
  }

  protected getResourceName() {
    return "environment";
  }

  protected getPublicFields() {
    return {
      id: environments.id,
      name: environments.name,
      projectId: environments.projectId,
    };
  }
}

export class EnvironmentService extends BaseAuthenticatedService<
  PublicEnvironment,
  string,
  typeof environments,
  NewEnvironment,
  Role
> {
  private readonly projectService: ProjectService;

  constructor(
    db: PostgresJsDatabase<typeof schema>,
    projectService: ProjectService,
  ) {
    super(db);
    this.projectService = projectService;
  }

  protected initializeBaseService() {
    return new EnvironmentBaseService(this.db);
  }

  protected getPermissionTable(): PermissionTable<Role> {
    return {
      create: ["OWNER", "ADMIN", "DEVELOPER"],
      read: ["OWNER", "ADMIN", "DEVELOPER", "ANNOTATOR"],
      update: ["OWNER", "ADMIN", "DEVELOPER"],
      delete: ["OWNER", "ADMIN"],
    };
  }

  /**
   * Get the user's role for an environment by looking up the environment's project.
   * Delegates to ProjectService.getRole for the actual permission check.
   */
  getRole({
    id,
    userId,
  }: {
    id: string;
    userId: string;
  }): Effect.Effect<Role, NotFoundError | DatabaseError> {
    return Effect.gen(this, function* () {
      const environment = yield* this.baseService.findById({ id });
      return yield* this.projectService.getRole({
        id: environment.projectId,
        userId,
      });
    });
  }

  create({
    data,
    userId,
  }: {
    data: NewEnvironment;
    userId: string;
  }): Effect.Effect<
    PublicEnvironment,
    AlreadyExistsError | NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      // Check permission on the parent project
      const role = yield* this.projectService.getRole({
        id: data.projectId,
        userId,
      });
      yield* this.verifyPermission(role, "create");

      return yield* Effect.tryPromise({
        try: async () => {
          const [result] = await this.db
            .insert(environments)
            .values({
              name: data.name,
              projectId: data.projectId,
            })
            .returning({
              id: environments.id,
              name: environments.name,
              projectId: environments.projectId,
            });
          return result;
        },
        catch: (error) => {
          if (isUniqueConstraintError(error)) {
            return new AlreadyExistsError({
              message: `An environment with name "${data.name}" already exists in this project`,
              resource: this.baseService.resourceName,
            });
          }
          return new DatabaseError({
            message: "Failed to create environment",
            cause: error,
          });
        },
      });
    });
  }

  findAll({
    userId,
  }: {
    userId: string;
  }): Effect.Effect<PublicEnvironment[], DatabaseError> {
    return Effect.tryPromise({
      try: async () => {
        return await this.db
          .select({
            id: environments.id,
            name: environments.name,
            projectId: environments.projectId,
          })
          .from(environments)
          .innerJoin(projects, eq(environments.projectId, projects.id))
          .innerJoin(
            organizationMemberships,
            eq(projects.organizationId, organizationMemberships.organizationId),
          )
          .where(eq(organizationMemberships.userId, userId));
      },
      catch: (error) =>
        new DatabaseError({
          message: "Failed to get user environments",
          cause: error,
        }),
    });
  }

  findByProject({
    projectId,
    userId,
  }: {
    projectId: string;
    userId: string;
  }): Effect.Effect<
    PublicEnvironment[],
    NotFoundError | PermissionDeniedError | DatabaseError
  > {
    return Effect.gen(this, function* () {
      const role = yield* this.projectService.getRole({
        id: projectId,
        userId,
      });
      yield* this.verifyPermission(role, "read");

      return yield* Effect.tryPromise({
        try: async () => {
          return await this.db
            .select({
              id: environments.id,
              name: environments.name,
              projectId: environments.projectId,
            })
            .from(environments)
            .where(eq(environments.projectId, projectId));
        },
        catch: (error) =>
          new DatabaseError({
            message: "Failed to get project environments",
            cause: error,
          }),
      });
    });
  }
}
