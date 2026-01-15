import { Effect } from "effect";
import { Database } from "@/db";
import { AuthenticatedUser } from "@/auth";
import { ImmutableResourceError } from "@/errors";
import type {
  CreateInvitationRequest,
  AcceptInvitationRequest,
} from "@/api/organization-invitations.schemas";

export * from "@/api/organization-invitations.schemas";

export const listInvitationsHandler = (organizationId: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.invitations.findAll({
      userId: user.id,
      organizationId,
    });
  });

export const createInvitationHandler = (
  organizationId: string,
  payload: CreateInvitationRequest,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;

    const invitationWithMetadata = yield* db.organizations.invitations.create({
      userId: user.id,
      organizationId,
      data: {
        recipientEmail: payload.recipientEmail,
        role: payload.role,
      },
    });

    // TODO: Send email using invitationWithMetadata (includes token, organizationName, senderName, etc.)
    // This will be implemented in a future PR with the email service integration

    // Return invitation without token and metadata (security)
    return {
      id: invitationWithMetadata.id,
      organizationId: invitationWithMetadata.organizationId,
      senderId: invitationWithMetadata.senderId,
      recipientEmail: invitationWithMetadata.recipientEmail,
      role: invitationWithMetadata.role,
      status: invitationWithMetadata.status,
      expiresAt: invitationWithMetadata.expiresAt,
      createdAt: invitationWithMetadata.createdAt,
      updatedAt: invitationWithMetadata.updatedAt,
      acceptedAt: invitationWithMetadata.acceptedAt,
      revokedAt: invitationWithMetadata.revokedAt,
    };
  });

export const getInvitationHandler = (
  organizationId: string,
  invitationId: string,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.invitations.findById({
      userId: user.id,
      organizationId,
      invitationId,
    });
  });

export const resendInvitationHandler = (
  organizationId: string,
  invitationId: string,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;

    // Get invitation with metadata (includes token)
    const invitationWithMetadata =
      yield* db.organizations.invitations.getWithMetadata({
        userId: user.id,
        organizationId,
        invitationId,
      });

    // Check if invitation is still pending
    if (invitationWithMetadata.status !== "pending") {
      return yield* Effect.fail(
        new ImmutableResourceError({
          message: `Cannot resend invitation with status '${invitationWithMetadata.status}'`,
        }),
      );
    }

    // Check if invitation is expired
    if (new Date() > invitationWithMetadata.expiresAt) {
      return yield* Effect.fail(
        new ImmutableResourceError({
          message: "Cannot resend expired invitation",
        }),
      );
    }

    // TODO: Send email using invitationWithMetadata (includes token, organizationName, senderName, etc.)
    // This will be implemented in a future PR with the email service integration

    // For now, just return void to indicate success
    return;
  });

export const revokeInvitationHandler = (
  organizationId: string,
  invitationId: string,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    yield* db.organizations.invitations.revoke({
      userId: user.id,
      organizationId,
      invitationId,
    });
  });

export const acceptInvitationHandler = (payload: AcceptInvitationRequest) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.invitations.accept({
      token: payload.token,
      acceptingUserId: user.id,
    });
  });
