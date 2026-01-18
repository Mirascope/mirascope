import {
  describe,
  it,
  expect,
  TestOrganizationFixture,
  TestFreePlanOrganizationFixture,
  MockDrizzleORM,
  TestDrizzleORM,
  MockAnalytics,
  MockSpansMeteringQueue,
} from "@/tests/db";
import { TestSubscriptionWithRealDatabaseFixture } from "@/tests/payments";
import { Database } from "@/db/database";
import { Effect, Layer } from "effect";
import {
  type PublicOrganizationInvitation,
  type PublicOrganizationMembership,
  type PublicOrganizationMembershipAudit,
} from "@/db/schema";
import {
  AlreadyExistsError,
  DatabaseError,
  ImmutableResourceError,
  NotFoundError,
  PermissionDeniedError,
  PlanLimitExceededError,
} from "@/errors";

describe("OrganizationInvitations", () => {
  describe("create", () => {
    it.effect("creates invitation as OWNER for MEMBER role", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const invitation = yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: { recipientEmail: "newuser@example.com", role: "MEMBER" },
        });

        expect(invitation).toMatchObject({
          organizationId: org.id,
          senderId: owner.id,
          recipientEmail: "newuser@example.com",
          role: "MEMBER",
          status: "pending",
          organizationName: org.name,
          senderEmail: owner.email,
          senderName: owner.name,
        });
        expect(invitation.token).toBeDefined();
        expect(invitation.expiresAt).toBeInstanceOf(Date);
      }),
    );

    it.effect("creates invitation as OWNER for ADMIN role", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const invitation = yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: { recipientEmail: "newadmin@example.com", role: "ADMIN" },
        });

        expect(invitation.role).toBe("ADMIN");
      }),
    );

    it.effect("creates invitation as ADMIN for MEMBER role", () =>
      Effect.gen(function* () {
        const { org, admin } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const invitation = yield* db.organizations.invitations.create({
          userId: admin.id,
          organizationId: org.id,
          data: { recipientEmail: "newuser@example.com", role: "MEMBER" },
        });

        expect(invitation).toMatchObject({
          senderId: admin.id,
          role: "MEMBER",
          senderEmail: admin.email,
        });
      }),
    );

    it.effect("normalizes email to lowercase", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const invitation = yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: {
            recipientEmail: "NewUser@EXAMPLE.COM",
            role: "MEMBER",
          },
        });

        expect(invitation.recipientEmail).toBe("newuser@example.com");
      }),
    );

    it.effect("calculates expiration as 7 days from creation", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const now = Date.now();
        const invitation = yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: { recipientEmail: "test@example.com", role: "MEMBER" },
        });

        // Expiration should be approximately 7 days from now
        // Allow for timezone differences and test execution time (6-8 days)
        const sixDaysMs = 6 * 24 * 60 * 60 * 1000;
        const eightDaysMs = 8 * 24 * 60 * 60 * 1000;
        const expiresInMs = invitation.expiresAt.getTime() - now;

        expect(expiresInMs).toBeGreaterThanOrEqual(sixDaysMs);
        expect(expiresInMs).toBeLessThanOrEqual(eightDaysMs);
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when ADMIN tries to invite ADMIN",
      () =>
        Effect.gen(function* () {
          const { org, admin } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations.invitations
            .create({
              userId: admin.id,
              organizationId: org.id,
              data: { recipientEmail: "newadmin@example.com", role: "ADMIN" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe("Cannot invite a member with role ADMIN");
        }),
    );

    it.effect(
      "returns `PermissionDeniedError` when MEMBER tries to create",
      () =>
        Effect.gen(function* () {
          const { org, member } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations.invitations
            .create({
              userId: member.id,
              organizationId: org.id,
              data: { recipientEmail: "test@example.com", role: "MEMBER" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
        }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations.invitations
          .create({
            userId: nonMember.id,
            organizationId: org.id,
            data: { recipientEmail: "test@example.com", role: "MEMBER" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }),
    );

    it.effect(
      "returns `AlreadyExistsError` when email is already a member",
      () =>
        Effect.gen(function* () {
          const { org, owner, member } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations.invitations
            .create({
              userId: owner.id,
              organizationId: org.id,
              data: { recipientEmail: member.email, role: "MEMBER" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(AlreadyExistsError);
          expect(result.message).toBe(
            "User is already a member of this organization",
          );
        }),
    );

    it.effect(
      "returns `AlreadyExistsError` when email is already a member (case insensitive)",
      () =>
        Effect.gen(function* () {
          const { org, owner, member } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations.invitations
            .create({
              userId: owner.id,
              organizationId: org.id,
              data: {
                recipientEmail: member.email.toUpperCase(),
                role: "MEMBER",
              },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(AlreadyExistsError);
        }),
    );

    it.effect(
      "returns `AlreadyExistsError` when pending invitation exists",
      () =>
        Effect.gen(function* () {
          const { org, owner } = yield* TestOrganizationFixture;
          const db = yield* Database;

          yield* db.organizations.invitations.create({
            userId: owner.id,
            organizationId: org.id,
            data: { recipientEmail: "test@example.com", role: "MEMBER" },
          });

          const result = yield* db.organizations.invitations
            .create({
              userId: owner.id,
              organizationId: org.id,
              data: { recipientEmail: "test@example.com", role: "ADMIN" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(AlreadyExistsError);
          expect(result.message).toBe(
            "A pending invitation already exists for this email",
          );
        }),
    );

    it.effect("allows creating invitation after previous was accepted", () =>
      Effect.gen(function* () {
        const { org, owner, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const firstInvitation = yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: { recipientEmail: nonMember.email, role: "MEMBER" },
        });

        yield* db.organizations.invitations.accept({
          token: firstInvitation.token,
          acceptingUserId: nonMember.id,
        });

        yield* db.organizations.memberships.delete({
          userId: owner.id,
          organizationId: org.id,
          memberId: nonMember.id,
        });

        const secondInvitation = yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: { recipientEmail: nonMember.email, role: "ADMIN" },
        });

        expect(secondInvitation.role).toBe("ADMIN");
      }),
    );

    it.effect(
      "returns `DatabaseError` when checking existing membership fails",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.invitations
            .create({
              userId: "owner-id",
              organizationId: "org-id",
              data: { recipientEmail: "test@example.com", role: "MEMBER" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to check existing membership");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              .select([{ role: "OWNER" }])
              .select(new Error("Connection failed"))
              .build(),
          ),
        ),
    );

    it.effect(
      "returns `DatabaseError` when checking existing invitation fails",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.invitations
            .create({
              userId: "owner-id",
              organizationId: "org-id",
              data: { recipientEmail: "test@example.com", role: "MEMBER" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to check existing invitation");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              .select([{ role: "OWNER" }])
              .select([])
              .select(new Error("Connection failed"))
              .build(),
          ),
        ),
    );

    it.effect("returns `DatabaseError` when insert fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.invitations
          .create({
            userId: "owner-id",
            organizationId: "org-id",
            data: { recipientEmail: "test@example.com", role: "MEMBER" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create invitation");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            .select([{ role: "OWNER" }])
            .select([])
            .select([])
            .select([{ stripeCustomerId: "cus_test" }]) // getPlan: fetch org
            .select([{ count: 1 }]) // checkSeatLimit: count memberships
            .select([{ count: 0 }]) // checkSeatLimit: count invitations
            .select([{ id: "org-id", name: "Test Org" }])
            .select([{ name: "Owner", email: "owner@example.com" }])
            .insert(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when fetching sender user fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.invitations
          .create({
            userId: "owner-id",
            organizationId: "org-id",
            data: { recipientEmail: "test@example.com", role: "MEMBER" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get user");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            .select([{ role: "OWNER" }])
            .select([])
            .select([])
            .select([{ stripeCustomerId: "cus_test" }]) // getPlan: fetch org
            .select([{ count: 1 }]) // checkSeatLimit: count memberships
            .select([{ count: 0 }]) // checkSeatLimit: count invitations
            .select([{ id: "org-id", name: "Test Org" }]) // getInvitationMetadata: fetch organization
            .select(new Error("Connection failed")) // getInvitationMetadata: fetch sender user fails
            .build(),
        ),
      ),
    );

    it.effect("returns `NotFoundError` when organization not found", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.invitations
          .create({
            userId: "owner-id",
            organizationId: "org-id",
            data: { recipientEmail: "test@example.com", role: "MEMBER" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found: org-id");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            .select([{ role: "OWNER" }])
            .select([])
            .select([])
            .select([]) // getPlan: fetch org returns empty (triggers NotFoundError)
            .build(),
        ),
      ),
    );

    it.effect(
      "returns `DatabaseError` when fetching organization fails in getInvitationMetadata",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.invitations
            .create({
              userId: "owner-id",
              organizationId: "org-id",
              data: { recipientEmail: "test@example.com", role: "MEMBER" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to fetch organization");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              .select([{ role: "OWNER" }])
              .select([])
              .select([])
              .select([{ stripeCustomerId: "cus_test" }]) // getPlan: fetch org
              .select([{ count: 1 }]) // checkSeatLimit: count memberships
              .select([{ count: 0 }]) // checkSeatLimit: count invitations
              .select(new Error("Connection failed")) // getInvitationMetadata: fetch organization fails
              .build(),
          ),
        ),
    );

    it.effect(
      "returns `NotFoundError` when organization not found in getInvitationMetadata",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.invitations
            .create({
              userId: "owner-id",
              organizationId: "org-id",
              data: { recipientEmail: "test@example.com", role: "MEMBER" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(NotFoundError);
          expect(result.message).toBe("Organization not found");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              .select([{ role: "OWNER" }])
              .select([])
              .select([])
              .select([{ stripeCustomerId: "cus_test" }]) // getPlan: fetch org
              .select([{ count: 1 }]) // checkSeatLimit: count memberships
              .select([{ count: 0 }]) // checkSeatLimit: count invitations
              .select([]) // getInvitationMetadata: organization not found
              .build(),
          ),
        ),
    );

    it.effect(
      "returns `DatabaseError` when counting memberships fails in checkSeatLimit",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.invitations
            .create({
              userId: "owner-id",
              organizationId: "org-id",
              data: { recipientEmail: "test@example.com", role: "MEMBER" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to count memberships");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              .select([{ role: "OWNER" }])
              .select([])
              .select([])
              .select([{ stripeCustomerId: "cus_test" }]) // getPlan: fetch org
              .select(new Error("Connection failed")) // checkSeatLimit: count memberships fails
              .build(),
          ),
        ),
    );

    it.effect(
      "returns `DatabaseError` when counting invitations fails in checkSeatLimit",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.invitations
            .create({
              userId: "owner-id",
              organizationId: "org-id",
              data: { recipientEmail: "test@example.com", role: "MEMBER" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to count invitations");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              .select([{ role: "OWNER" }])
              .select([])
              .select([])
              .select([{ stripeCustomerId: "cus_test" }]) // getPlan: fetch org
              .select([{ count: 1 }]) // checkSeatLimit: count memberships succeeds
              .select(new Error("Connection failed")) // checkSeatLimit: count invitations fails
              .build(),
          ),
        ),
    );

    it.effect(
      "returns `PlanLimitExceededError` when seat limit is exceeded",
      () =>
        Effect.gen(function* () {
          const { org, owner, nonMember } =
            yield* TestFreePlanOrganizationFixture;
          const db = yield* Database;

          // Org has 1 seat (owner) and FREE plan allows only 1 seat
          // Trying to add another user should exceed the limit
          const result = yield* db.organizations.invitations
            .create({
              userId: owner.id,
              organizationId: org.id,
              data: { recipientEmail: nonMember.email, role: "MEMBER" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PlanLimitExceededError);
          expect(result.message).toContain("free plan limit is 1 seat(s)");
        }).pipe(
          Effect.provide(
            Layer.mergeAll(
              Database.Default.pipe(
                Layer.provide(
                  TestSubscriptionWithRealDatabaseFixture(
                    { plan: "free" },
                    TestDrizzleORM,
                  ),
                ),
              ),
              MockAnalytics,
              MockSpansMeteringQueue,
            ),
          ),
        ),
    );
  });

  describe("findAll", () => {
    it.effect("lists all pending invitations for an organization", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: { recipientEmail: "user1@example.com", role: "MEMBER" },
        });

        yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: { recipientEmail: "user2@example.com", role: "ADMIN" },
        });

        const invitations = yield* db.organizations.invitations.findAll({
          userId: owner.id,
          organizationId: org.id,
        });

        expect(invitations).toHaveLength(2);
        expect(invitations[0]).toMatchObject({
          recipientEmail: "user1@example.com",
          status: "pending",
        } satisfies Partial<PublicOrganizationInvitation>);
        expect(invitations[1]).toMatchObject({
          recipientEmail: "user2@example.com",
          status: "pending",
        } satisfies Partial<PublicOrganizationInvitation>);
      }),
    );

    it.effect("returns empty array when no invitations exist", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const invitations = yield* db.organizations.invitations.findAll({
          userId: owner.id,
          organizationId: org.id,
        });

        expect(invitations).toEqual([]);
      }),
    );

    it.effect("does not include token in results", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: { recipientEmail: "test@example.com", role: "MEMBER" },
        });

        const invitations = yield* db.organizations.invitations.findAll({
          userId: owner.id,
          organizationId: org.id,
        });

        expect(invitations[0]).not.toHaveProperty("token");
      }),
    );

    it.effect("allows ADMIN to list invitations", () =>
      Effect.gen(function* () {
        const { org, owner, admin } = yield* TestOrganizationFixture;
        const db = yield* Database;

        yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: { recipientEmail: "test@example.com", role: "MEMBER" },
        });

        const invitations = yield* db.organizations.invitations.findAll({
          userId: admin.id,
          organizationId: org.id,
        });

        expect(invitations).toHaveLength(1);
      }),
    );

    it.effect("returns `PermissionDeniedError` when MEMBER tries to list", () =>
      Effect.gen(function* () {
        const { org, member } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations.invitations
          .findAll({
            userId: member.id,
            organizationId: org.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
      }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations.invitations
          .findAll({
            userId: nonMember.id,
            organizationId: org.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.invitations
          .findAll({
            userId: "owner-id",
            organizationId: "org-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to list invitations");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            .select([{ role: "OWNER" }])
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );
  });

  describe("findById", () => {
    it.effect("retrieves a specific invitation", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const created = yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: { recipientEmail: "test@example.com", role: "MEMBER" },
        });

        const found = yield* db.organizations.invitations.findById({
          userId: owner.id,
          organizationId: org.id,
          invitationId: created.id,
        });

        expect(found).toMatchObject({
          id: created.id,
          recipientEmail: "test@example.com",
          role: "MEMBER",
        } satisfies Partial<PublicOrganizationInvitation>);
      }),
    );

    it.effect("does not include token in result", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const created = yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: { recipientEmail: "test@example.com", role: "MEMBER" },
        });

        const found = yield* db.organizations.invitations.findById({
          userId: owner.id,
          organizationId: org.id,
          invitationId: created.id,
        });

        expect(found).not.toHaveProperty("token");
      }),
    );

    it.effect("allows ADMIN to get invitation", () =>
      Effect.gen(function* () {
        const { org, owner, admin } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const created = yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: { recipientEmail: "test@example.com", role: "MEMBER" },
        });

        const found = yield* db.organizations.invitations.findById({
          userId: admin.id,
          organizationId: org.id,
          invitationId: created.id,
        });

        expect(found.id).toBe(created.id);
      }),
    );

    it.effect("returns `PermissionDeniedError` when MEMBER tries to get", () =>
      Effect.gen(function* () {
        const { org, owner, member } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const created = yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: { recipientEmail: "test@example.com", role: "MEMBER" },
        });

        const result = yield* db.organizations.invitations
          .findById({
            userId: member.id,
            organizationId: org.id,
            invitationId: created.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
      }),
    );

    it.effect("returns `NotFoundError` when invitation doesn't exist", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations.invitations
          .findById({
            userId: owner.id,
            organizationId: org.id,
            invitationId: crypto.randomUUID(),
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Invitation not found");
      }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations.invitations
          .findById({
            userId: nonMember.id,
            organizationId: org.id,
            invitationId: crypto.randomUUID(),
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.invitations
          .findById({
            userId: "owner-id",
            organizationId: "org-id",
            invitationId: "invitation-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find invitation");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            .select([{ role: "OWNER" }])
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );
  });

  describe("update", () => {
    it.effect(
      "returns `ImmutableResourceError` (invitations are immutable)",
      () =>
        Effect.gen(function* () {
          const { org, owner } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations.invitations
            .update({
              userId: owner.id,
              organizationId: org.id,
              invitationId: crypto.randomUUID(),
              data: undefined as never,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(ImmutableResourceError);
          expect(result.message).toContain("Invitations cannot be updated.");
        }),
    );
  });

  describe("delete", () => {
    it.effect(
      "returns `ImmutableResourceError` (invitations are immutable)",
      () =>
        Effect.gen(function* () {
          const { org, owner } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const invitation = yield* db.organizations.invitations.create({
            userId: owner.id,
            organizationId: org.id,
            data: { recipientEmail: "test@example.com", role: "MEMBER" },
          });

          const result = yield* db.organizations.invitations
            .delete({
              userId: owner.id,
              organizationId: org.id,
              invitationId: invitation.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(ImmutableResourceError);
          expect(result.message).toContain("Invitations cannot be deleted.");
        }),
    );
  });

  describe("revoke", () => {
    it.effect("revokes a pending invitation", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const invitation = yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: { recipientEmail: "test@example.com", role: "MEMBER" },
        });

        yield* db.organizations.invitations.revoke({
          userId: owner.id,
          organizationId: org.id,
          invitationId: invitation.id,
        });

        const found = yield* db.organizations.invitations.findById({
          userId: owner.id,
          organizationId: org.id,
          invitationId: invitation.id,
        });

        expect(found.status).toBe("revoked");
        expect(found.revokedAt).toBeInstanceOf(Date);
      }),
    );

    it.effect("allows OWNER to revoke ADMIN invitation", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const invitation = yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: { recipientEmail: "test@example.com", role: "ADMIN" },
        });

        yield* db.organizations.invitations.revoke({
          userId: owner.id,
          organizationId: org.id,
          invitationId: invitation.id,
        });

        const found = yield* db.organizations.invitations.findById({
          userId: owner.id,
          organizationId: org.id,
          invitationId: invitation.id,
        });

        expect(found.status).toBe("revoked");
      }),
    );

    it.effect("allows ADMIN to revoke MEMBER invitation", () =>
      Effect.gen(function* () {
        const { org, owner, admin } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const invitation = yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: { recipientEmail: "test@example.com", role: "MEMBER" },
        });

        yield* db.organizations.invitations.revoke({
          userId: admin.id,
          organizationId: org.id,
          invitationId: invitation.id,
        });

        const found = yield* db.organizations.invitations.findById({
          userId: owner.id,
          organizationId: org.id,
          invitationId: invitation.id,
        });

        expect(found.status).toBe("revoked");
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when ADMIN tries to revoke ADMIN invitation",
      () =>
        Effect.gen(function* () {
          const { org, owner, admin } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const invitation = yield* db.organizations.invitations.create({
            userId: owner.id,
            organizationId: org.id,
            data: { recipientEmail: "test@example.com", role: "ADMIN" },
          });

          const result = yield* db.organizations.invitations
            .revoke({
              userId: admin.id,
              organizationId: org.id,
              invitationId: invitation.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "Cannot revoke invitation for role ADMIN",
          );
        }),
    );

    it.effect(
      "returns `PermissionDeniedError` when MEMBER tries to revoke",
      () =>
        Effect.gen(function* () {
          const { org, owner, member } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const invitation = yield* db.organizations.invitations.create({
            userId: owner.id,
            organizationId: org.id,
            data: { recipientEmail: "test@example.com", role: "MEMBER" },
          });

          const result = yield* db.organizations.invitations
            .revoke({
              userId: member.id,
              organizationId: org.id,
              invitationId: invitation.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
        }),
    );

    it.effect("returns `NotFoundError` when invitation doesn't exist", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations.invitations
          .revoke({
            userId: owner.id,
            organizationId: org.id,
            invitationId: crypto.randomUUID(),
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Invitation not found");
      }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations.invitations
          .revoke({
            userId: nonMember.id,
            organizationId: org.id,
            invitationId: crypto.randomUUID(),
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }),
    );

    it.effect("returns `DatabaseError` when fetching invitation fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.invitations
          .revoke({
            userId: "owner-id",
            organizationId: "org-id",
            invitationId: "invitation-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to fetch invitation");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            .select([{ role: "OWNER" }])
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when revoke fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.invitations
          .revoke({
            userId: "owner-id",
            organizationId: "org-id",
            invitationId: "invitation-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to revoke invitation");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            .select([{ role: "OWNER" }])
            .select([{ role: "MEMBER" }])
            .update(new Error("Connection failed"))
            .build(),
        ),
      ),
    );
  });

  describe("getWithMetadata", () => {
    it.effect("retrieves invitation with metadata for resending email", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const invitation = yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: { recipientEmail: "test@example.com", role: "MEMBER" },
        });

        const retrieved = yield* db.organizations.invitations.getWithMetadata({
          userId: owner.id,
          organizationId: org.id,
          invitationId: invitation.id,
        });

        expect(retrieved).toMatchObject({
          id: invitation.id,
          token: invitation.token,
          recipientEmail: invitation.recipientEmail,
          organizationName: org.name,
          senderEmail: owner.email,
        });
      }),
    );

    it.effect("allows ADMIN to get metadata for MEMBER invitation", () =>
      Effect.gen(function* () {
        const { org, owner, admin } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const invitation = yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: { recipientEmail: "test@example.com", role: "MEMBER" },
        });

        const invitationWithMetadata =
          yield* db.organizations.invitations.getWithMetadata({
            userId: admin.id,
            organizationId: org.id,
            invitationId: invitation.id,
          });

        expect(invitationWithMetadata.id).toBe(invitation.id);
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when ADMIN tries to get metadata for ADMIN invitation",
      () =>
        Effect.gen(function* () {
          const { org, owner, admin } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const invitation = yield* db.organizations.invitations.create({
            userId: owner.id,
            organizationId: org.id,
            data: { recipientEmail: "test@example.com", role: "ADMIN" },
          });

          const result = yield* db.organizations.invitations
            .getWithMetadata({
              userId: admin.id,
              organizationId: org.id,
              invitationId: invitation.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "Cannot get metadata for invitation with role ADMIN",
          );
        }),
    );

    it.effect(
      "returns `PermissionDeniedError` when MEMBER tries to get metadata",
      () =>
        Effect.gen(function* () {
          const { org, owner, member } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const invitation = yield* db.organizations.invitations.create({
            userId: owner.id,
            organizationId: org.id,
            data: { recipientEmail: "test@example.com", role: "MEMBER" },
          });

          const result = yield* db.organizations.invitations
            .getWithMetadata({
              userId: member.id,
              organizationId: org.id,
              invitationId: invitation.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
        }),
    );

    it.effect("returns `NotFoundError` when invitation doesn't exist", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations.invitations
          .getWithMetadata({
            userId: owner.id,
            organizationId: org.id,
            invitationId: crypto.randomUUID(),
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Invitation not found");
      }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations.invitations
          .getWithMetadata({
            userId: nonMember.id,
            organizationId: org.id,
            invitationId: crypto.randomUUID(),
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.invitations
          .getWithMetadata({
            userId: "owner-id",
            organizationId: "org-id",
            invitationId: "invitation-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to fetch invitation");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            .select([{ role: "OWNER" }])
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );
  });

  describe("accept", () => {
    it.effect("accepts invitation and creates membership", () =>
      Effect.gen(function* () {
        const { org, owner, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const invitation = yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: { recipientEmail: nonMember.email, role: "MEMBER" },
        });

        const membership = yield* db.organizations.invitations.accept({
          token: invitation.token,
          acceptingUserId: nonMember.id,
        });

        expect(membership).toMatchObject({
          memberId: nonMember.id,
          role: "MEMBER",
        } satisfies Partial<PublicOrganizationMembership>);

        const found = yield* db.organizations.memberships.findById({
          userId: owner.id,
          organizationId: org.id,
          memberId: nonMember.id,
        });

        expect(found.role).toBe("MEMBER");
      }),
    );

    it.effect("creates audit log with GRANT action", () =>
      Effect.gen(function* () {
        const { org, owner, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const invitation = yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: { recipientEmail: nonMember.email, role: "ADMIN" },
        });

        yield* db.organizations.invitations.accept({
          token: invitation.token,
          acceptingUserId: nonMember.id,
        });

        const audits = yield* db.organizations.memberships.audits.findAll({
          organizationId: org.id,
          memberId: nonMember.id,
        });

        expect(audits).toHaveLength(1);
        expect(audits[0]).toMatchObject({
          actorId: owner.id,
          targetId: nonMember.id,
          action: "GRANT",
          previousRole: null,
          newRole: "ADMIN",
        } satisfies Partial<PublicOrganizationMembershipAudit>);
      }),
    );

    it.effect("accepts invitation with case-insensitive email match", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const testId = crypto.randomUUID().slice(0, 8);
        const newUser = yield* db.users.create({
          data: {
            email: `NewUser-${testId}@EXAMPLE.COM`,
            name: "New User",
          },
        });

        const invitation = yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: {
            recipientEmail: newUser.email.toLowerCase(),
            role: "MEMBER",
          },
        });

        const membership = yield* db.organizations.invitations.accept({
          token: invitation.token,
          acceptingUserId: newUser.id,
        });

        expect(membership.memberId).toBe(newUser.id);
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when invitation is already accepted",
      () =>
        Effect.gen(function* () {
          const { org, owner, nonMember } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const invitation = yield* db.organizations.invitations.create({
            userId: owner.id,
            organizationId: org.id,
            data: { recipientEmail: nonMember.email, role: "MEMBER" },
          });

          yield* db.organizations.invitations.accept({
            token: invitation.token,
            acceptingUserId: nonMember.id,
          });

          const result = yield* db.organizations.invitations
            .accept({
              token: invitation.token,
              acceptingUserId: nonMember.id,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe("Invitation has already been accepted");
        }),
    );

    it.effect("returns `PermissionDeniedError` when email doesn't match", () =>
      Effect.gen(function* () {
        const { org, owner, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const testId = crypto.randomUUID().slice(0, 8);
        const otherUser = yield* db.users.create({
          data: {
            email: `other-${testId}@example.com`,
            name: "Other User",
          },
        });

        const invitation = yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: { recipientEmail: nonMember.email, role: "MEMBER" },
        });

        const result = yield* db.organizations.invitations
          .accept({
            token: invitation.token,
            acceptingUserId: otherUser.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(PermissionDeniedError);
        expect(result.message).toBe("Email address does not match invitation");
      }),
    );

    it.effect("returns `NotFoundError` when token is invalid", () =>
      Effect.gen(function* () {
        const { nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations.invitations
          .accept({
            token: crypto.randomUUID(),
            acceptingUserId: nonMember.id,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Invitation not found");
      }),
    );

    it.effect("returns `NotFoundError` when accepting user doesn't exist", () =>
      Effect.gen(function* () {
        const { org, owner, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const invitation = yield* db.organizations.invitations.create({
          userId: owner.id,
          organizationId: org.id,
          data: { recipientEmail: nonMember.email, role: "MEMBER" },
        });

        const result = yield* db.organizations.invitations
          .accept({
            token: invitation.token,
            acceptingUserId: crypto.randomUUID(),
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("User not found");
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when invitation has expired",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const expiredDate = new Date();
          expiredDate.setDate(expiredDate.getDate() - 1);

          const result = yield* db.organizations.invitations
            .accept({
              token: "some-token",
              acceptingUserId: "user-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe("Invitation has expired");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              .select([
                {
                  id: "invitation-id",
                  organizationId: "org-id",
                  senderId: "sender-id",
                  recipientEmail: "test@example.com",
                  role: "MEMBER",
                  token: "some-token",
                  status: "pending",
                  expiresAt: new Date(Date.now() - 1000 * 60 * 60), // 1 hour ago
                  createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24),
                  updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 24),
                  acceptedAt: null,
                  revokedAt: null,
                },
              ])
              .build(),
          ),
        ),
    );

    it.effect("returns `DatabaseError` when fetching invitation fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations.invitations
          .accept({
            token: "some-token",
            acceptingUserId: "user-id",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to fetch invitation");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM().select(new Error("Connection failed")).build(),
        ),
      ),
    );

    it.effect(
      "returns `DatabaseError` when updating invitation status fails",
      () =>
        Effect.gen(function* () {
          const db = yield* Database;

          const result = yield* db.organizations.invitations
            .accept({
              token: "some-token",
              acceptingUserId: "user-id",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(DatabaseError);
          expect(result.message).toBe("Failed to update invitation status");
        }).pipe(
          Effect.provide(
            new MockDrizzleORM()
              // Fetch invitation
              .select([
                {
                  id: "invitation-id",
                  organizationId: "org-id",
                  senderId: "sender-id",
                  recipientEmail: "test@example.com",
                  role: "MEMBER",
                  token: "some-token",
                  status: "pending",
                  expiresAt: new Date(Date.now() + 1000 * 60 * 60 * 24 * 7),
                  createdAt: new Date(),
                  updatedAt: new Date(),
                  acceptedAt: null,
                  revokedAt: null,
                },
              ])
              // Fetch accepting user
              .select([
                {
                  id: "user-id",
                  email: "test@example.com",
                  name: "Test User",
                },
              ])
              // Check for sender's role in org (for create membership authorization)
              .select([{ role: "OWNER" }])
              // checkSeatLimit (check: "membership"): getPlan -> fetch organization
              .select([{ stripeCustomerId: "cus_test" }])
              // checkSeatLimit (check: "membership"): count memberships only
              .select([{ count: 1 }])
              // Insert membership (returns via .returning(), no separate select needed)
              .insert([
                { memberId: "user-id", role: "MEMBER", createdAt: new Date() },
              ])
              // Insert audit log
              .insert([
                {
                  id: "audit-id",
                  userId: "sender-id",
                  organizationId: "org-id",
                  action: "MEMBER_ADDED",
                },
              ])
              // Update invitation status - THIS FAILS
              .update(new Error("Connection failed"))
              .build(),
          ),
        ),
    );
  });
});
