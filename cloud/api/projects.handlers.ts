import { Effect } from "effect";
import { DatabaseService } from "@/db";
import { AuthenticatedUser } from "@/auth";
import type {
  CreateProjectRequest,
  UpdateProjectRequest,
} from "@/api/projects.schemas";

export * from "@/api/projects.schemas";

export const listProjectsHandler = (organizationId: string) =>
  Effect.gen(function* () {
    const db = yield* DatabaseService;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.projects.findAll({
      userId: user.id,
      organizationId,
    });
  });

export const createProjectHandler = (
  organizationId: string,
  payload: CreateProjectRequest,
) =>
  Effect.gen(function* () {
    const db = yield* DatabaseService;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.projects.create({
      organizationId,
      data: { name: payload.name },
      userId: user.id,
    });
  });

export const getProjectHandler = (organizationId: string, projectId: string) =>
  Effect.gen(function* () {
    const db = yield* DatabaseService;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.projects.findById({
      organizationId,
      projectId,
      userId: user.id,
    });
  });

export const updateProjectHandler = (
  organizationId: string,
  projectId: string,
  payload: UpdateProjectRequest,
) =>
  Effect.gen(function* () {
    const db = yield* DatabaseService;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.projects.update({
      organizationId,
      projectId,
      data: payload,
      userId: user.id,
    });
  });

export const deleteProjectHandler = (
  organizationId: string,
  projectId: string,
) =>
  Effect.gen(function* () {
    const db = yield* DatabaseService;
    const user = yield* AuthenticatedUser;
    yield* db.organizations.projects.delete({
      organizationId,
      projectId,
      userId: user.id,
    });
  });
