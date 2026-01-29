import { Effect } from "effect";

import type {
  CreateInvitationRequest,
  AcceptInvitationRequest,
} from "@/api/organization-invitations.schemas";

import { AuthenticatedUser } from "@/auth";
import { Database } from "@/db/database";
import { Emails } from "@/emails";
import { renderEmailTemplate } from "@/emails/render";
import { InvitationEmail } from "@/emails/templates/invitation";
import { ImmutableResourceError } from "@/errors";
import { Settings } from "@/settings";

export * from "@/api/organization-invitations.schemas";

// =============================================================================
// Private Utilities
// =============================================================================

/**
 * Builds the invitation acceptance URL with the given token.
 *
 * @param siteUrl - The base URL from Settings
 * @param token - The invitation token
 * @returns The full URL for accepting the invitation
 */
function buildAcceptUrl(siteUrl: string, token: string): string {
  return `${siteUrl}/invitations/accept?token=${token}`;
}

/**
 * Builds the "from" address for invitation emails.
 *
 * Uses the sender's name if available, otherwise falls back to email.
 * Format: "Sender Name <sender@example.com>"
 *
 * @param senderName - The sender's name (may be null)
 * @param senderEmail - The sender's email address
 * @returns Formatted email address for the "from" field
 */
function buildFromAddress(
  senderName: string | null,
  senderEmail: string,
): string {
  const fromName = senderName || senderEmail;
  return `${fromName} <${senderEmail}>`;
}

// =============================================================================
// Handlers
// =============================================================================

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
    const emails = yield* Emails;
    const settings = yield* Settings;

    const invitationWithMetadata = yield* db.organizations.invitations.create({
      userId: user.id,
      organizationId,
      data: {
        recipientEmail: payload.recipientEmail,
        role: payload.role,
      },
    });

    // Send invitation email
    const acceptUrl = buildAcceptUrl(
      settings.siteUrl,
      invitationWithMetadata.token,
    );
    const fromAddress = buildFromAddress(
      invitationWithMetadata.senderName,
      invitationWithMetadata.senderEmail,
    );

    const htmlContent = yield* renderEmailTemplate(
      InvitationEmail,
      {
        senderName: invitationWithMetadata.senderName || "A team member",
        organizationName: invitationWithMetadata.organizationName,
        recipientEmail: invitationWithMetadata.recipientEmail,
        role: invitationWithMetadata.role,
        acceptUrl,
        expiresAt: invitationWithMetadata.expiresAt,
      },
      { email: invitationWithMetadata.recipientEmail },
    );

    // Only send email if rendering succeeded
    if (htmlContent !== null) {
      yield* emails
        .send({
          from: fromAddress,
          replyTo: invitationWithMetadata.senderEmail,
          to: invitationWithMetadata.recipientEmail,
          subject: `You're invited to join ${invitationWithMetadata.organizationName} on Mirascope`,
          html: htmlContent,
        })
        .pipe(
          Emails.DefaultRetries(
            `Failed to send invitation email to ${invitationWithMetadata.recipientEmail}`,
          ),
        );
    }

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
    const emails = yield* Emails;
    const settings = yield* Settings;

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

    // Send invitation email
    const acceptUrl = buildAcceptUrl(
      settings.siteUrl,
      invitationWithMetadata.token,
    );
    const fromAddress = buildFromAddress(
      invitationWithMetadata.senderName,
      invitationWithMetadata.senderEmail,
    );

    const htmlContent = yield* renderEmailTemplate(
      InvitationEmail,
      {
        senderName: invitationWithMetadata.senderName || "A team member",
        organizationName: invitationWithMetadata.organizationName,
        recipientEmail: invitationWithMetadata.recipientEmail,
        role: invitationWithMetadata.role,
        acceptUrl,
        expiresAt: invitationWithMetadata.expiresAt,
      },
      { email: invitationWithMetadata.recipientEmail },
    );

    // Only send email if rendering succeeded
    if (htmlContent !== null) {
      yield* emails
        .send({
          from: fromAddress,
          replyTo: invitationWithMetadata.senderEmail,
          to: invitationWithMetadata.recipientEmail,
          subject: `You're invited to join ${invitationWithMetadata.organizationName} on Mirascope`,
          html: htmlContent,
        })
        .pipe(
          Emails.DefaultRetries(
            `Failed to resend invitation email to ${invitationWithMetadata.recipientEmail}`,
          ),
        );
    }

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
