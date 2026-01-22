import { Effect } from "effect";
import { Database } from "@/db/database";
import { AuthenticatedUser } from "@/auth";
import type { UpdateMemberRoleRequest } from "@/api/organization-memberships.schemas";

export * from "@/api/organization-memberships.schemas";

/**
 * Lists all members of an organization with user information.
 */
export const listMembersHandler = (organizationId: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.memberships.findAllWithUserInfo({
      userId: user.id,
      organizationId,
    });
  });

/**
 * Updates a member's role in an organization.
 */
export const updateMemberRoleHandler = (
  organizationId: string,
  memberId: string,
  payload: UpdateMemberRoleRequest,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.memberships.update({
      userId: user.id,
      organizationId,
      memberId,
      data: { role: payload.role },
    });
  });

/**
 * Removes a member from an organization.
 */
export const removeMemberHandler = (organizationId: string, memberId: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    yield* db.organizations.memberships.delete({
      userId: user.id,
      organizationId,
      memberId,
    });
  });
