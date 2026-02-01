import { Effect } from "effect";

import type {
  CreateEnvironmentRequest,
  EnvironmentAnalyticsRequest,
  UpdateEnvironmentRequest,
} from "@/api/environments.schemas";

import { AuthenticatedUser } from "@/auth";
import { ClickHouseSearch } from "@/db/clickhouse/search";
import { Database } from "@/db/database";

export * from "@/api/environments.schemas";

export const listEnvironmentsHandler = (
  organizationId: string,
  projectId: string,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.projects.environments.findAll({
      userId: user.id,
      organizationId,
      projectId,
    });
  });

export const createEnvironmentHandler = (
  organizationId: string,
  projectId: string,
  payload: CreateEnvironmentRequest,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.projects.environments.create({
      userId: user.id,
      organizationId,
      projectId,
      data: { name: payload.name, slug: payload.slug },
    });
  });

export const getEnvironmentHandler = (
  organizationId: string,
  projectId: string,
  environmentId: string,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.projects.environments.findById({
      userId: user.id,
      organizationId,
      projectId,
      environmentId,
    });
  });

export const updateEnvironmentHandler = (
  organizationId: string,
  projectId: string,
  environmentId: string,
  payload: UpdateEnvironmentRequest,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.projects.environments.update({
      userId: user.id,
      organizationId,
      projectId,
      environmentId,
      data: payload,
    });
  });

export const deleteEnvironmentHandler = (
  organizationId: string,
  projectId: string,
  environmentId: string,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    yield* db.organizations.projects.environments.delete({
      userId: user.id,
      organizationId,
      projectId,
      environmentId,
    });
  });

export const getEnvironmentAnalyticsHandler = (
  organizationId: string,
  projectId: string,
  environmentId: string,
  params: EnvironmentAnalyticsRequest,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;

    // Verify user has access to this environment
    yield* db.organizations.projects.environments.findById({
      userId: user.id,
      organizationId,
      projectId,
      environmentId,
    });

    // Query ClickHouse for analytics
    const searchService = yield* ClickHouseSearch;
    return yield* searchService.getAnalyticsSummary({
      environmentId,
      startTime: new Date(params.startTime),
      endTime: new Date(params.endTime),
    });
  });
