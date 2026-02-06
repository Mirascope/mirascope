import { Effect } from "effect";

import type {
  AddClawMemberRequest,
  UpdateClawMemberRoleRequest,
} from "@/api/claw-memberships.schemas";

import { AuthenticatedUser } from "@/auth";
import { Database } from "@/db/database";

export * from "@/api/claw-memberships.schemas";

/**
 * Lists all members of a claw with user information.
 */
export const listClawMembersHandler = (
  organizationId: string,
  clawId: string,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.claws.memberships.findAllWithUserInfo({
      userId: user.id,
      organizationId,
      clawId,
    });
  });

/**
 * Adds a member to a claw.
 */
export const addClawMemberHandler = (
  organizationId: string,
  clawId: string,
  payload: AddClawMemberRequest,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.claws.memberships.create({
      userId: user.id,
      organizationId,
      clawId,
      data: { memberId: payload.memberId, role: payload.role },
    });
  });

/**
 * Gets a member's membership info in a claw.
 */
export const getClawMembershipHandler = (
  organizationId: string,
  clawId: string,
  memberId: string,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.claws.memberships.findById({
      userId: user.id,
      organizationId,
      clawId,
      memberId,
    });
  });

/**
 * Updates a member's role in a claw.
 */
export const updateClawMemberRoleHandler = (
  organizationId: string,
  clawId: string,
  memberId: string,
  payload: UpdateClawMemberRoleRequest,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.claws.memberships.update({
      userId: user.id,
      organizationId,
      clawId,
      memberId,
      data: { role: payload.role },
    });
  });

/**
 * Removes a member from a claw.
 */
export const removeClawMemberHandler = (
  organizationId: string,
  clawId: string,
  memberId: string,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    yield* db.organizations.claws.memberships.delete({
      userId: user.id,
      organizationId,
      clawId,
      memberId,
    });
  });
