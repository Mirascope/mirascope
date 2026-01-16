import { Effect, Schema } from "effect";
import { ParseError } from "effect/ParseResult";
import { describe, it, expect, assert, TestApiContext } from "@/tests/api";
import { vi } from "vitest";
import { TestOrganizationFixture } from "@/tests/db";
import {
  CreateInvitationRequestSchema,
  AcceptInvitationRequestSchema,
} from "@/api/organization-invitations.schemas";
import type { PublicOrganizationInvitation } from "@/db/schema";
import { Database } from "@/db";
import { DrizzleORM } from "@/db/client";
import { organizationInvitations } from "@/db/schema";
import { eq } from "drizzle-orm";
import {
  AlreadyExistsError,
  ImmutableResourceError,
  NotFoundError,
} from "@/errors";
import { AuthenticatedUser } from "@/auth";
import {
  resendInvitationHandler,
  acceptInvitationHandler,
  createInvitationHandler,
} from "@/api/organization-invitations.handlers";

describe("CreateInvitationRequestSchema validation", () => {
  it("rejects invalid email format", () => {
    expect(() =>
      Schema.decodeUnknownSync(CreateInvitationRequestSchema)({
        recipientEmail: "not-an-email",
        role: "MEMBER",
      }),
    ).toThrow("Invalid email format");
  });

  it("rejects missing @ symbol", () => {
    expect(() =>
      Schema.decodeUnknownSync(CreateInvitationRequestSchema)({
        recipientEmail: "testexample.com",
        role: "MEMBER",
      }),
    ).toThrow("Invalid email format");
  });

  it("rejects OWNER role", () => {
    expect(() =>
      Schema.decodeUnknownSync(CreateInvitationRequestSchema)({
        recipientEmail: "test@example.com",
        role: "OWNER",
      }),
    ).toThrow();
  });

  it("accepts valid email and ADMIN role", () => {
    const result = Schema.decodeUnknownSync(CreateInvitationRequestSchema)({
      recipientEmail: "test@example.com",
      role: "ADMIN",
    });
    expect(result.recipientEmail).toBe("test@example.com");
    expect(result.role).toBe("ADMIN");
  });

  it("accepts valid email and MEMBER role", () => {
    const result = Schema.decodeUnknownSync(CreateInvitationRequestSchema)({
      recipientEmail: "test@example.com",
      role: "MEMBER",
    });
    expect(result.recipientEmail).toBe("test@example.com");
    expect(result.role).toBe("MEMBER");
  });
});

describe("AcceptInvitationRequestSchema validation", () => {
  it("accepts valid token", () => {
    const result = Schema.decodeUnknownSync(AcceptInvitationRequestSchema)({
      token: "some-valid-token",
    });
    expect(result.token).toBe("some-valid-token");
  });
});

