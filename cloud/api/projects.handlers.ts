import { Effect } from "effect";
import { Database } from "@/db";
import { AuthenticatedUser } from "@/auth";
import { Analytics } from "@/analytics";
import type {
  CreateProjectRequest,
  UpdateProjectRequest,
} from "@/api/projects.schemas";

export * from "@/api/projects.schemas";

export const listProjectsHandler = (organizationId: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
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
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    const analytics = yield* Analytics;

    const project = yield* db.organizations.projects.create({
      organizationId,
      data: { name: payload.name, slug: payload.slug },
      userId: user.id,
    });

    yield* analytics.trackEvent({
      name: "project_created",
      properties: {
        projectId: project.id,
        projectName: project.name,
        organizationId,
        userId: user.id,
      },
      distinctId: user.id,
    });

    return project;
  });

export const getProjectHandler = (organizationId: string, projectId: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
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
    const db = yield* Database;
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
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    const analytics = yield* Analytics;

    yield* db.organizations.projects.delete({
      organizationId,
      projectId,
      userId: user.id,
    });

    yield* analytics.trackEvent({
      name: "project_deleted",
      properties: {
        projectId,
        organizationId,
        userId: user.id,
      },
      distinctId: user.id,
    });
  });
