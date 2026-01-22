import { Effect } from "effect";
import { Database } from "@/db/database";
import { AuthenticatedUser } from "@/auth";
import type { PublicTag } from "@/db/schema";
import type { CreateTagRequest, UpdateTagRequest } from "@/api/tags.schemas";

export * from "@/api/tags.schemas";

export const toTag = (tag: PublicTag) => ({
  ...tag,
  createdAt: tag.createdAt?.toISOString() ?? null,
  updatedAt: tag.updatedAt?.toISOString() ?? null,
});

/**
 * Handler for listing tags in a project.
 */
export const listTagsHandler = (organizationId: string, projectId: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;

    const results = yield* db.organizations.projects.tags.findAll({
      userId: user.id,
      organizationId,
      projectId,
    });

    return {
      tags: results.map(toTag),
      total: results.length,
    };
  });

/**
 * Handler for creating a tag in a project.
 */
export const createTagHandler = (
  organizationId: string,
  projectId: string,
  payload: CreateTagRequest,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;

    const result = yield* db.organizations.projects.tags.create({
      userId: user.id,
      organizationId,
      projectId,
      data: { name: payload.name },
    });

    return toTag(result);
  });

/**
 * Handler for retrieving a tag by ID in a project.
 */
export const getTagHandler = (
  organizationId: string,
  projectId: string,
  tagId: string,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;

    const result = yield* db.organizations.projects.tags.findById({
      userId: user.id,
      organizationId,
      projectId,
      tagId,
    });

    return toTag(result);
  });

/**
 * Handler for updating a tag in a project.
 */
export const updateTagHandler = (
  organizationId: string,
  projectId: string,
  tagId: string,
  payload: UpdateTagRequest,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;

    const result = yield* db.organizations.projects.tags.update({
      userId: user.id,
      organizationId,
      projectId,
      tagId,
      data: { name: payload.name },
    });

    return toTag(result);
  });

/**
 * Handler for deleting a tag in a project.
 */
export const deleteTagHandler = (
  organizationId: string,
  projectId: string,
  tagId: string,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;

    yield* db.organizations.projects.tags.delete({
      userId: user.id,
      organizationId,
      projectId,
      tagId,
    });
  });