describe.sequential("Organization Invitations API", (it) => {
  let createdInvitation: PublicOrganizationInvitation;
  let invitationForRevoke: PublicOrganizationInvitation;

  // Test list endpoint
  it.effect("GET /organizations/:id/invitations - lists invitations", () =>
    Effect.gen(function* () {
      const { client, org } = yield* TestApiContext;
      const invitations = yield* client["organization-invitations"].list({
        path: { organizationId: org.id },
      });
      expect(Array.isArray(invitations)).toBe(true);
    }),
  );

  // Test create endpoint - MEMBER role
  it.effect(
    "POST /organizations/:id/invitations - creates invitation with MEMBER role",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const invitation = yield* client["organization-invitations"].create({
          path: { organizationId: org.id },
          payload: {
            recipientEmail: "newmember@example.com",
            role: "MEMBER",
          },
        });

        expect(invitation.recipientEmail).toBe("newmember@example.com");
        expect(invitation.role).toBe("MEMBER");
        expect(invitation.status).toBe("pending");
        expect(invitation.organizationId).toBe(org.id);
        expect(invitation.id).toBeDefined();
        expect(invitation.expiresAt).toBeDefined();

        // Store for later tests
        createdInvitation = invitation;
      }),
  );

  // Test create endpoint - ADMIN role
  it.effect(
    "POST /organizations/:id/invitations - creates invitation with ADMIN role",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const invitation = yield* client["organization-invitations"].create({
          path: { organizationId: org.id },
          payload: {
            recipientEmail: "admin@example.com",
            role: "ADMIN",
          },
        });

        expect(invitation.recipientEmail).toBe("admin@example.com");
        expect(invitation.role).toBe("ADMIN");
        expect(invitation.status).toBe("pending");
      }),
  );

  // Test schema validation
  it.effect("POST /organizations/:id/invitations - rejects invalid email", () =>
    Effect.gen(function* () {
      const { client, org } = yield* TestApiContext;
      const result = yield* client["organization-invitations"]
        .create({
          path: { organizationId: org.id },
          payload: {
            recipientEmail: "not-an-email",
            role: "MEMBER",
          },
        })
        .pipe(Effect.flip);

      expect(result).toBeInstanceOf(ParseError);
      expect(result.message).toContain("Invalid email format");
    }),
  );

  // Test get endpoint
  it.effect(
    "GET /organizations/:id/invitations/:invitationId - retrieves invitation",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const invitation = yield* client["organization-invitations"].get({
          path: {
            organizationId: org.id,
            invitationId: createdInvitation.id,
          },
        });

        expect(invitation.id).toBe(createdInvitation.id);
        expect(invitation.recipientEmail).toBe(
          createdInvitation.recipientEmail,
        );
        expect(invitation.role).toBe(createdInvitation.role);
      }),
  );

  // Test resend endpoint
  it.effect(
    "POST /organizations/:id/invitations/:invitationId/resend - resends invitation",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        yield* client["organization-invitations"].resend({
          path: {
            organizationId: org.id,
            invitationId: createdInvitation.id,
          },
        });
        // No error means success
      }),
  );

  // Test revoke endpoint
  it.effect(
    "POST /organizations/:id/invitations/:invitationId/revoke - revokes pending invitation",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;

        // Create a new invitation to revoke
        const invitation = yield* client["organization-invitations"].create({
          path: { organizationId: org.id },
          payload: {
            recipientEmail: "revoke-test@example.com",
            role: "MEMBER",
          },
        });
        invitationForRevoke = invitation;

        // Revoke the invitation
        yield* client["organization-invitations"].revoke({
          path: {
            organizationId: org.id,
            invitationId: invitation.id,
          },
        });

        // Verify it was revoked (soft-delete updates status to "revoked")
        const revokedInvitation = yield* client["organization-invitations"].get(
          {
            path: {
              organizationId: org.id,
              invitationId: invitation.id,
            },
          },
        );

        expect(revokedInvitation.status).toBe("revoked");
        expect(revokedInvitation.revokedAt).toBeInstanceOf(Date);
      }),
  );

  // Test resend validation - revoked invitation
  it.effect(
    "POST /organizations/:id/invitations/:invitationId/resend - rejects revoked invitation",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;

        // Try to resend the revoked invitation
        const result = yield* client["organization-invitations"]
          .resend({
            path: {
              organizationId: org.id,
              invitationId: invitationForRevoke.id,
            },
          })
          .pipe(Effect.flip);

        // Should fail with ImmutableResourceError
        assert(result instanceof ImmutableResourceError);
        expect(result.message).toContain(
          "Cannot resend invitation with status",
        );
      }),
  );

  // Test duplicate prevention
  it.effect(
    "POST /organizations/:id/invitations - prevents duplicate invitations",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;

        // Try to create another invitation for the same email
        const result = yield* client["organization-invitations"]
          .create({
            path: { organizationId: org.id },
            payload: {
              recipientEmail: "newmember@example.com", // Same as first invitation
              role: "MEMBER",
            },
          })
          .pipe(Effect.flip);

        assert(result instanceof AlreadyExistsError);
      }),
  );

  // Test email normalization (case-insensitive)
  it.effect(
    "POST /organizations/:id/invitations - email is case-insensitive for duplicates",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;

        // Try to create invitation with uppercase email
        const result = yield* client["organization-invitations"]
          .create({
            path: { organizationId: org.id },
            payload: {
              recipientEmail: "NEWMEMBER@EXAMPLE.COM", // Same email, different case
              role: "MEMBER",
            },
          })
          .pipe(Effect.flip);

        assert(result instanceof AlreadyExistsError);
      }),
  );

  // Test list shows only pending invitations
  it.effect(
    "GET /organizations/:id/invitations - only shows pending invitations",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const invitations = yield* client["organization-invitations"].list({
          path: { organizationId: org.id },
        });

        // All listed invitations should be pending
        const allPending = invitations.every((inv) => inv.status === "pending");
        expect(allPending).toBe(true);

        // Should not include the revoked invitation
        const hasRevoked = invitations.some(
          (inv) => inv.id === invitationForRevoke.id,
        );
        expect(hasRevoked).toBe(false);
      }),
  );

  it.effect("POST /invitations/accept - fails with invalid token", () =>
    Effect.gen(function* () {
      const { client } = yield* TestApiContext;

      const result = yield* client["organization-invitations"]
        .accept({
          payload: { token: "fake-token" },
        })
        .pipe(Effect.flip);

      assert(result instanceof NotFoundError);
      expect(result.message).toContain("Invitation not found");
    }),
  );
});

