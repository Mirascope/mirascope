import { Effect } from "effect";

import type { CreateClawRequest, UpdateClawRequest } from "@/api/claws.schemas";

import { Analytics } from "@/analytics";
import { AuthenticatedUser } from "@/auth";
import { Database } from "@/db/database";

export * from "@/api/claws.schemas";

export const listClawsHandler = (organizationId: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.claws.findAll({
      userId: user.id,
      organizationId,
    });
  });

export const createClawHandler = (
  organizationId: string,
  payload: CreateClawRequest,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    const analytics = yield* Analytics;

    const claw = yield* db.organizations.claws.create({
      userId: user.id,
      organizationId,
      data: {
        slug: payload.slug,
        displayName: payload.name,
        description: payload.description,
      },
    });

    yield* analytics.trackEvent({
      name: "claw_created",
      properties: {
        clawId: claw.id,
        organizationId,
        userId: user.id,
      },
      distinctId: user.id,
    });

    return claw;
  });

export const getClawHandler = (organizationId: string, clawId: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.claws.findById({
      organizationId,
      clawId,
      userId: user.id,
    });
  });

export const updateClawHandler = (
  organizationId: string,
  clawId: string,
  payload: UpdateClawRequest,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.claws.update({
      organizationId,
      clawId,
      data: {
        displayName: payload.name,
        description: payload.description,
      },
      userId: user.id,
    });
  });

export const deleteClawHandler = (organizationId: string, clawId: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    const analytics = yield* Analytics;

    yield* db.organizations.claws.delete({
      organizationId,
      clawId,
      userId: user.id,
    });

    yield* analytics.trackEvent({
      name: "claw_deleted",
      properties: {
        clawId,
        organizationId,
        userId: user.id,
      },
      distinctId: user.id,
    });
  });
