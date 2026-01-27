import { Effect } from "effect";
import { Database } from "@/db/database";
import { AuthenticatedUser } from "@/auth";
import type {
  AddProjectMemberRequest,
  UpdateProjectMemberRoleRequest,
} from "@/api/project-memberships.schemas";

export * from "@/api/project-memberships.schemas";

/**
 * Lists all members of a project with user information.
 */
export const listProjectMembersHandler = (
  organizationId: string,
  projectId: string,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.projects.memberships.findAllWithUserInfo({
      userId: user.id,
      organizationId,
      projectId,
    });
  });

/**
 * Adds a member to a project.
 */
export const addProjectMemberHandler = (
  organizationId: string,
  projectId: string,
  payload: AddProjectMemberRequest,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.projects.memberships.create({
      userId: user.id,
      organizationId,
      projectId,
      data: { memberId: payload.memberId, role: payload.role },
    });
  });

/**
 * Gets a member's membership info in a project.
 */
export const getProjectMembershipHandler = (
  organizationId: string,
  projectId: string,
  memberId: string,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.projects.memberships.findById({
      userId: user.id,
      organizationId,
      projectId,
      memberId,
    });
  });

/**
 * Updates a member's role in a project.
 */
export const updateProjectMemberRoleHandler = (
  organizationId: string,
  projectId: string,
  memberId: string,
  payload: UpdateProjectMemberRoleRequest,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.projects.memberships.update({
      userId: user.id,
      organizationId,
      projectId,
      memberId,
      data: { role: payload.role },
    });
  });

/**
 * Removes a member from a project.
 */
export const removeProjectMemberHandler = (
  organizationId: string,
  projectId: string,
  memberId: string,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    yield* db.organizations.projects.memberships.delete({
      userId: user.id,
      organizationId,
      projectId,
      memberId,
    });
  });