// Edge case tests that need direct database access
describe("Organization Invitations API - Edge Cases", () => {
  it.rollback(
    "POST /organizations/:id/invitations/:invitationId/resend - rejects accepted invitation",
    () =>
      Effect.gen(function* () {
        const db = yield* Database;
        const drizzle = yield* DrizzleORM;
        const { org, owner } = yield* TestOrganizationFixture;

        // Create invitation
        const invitation = yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: {
            recipientEmail: "accepted-test@example.com",
            role: "MEMBER",
          },
        });

        // Manually mark invitation as accepted
        yield* drizzle
          .update(organizationInvitations)
          .set({
            status: "accepted",
            acceptedAt: new Date(),
          })
          .where(eq(organizationInvitations.id, invitation.id));

        // Try to resend using the handler directly - should fail
        const result = yield* resendInvitationHandler(org.id, invitation.id)
          .pipe(Effect.provideService(AuthenticatedUser, owner))
          .pipe(Effect.flip);

        assert(result instanceof ImmutableResourceError);
        expect(result.message).toContain(
          "Cannot resend invitation with status",
        );
      }),
  );

  it.rollback(
    "POST /organizations/:id/invitations/:invitationId/resend - rejects expired invitation",
    () =>
      Effect.gen(function* () {
        const db = yield* Database;
        const drizzle = yield* DrizzleORM;
        const { org, owner } = yield* TestOrganizationFixture;

        // Create invitation
        const invitation = yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: {
            recipientEmail: "expired-test@example.com",
            role: "MEMBER",
          },
        });

        // Manually expire the invitation
        // Must satisfy constraint: expiresAt > createdAt
        const pastCreatedDate = new Date(Date.now() - 1000 * 60 * 60 * 24 * 8); // 8 days ago
        const pastExpiredDate = new Date(Date.now() - 1000 * 60 * 60 * 24); // 1 day ago
        yield* drizzle
          .update(organizationInvitations)
          .set({
            createdAt: pastCreatedDate,
            expiresAt: pastExpiredDate,
            updatedAt: pastExpiredDate,
          })
          .where(eq(organizationInvitations.id, invitation.id));

        // Try to resend using the handler directly - should fail
        const result = yield* resendInvitationHandler(org.id, invitation.id)
          .pipe(Effect.provideService(AuthenticatedUser, owner))
          .pipe(Effect.flip);

        assert(result instanceof ImmutableResourceError);
        expect(result.message).toContain("Cannot resend expired invitation");
      }),
  );

  it.rollback(
    "POST /invitations/accept - accepts invitation with valid token (handler)",
    () =>
      Effect.gen(function* () {
        const db = yield* Database;
        const { org, owner, nonMember } = yield* TestOrganizationFixture;

        // Create invitation and get the token
        const invitationWithMetadata =
          yield* db.organizations.invitations.create({
            userId: owner.id,
            organizationId: org.id,
            data: {
              recipientEmail: nonMember.email,
              role: "MEMBER",
            },
          });

        // Accept the invitation using the handler
        const membership = yield* acceptInvitationHandler({
          token: invitationWithMetadata.token,
        }).pipe(Effect.provideService(AuthenticatedUser, nonMember));

        expect(membership.memberId).toBe(nonMember.id);
        expect(membership.role).toBe("MEMBER");
        expect(membership.createdAt).toBeInstanceOf(Date);
      }),
  );

  it.rollback(
    "POST /organizations/:id/invitations - handles sender with no name (uses email as fallback)",
    () =>
      Effect.gen(function* () {
        const drizzle = yield* DrizzleORM;
        const { org, owner } = yield* TestOrganizationFixture;

        // Update owner to have null name
        const { users } = yield* Effect.promise(() => import("@/db/schema"));
        yield* drizzle
          .update(users)
          .set({ name: null })
          .where(eq(users.id, owner.id));

        // Create invitation - should use email as fallback for sender name
        const invitation = yield* createInvitationHandler(org.id, {
          recipientEmail: "no-sender-name@example.com",
          role: "MEMBER",
        }).pipe(
          Effect.provideService(AuthenticatedUser, { ...owner, name: null }),
        );

        expect(invitation.recipientEmail).toBe("no-sender-name@example.com");
        expect(invitation.role).toBe("MEMBER");
        expect(invitation.status).toBe("pending");
      }),
  );

  it.rollback(
    "POST /organizations/:id/invitations/:invitationId/resend - handles sender with no name (uses email as fallback)",
    () =>
      Effect.gen(function* () {
        const drizzle = yield* DrizzleORM;
        const { org, owner } = yield* TestOrganizationFixture;

        // Update owner to have null name
        const { users } = yield* Effect.promise(() => import("@/db/schema"));
        yield* drizzle
          .update(users)
          .set({ name: null })
          .where(eq(users.id, owner.id));

        // Create an invitation first
        const invitation = yield* createInvitationHandler(org.id, {
          recipientEmail: "no-sender-name@example.com",
          role: "MEMBER",
        }).pipe(
          Effect.provideService(AuthenticatedUser, { ...owner, name: null }),
        );

        // Resend invitation - should use email as fallback for sender name
        yield* resendInvitationHandler(org.id, invitation.id).pipe(
          Effect.provideService(AuthenticatedUser, { ...owner, name: null }),
        );
      }),
  );

  it.rollback(
    "POST /organizations/:id/invitations - creates invitation when email rendering fails (returns null)",
    () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;

        // Mock renderEmailTemplate to return null (rendering failure)
        const renderModule = yield* Effect.promise(
          () => import("@/emails/render"),
        );
        const renderSpy = vi
          .spyOn(renderModule, "renderEmailTemplate")
          .mockReturnValueOnce(Effect.succeed(null));

        // Create invitation - should succeed despite rendering failure
        const invitation = yield* createInvitationHandler(org.id, {
          recipientEmail: "email-render-fail@example.com",
          role: "MEMBER",
        }).pipe(Effect.provideService(AuthenticatedUser, owner));

        expect(invitation.recipientEmail).toBe("email-render-fail@example.com");
        expect(invitation.role).toBe("MEMBER");
        expect(invitation.status).toBe("pending");

        // Verify renderEmailTemplate was called
        expect(renderSpy).toHaveBeenCalled();

        renderSpy.mockRestore();
      }),
  );

  it.rollback(
    "POST /organizations/:id/invitations/:invitationId/resend - resends invitation when email rendering fails (returns null)",
    () =>
      Effect.gen(function* () {
        const db = yield* Database;
        const { org, owner } = yield* TestOrganizationFixture;

        // Create an invitation first
        const invitation = yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: {
            recipientEmail: "resend-render-fail@example.com",
            role: "MEMBER",
          },
        });

        // Mock renderEmailTemplate to return null (rendering failure)
        const renderModule = yield* Effect.promise(
          () => import("@/emails/render"),
        );
        const renderSpy = vi
          .spyOn(renderModule, "renderEmailTemplate")
          .mockReturnValueOnce(Effect.succeed(null));

        // Resend invitation - should succeed despite rendering failure
        yield* resendInvitationHandler(org.id, invitation.id).pipe(
          Effect.provideService(AuthenticatedUser, owner),
        );

        // Verify renderEmailTemplate was called
        expect(renderSpy).toHaveBeenCalled();

        renderSpy.mockRestore();
      }),
  );
});
