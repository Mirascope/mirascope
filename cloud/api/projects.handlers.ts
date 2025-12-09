import { Effect } from "effect";
import { DatabaseService } from "@/db";
import { AuthenticatedUser } from "@/auth";
import type {
  CreateProjectRequest,
  UpdateProjectRequest,
} from "@/api/projects.schemas";

export * from "@/api/projects.schemas";

export const listProjectsHandler = () =>
  Effect.gen(function* () {
    const db = yield* DatabaseService;
    const user = yield* AuthenticatedUser;
    return yield* db.projects.findAll({ userId: user.id });
  });

export const createProjectHandler = (payload: CreateProjectRequest) =>
  Effect.gen(function* () {
    const db = yield* DatabaseService;
    const user = yield* AuthenticatedUser;
    return yield* db.projects.create({
      data: {
        name: payload.name,
        userOwnerId: payload.userOwnerId,
        orgOwnerId: payload.orgOwnerId,
      },
      userId: user.id,
    });
  });

export const getProjectHandler = (projectId: string) =>
  Effect.gen(function* () {
    const db = yield* DatabaseService;
    const user = yield* AuthenticatedUser;
    return yield* db.projects.findById({ id: projectId, userId: user.id });
  });

export const updateProjectHandler = (
  projectId: string,
  payload: UpdateProjectRequest,
) =>
  Effect.gen(function* () {
    const db = yield* DatabaseService;
    const user = yield* AuthenticatedUser;
    return yield* db.projects.update({
      id: projectId,
      data: payload,
      userId: user.id,
    });
  });

export const deleteProjectHandler = (projectId: string) =>
  Effect.gen(function* () {
    const db = yield* DatabaseService;
    const user = yield* AuthenticatedUser;
    yield* db.projects.delete({ id: projectId, userId: user.id });
  });
