import {
  describe,
  it,
  expect,
  assert,
  TestOrganizationFixture,
  TestDrizzleORM,
  MockDrizzleORM,
  MockStripe,
} from "@/tests/db";
import { Database } from "@/db/database";
import { Effect, Layer } from "effect";
import {
  type PublicOrganizationWithMembership,
  type PublicOrganizationMembershipAudit,
} from "@/db/schema";
import {
  AlreadyExistsError,
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
} from "@/errors";

describe("Organizations", () => {
  // ===========================================================================
  // create
  // ===========================================================================

  describe("create", () => {
    it.effect("creates an organization with owner membership", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const user = yield* db.users.create({
          data: { email: "create-org@example.com", name: "Create Org User" },
        });

        const name = "New Test Organization";
        const slug = "new-test-organization";
        const org = yield* db.organizations.create({
          userId: user.id,
          data: { name, slug },
        });

        expect(org).toEqual({
          id: org.id,
          name,
          slug,
          stripeCustomerId: org.stripeCustomerId,
          role: "OWNER",
        } satisfies PublicOrganizationWithMembership);

        // Verify the organization can be found
        const found = yield* db.organizations.findById({
          userId: user.id,
          organizationId: org.id,
        });
        expect(found.name).toBe(name);

        // Verify audit log was created for OWNER GRANT
        const audits = yield* db.organizations.memberships.audits.findAll({
          organizationId: org.id,
          memberId: user.id,
        });
        expect(audits).toHaveLength(1);
        expect(audits[0]).toMatchObject({
          actorId: user.id,
          targetId: user.id,
          action: "GRANT",
          previousRole: null,
          newRole: "OWNER",
        } satisfies Partial<PublicOrganizationMembershipAudit>);
      }),
    );

    it.effect("returns `AlreadyExistsError` when slug is taken", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations
          .create({
            userId: owner.id,
            data: { name: "Different Name", slug: org.slug },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(AlreadyExistsError);
        expect(result.message).toBe(
          "An organization with this slug already exists",
        );
      }),
    );

    it.effect("returns `NotFoundError` when user does not exist", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .create({
            userId: "nonexistent-user-id",
            data: { name: "Test Org", slug: "test-org" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          "User with id nonexistent-user-id not found",
        );
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // select user email: returns empty (user not found)
            .select([])
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when fetching user email fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .create({
            userId: "user-id",
            data: { name: "Test Org", slug: "test-org" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe(
          "Failed to fetch user for organization creation",
        );
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // select user email: fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when insert fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .create({
            userId: "user-id",
            data: { name: "Test Org", slug: "test-org" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create organization");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // select user email: succeeds
            .select([{ email: "test@example.com" }])
            // insert organization: fails
            .insert(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when membership insert fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .create({
            userId: "user-id",
            data: { name: "Test Org", slug: "test-org" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create organization membership");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // select user email: succeeds
            .select([{ email: "test@example.com" }])
            // insert organization: succeeds
            .insert([{ id: "org-id", name: "Test Org" }])
            // insert membership: fails
            .insert(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when audit log insert fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .create({
            userId: "user-id",
            data: { name: "Test Org", slug: "test-org" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to create audit log");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // select user email: succeeds
            .select([{ email: "test@example.com" }])
            // insert organization: succeeds
            .insert([{ id: "org-id", name: "Test Org" }])
            // insert membership: succeeds
            .insert([])
            // insert audit: fails
            .insert(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect(
      "creates Stripe customer with correct email, name, and metadata",
      () => {
        // Capture the params passed to Stripe for customer creation
        type CapturedParams = {
          email?: string;
          name?: string;
          metadata?: Record<string, string>;
        };

        let capturedParams: CapturedParams | null = null;

        return Effect.gen(capturedParams, function* () {
          const db = yield* Database;

          const user = yield* db.users.create({
            data: {
              email: "stripe-test@example.com",
              name: "Stripe Test User",
            },
          });

          const organizationName = "Stripe Test Org";
          const organizationSlug = "stripe-test-org";

          const organization = yield* db.organizations.create({
            userId: user.id,
            data: { name: organizationName, slug: organizationSlug },
          });

          // Verify Stripe customer was created with correct parameters
          assert(capturedParams !== null);
          expect(capturedParams.email).toBe(user.email);
          expect(capturedParams.name).toBe(organizationName);
          expect(capturedParams.metadata).toMatchObject({
            organizationId: organization.id,
            organizationName,
            organizationSlug,
          });
        }).pipe(
          Effect.provide(
            Database.Default.pipe(
              Layer.provideMerge(TestDrizzleORM),
              Layer.provide(
                new MockStripe().customers
                  .create((params: CapturedParams) => {
                    capturedParams = params;
                    return { id: "cus_mock" };
                  })
                  .build(),
              ),
            ),
          ),
        );
      },
    );

    it.effect("deletes Stripe customer when database transaction fails", () => {
      // Track Stripe calls
      type CapturedCustomerId = string;
      let createdCustomerId: CapturedCustomerId | null = null;
      let deletedCustomerId: CapturedCustomerId | null = null;

      return Effect.gen(function* () {
        const db = yield* Database;

        // Attempt to create organization with DB insert that fails
        const result = yield* db.organizations
          .create({
            userId: "user-id",
            data: { name: "Test Org", slug: "test-org" },
          })
          .pipe(Effect.flip);

        // Verify the operation failed
        expect(result).toBeInstanceOf(DatabaseError);

        // Verify Stripe customer was created and deleted in cleanup
        assert(createdCustomerId !== null);
        assert(deletedCustomerId !== null);
        expect(deletedCustomerId).toBe(createdCustomerId);
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // select user email: succeeds
            .select([{ email: "test@example.com" }])
            // insert organization: fails (triggers rollback)
            .insert(new Error("Database connection failed"))
            .build(
              new MockStripe().customers
                .create(() => {
                  createdCustomerId = "cus_mock";
                  return { id: createdCustomerId };
                })
                .customers.del((id: CapturedCustomerId) => {
                  deletedCustomerId = id;
                  return { id };
                })
                .build(),
            ),
        ),
      );
    });
  });

  // ===========================================================================
  // findAll
  // ===========================================================================

  describe("findAll", () => {
    it.effect("retrieves all organizations for a user", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        // Create a second organization
        const org2 = yield* db.organizations.create({
          userId: owner.id,
          data: { name: "Second Organization", slug: "second-organization" },
        });

        const orgs = yield* db.organizations.findAll({ userId: owner.id });

        expect(orgs).toHaveLength(2);
        expect(orgs.map((o) => o.name).sort()).toEqual(
          [org.name, org2.name].sort(),
        );
      }),
    );

    it.effect("returns empty array for user with no organizations", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const user = yield* db.users.create({
          data: { email: "no-orgs@example.com", name: "No Orgs User" },
        });

        const orgs = yield* db.organizations.findAll({ userId: user.id });

        expect(orgs).toEqual([]);
      }),
    );

    it.effect("returns `DatabaseError` when query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .findAll({ userId: "user-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get user organizations");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM().select(new Error("Connection failed")).build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // findById
  // ===========================================================================

  describe("findById", () => {
    it.effect("retrieves organization when user is OWNER", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const found = yield* db.organizations.findById({
          userId: owner.id,
          organizationId: org.id,
        });

        expect(found).toMatchObject({
          id: org.id,
          name: org.name,
          role: "OWNER",
        } satisfies Partial<PublicOrganizationWithMembership>);
      }),
    );

    it.effect("retrieves organization when user is ADMIN", () =>
      Effect.gen(function* () {
        const { org, admin } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const found = yield* db.organizations.findById({
          userId: admin.id,
          organizationId: org.id,
        });

        expect(found).toMatchObject({
          id: org.id,
          name: org.name,
          role: "ADMIN",
        });
      }),
    );

    it.effect("retrieves organization when user is MEMBER", () =>
      Effect.gen(function* () {
        const { org, member } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const found = yield* db.organizations.findById({
          userId: member.id,
          organizationId: org.id,
        });

        expect(found).toMatchObject({
          id: org.id,
          name: org.name,
          role: "MEMBER",
        });
      }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations
          .findById({ userId: nonMember.id, organizationId: org.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }),
    );

    it.effect("returns `DatabaseError` when getRole fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .findById({ userId: "user-id", organizationId: "org-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get membership");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // getRole -> getMembership: fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when fetching organization fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .findById({ userId: "user-id", organizationId: "org-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to find organization");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize -> getRole -> getMembership
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "user-id",
                createdAt: new Date(),
              },
            ])
            // findById query: fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `NotFoundError` when organization not found", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .findById({ userId: "user-id", organizationId: "org-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          "Organization with organizationId org-id not found",
        );
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize -> getRole -> getMembership
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "user-id",
                createdAt: new Date(),
              },
            ])
            // findById query: returns empty (org not found)
            .select([])
            .build(),
        ),
      ),
    );
  });

  // ===========================================================================
  // update
  // ===========================================================================

  describe("update", () => {
    it.effect("updates organization when user is OWNER", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const newName = "Updated Organization Name";
        const updated = yield* db.organizations.update({
          userId: owner.id,
          organizationId: org.id,
          data: { name: newName },
        });

        expect(updated).toEqual({
          id: org.id,
          name: newName,
          slug: org.slug,
          stripeCustomerId: org.stripeCustomerId,
          role: "OWNER",
        } satisfies PublicOrganizationWithMembership);
      }),
    );

    it.effect("updates organization when user is ADMIN", () =>
      Effect.gen(function* () {
        const { org, admin } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const newName = "Admin Updated Name";
        const updated = yield* db.organizations.update({
          userId: admin.id,
          organizationId: org.id,
          data: { name: newName },
        });

        expect(updated).toEqual({
          id: org.id,
          name: newName,
          slug: org.slug,
          stripeCustomerId: org.stripeCustomerId,
          role: "ADMIN",
        } satisfies PublicOrganizationWithMembership);
      }),
    );

    it.effect("persists updates correctly", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const newName = "Persisted Name";
        yield* db.organizations.update({
          userId: owner.id,
          organizationId: org.id,
          data: { name: newName },
        });

        const found = yield* db.organizations.findById({
          userId: owner.id,
          organizationId: org.id,
        });

        expect(found.name).toBe(newName);
      }),
    );

    it.effect("updates organization slug only", () =>
      Effect.gen(function* () {
        const { org, owner } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const newSlug = "updated-slug";
        const updated = yield* db.organizations.update({
          userId: owner.id,
          organizationId: org.id,
          data: { slug: newSlug },
        });

        expect(updated).toEqual({
          id: org.id,
          name: org.name,
          slug: newSlug,
          stripeCustomerId: org.stripeCustomerId,
          role: "OWNER",
        } satisfies PublicOrganizationWithMembership);
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when MEMBER tries to update",
      () =>
        Effect.gen(function* () {
          const { org, member } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations
            .update({
              userId: member.id,
              organizationId: org.id,
              data: { name: "Should Fail" },
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to update this organization",
          );
        }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations
          .update({
            userId: nonMember.id,
            organizationId: org.id,
            data: { name: "Should Fail" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }),
    );

    it.effect("returns `DatabaseError` when getRole fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .update({
            userId: "user-id",
            organizationId: "org-id",
            data: { name: "New Name" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get membership");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // getRole -> getMembership: fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when update query fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .update({
            userId: "user-id",
            organizationId: "org-id",
            data: { name: "New Name" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to update organization");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize -> getRole -> memberships.findById
            //   -> authorize -> getRole -> getMembership
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "user-id",
                createdAt: new Date(),
              },
            ])
            //   -> findById actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "user-id",
                createdAt: new Date(),
              },
            ])
            // update query: fails
            .update(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `NotFoundError` when organization does not exist", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .update({
            userId: "user-id",
            organizationId: "org-id",
            data: { name: "New Name" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          "organization with organizationId org-id not found",
        );
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize -> getRole -> memberships.findById
            //   -> authorize -> getRole -> getMembership
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "user-id",
                createdAt: new Date(),
              },
            ])
            //   -> findById actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "user-id",
                createdAt: new Date(),
              },
            ])
            // update query: no rows updated
            .update([])
            .build(),
        ),
      ),
    );

    it.effect(
      "calls updateCustomer with correct parameters when name or slug changes",
      () => {
        // Capture the params passed to updateCustomer
        type CapturedParams = {
          customerId: string;
          organizationName?: string;
          organizationSlug?: string;
        };

        let capturedParams: CapturedParams | null = null;

        return Effect.gen(function* () {
          const db = yield* Database;

          const user = yield* db.users.create({
            data: {
              email: "update-test@example.com",
              name: "Update Test User",
            },
          });

          const organization = yield* db.organizations.create({
            userId: user.id,
            data: { name: "Original Name", slug: "original-slug" },
          });

          // Update organization name and slug
          const newName = "Updated Name";
          const newSlug = "updated-slug";

          yield* db.organizations.update({
            userId: user.id,
            organizationId: organization.id,
            data: { name: newName, slug: newSlug },
          });

          // Verify updateCustomer was called with correct parameters
          assert(capturedParams !== null);
          expect(capturedParams.customerId).toBe(organization.stripeCustomerId);
          expect(capturedParams.organizationName).toBe(newName);
          expect(capturedParams.organizationSlug).toBe(newSlug);
        }).pipe(
          Effect.provide(
            Database.Default.pipe(
              Layer.provideMerge(TestDrizzleORM),
              Layer.provide(
                new MockStripe().customers
                  .create(() => ({ id: "cus_mock" }))
                  .customers.retrieve(() => ({
                    id: "cus_mock",
                    metadata: {
                      organizationId: "org-id",
                      organizationName: "Original Name",
                      organizationSlug: "original-slug",
                    },
                  }))
                  .customers.update(
                    (
                      id: string,
                      params: {
                        name?: string;
                        metadata?: Record<string, string>;
                      },
                    ) => {
                      capturedParams = {
                        customerId: id,
                        organizationName: params.name,
                        organizationSlug: params.metadata?.organizationSlug,
                      };
                      return { id };
                    },
                  )
                  .build(),
              ),
            ),
          ),
        );
      },
    );
  });

  // ===========================================================================
  // delete
  // ===========================================================================

  describe("delete", () => {
    it.effect("deletes an organization", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        // Create a new organization to delete
        const user = yield* db.users.create({
          data: { email: "delete-test@example.com", name: "Delete Test User" },
        });

        const org = yield* db.organizations.create({
          userId: user.id,
          data: {
            name: "Organization To Delete",
            slug: "organization-to-delete",
          },
        });

        yield* db.organizations.delete({
          userId: user.id,
          organizationId: org.id,
        });

        // Verify it's gone
        const result = yield* db.organizations
          .findById({ userId: user.id, organizationId: org.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
      }),
    );

    it.effect(
      "returns `PermissionDeniedError` when ADMIN tries to delete",
      () =>
        Effect.gen(function* () {
          const { org, admin } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations
            .delete({ userId: admin.id, organizationId: org.id })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to delete this organization",
          );
        }),
    );

    it.effect(
      "returns `PermissionDeniedError` when MEMBER tries to delete",
      () =>
        Effect.gen(function* () {
          const { org, member } = yield* TestOrganizationFixture;
          const db = yield* Database;

          const result = yield* db.organizations
            .delete({ userId: member.id, organizationId: org.id })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(PermissionDeniedError);
          expect(result.message).toBe(
            "You do not have permission to delete this organization",
          );
        }),
    );

    it.effect("returns `NotFoundError` when user is not a member", () =>
      Effect.gen(function* () {
        const { org, nonMember } = yield* TestOrganizationFixture;
        const db = yield* Database;

        const result = yield* db.organizations
          .delete({ userId: nonMember.id, organizationId: org.id })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe("Organization not found");
      }),
    );

    it.effect("returns `DatabaseError` when getRole fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .delete({ userId: "user-id", organizationId: "org-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to get membership");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // getRole -> getMembership: fails
            .select(new Error("Connection failed"))
            .build(),
        ),
      ),
    );

    it.effect("returns `DatabaseError` when delete fails", () =>
      Effect.gen(function* () {
        const db = yield* Database;

        const result = yield* db.organizations
          .delete({ userId: "user-id", organizationId: "org-id" })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(DatabaseError);
        expect(result.message).toBe("Failed to delete organization");
      }).pipe(
        Effect.provide(
          new MockDrizzleORM()
            // authorize -> getRole -> memberships.findById
            //   -> authorize -> getRole -> getMembership
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "user-id",
                createdAt: new Date(),
              },
            ])
            //   -> findById actual query
            .select([
              {
                role: "OWNER",
                organizationId: "org-id",
                memberId: "user-id",
                createdAt: new Date(),
              },
            ])
            // delete: fails
            .delete(new Error("Connection failed"))
            .build(),
        ),
      ),
    );
  });
});
