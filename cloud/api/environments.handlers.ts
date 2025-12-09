import { Effect } from "effect";
import { DatabaseService } from "@/db";
import { AuthenticatedUser } from "@/auth";
import type { CreateEnvironmentRequest } from "@/api/environments.schemas";

export * from "@/api/environments.schemas";

export const listEnvironmentsHandler = (projectId: string) =>
  Effect.gen(function* () {
    const db = yield* DatabaseService;
    const user = yield* AuthenticatedUser;
    return yield* db.environments.findByProject(projectId, user.id);
  });

export const createEnvironmentHandler = (
  projectId: string,
  payload: CreateEnvironmentRequest,
) =>
  Effect.gen(function* () {
    const db = yield* DatabaseService;
    const user = yield* AuthenticatedUser;
    return yield* db.environments.create(
      { name: payload.name, projectId },
      user.id,
    );
  });

export const getEnvironmentHandler = (environmentId: string) =>
  Effect.gen(function* () {
    const db = yield* DatabaseService;
    const user = yield* AuthenticatedUser;
    return yield* db.environments.findById(environmentId, user.id);
  });

export const deleteEnvironmentHandler = (environmentId: string) =>
  Effect.gen(function* () {
    const db = yield* DatabaseService;
    const user = yield* AuthenticatedUser;
    yield* db.environments.delete(environmentId, user.id);
  });
