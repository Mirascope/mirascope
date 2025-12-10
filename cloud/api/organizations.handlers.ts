import { Effect } from "effect";
import { DatabaseService } from "@/db";
import { AuthenticatedUser } from "@/auth";
import type {
  CreateOrganizationRequest,
  UpdateOrganizationRequest,
} from "@/api/organizations.schemas";

export * from "@/api/organizations.schemas";

export const listOrganizationsHandler = Effect.gen(function* () {
  const db = yield* DatabaseService;
  const user = yield* AuthenticatedUser;
  return yield* db.organizations.findAll({ userId: user.id });
});

export const createOrganizationHandler = (payload: CreateOrganizationRequest) =>
  Effect.gen(function* () {
    const db = yield* DatabaseService;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.create({
      data: { name: payload.name },
      userId: user.id,
    });
  });

export const getOrganizationHandler = (id: string) =>
  Effect.gen(function* () {
    const db = yield* DatabaseService;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.findById({ id, userId: user.id });
  });

export const updateOrganizationHandler = (
  id: string,
  payload: UpdateOrganizationRequest,
) =>
  Effect.gen(function* () {
    const db = yield* DatabaseService;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.update({
      id,
      data: { name: payload.name },
      userId: user.id,
    });
  });

export const deleteOrganizationHandler = (id: string) =>
  Effect.gen(function* () {
    const db = yield* DatabaseService;
    const user = yield* AuthenticatedUser;
    yield* db.organizations.delete({ id, userId: user.id });
  });
