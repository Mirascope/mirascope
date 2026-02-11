import { Effect, Schema } from "effect";

import type { PublicClaw } from "@/db/schema";

import {
  ClawRoleSchema,
  ClawMemberWithUserSchema,
  AddClawMemberRequestSchema,
  UpdateClawMemberRoleRequestSchema,
  ClawMembershipResponseSchema,
} from "@/api/claw-memberships.schemas";
import { describe, it, expect, TestApiContext } from "@/tests/api";

describe("ClawRoleSchema validation", () => {
  it("accepts ADMIN role", () => {
    const result = Schema.decodeUnknownSync(ClawRoleSchema)("ADMIN");
    expect(result).toBe("ADMIN");
  });

  it("accepts DEVELOPER role", () => {
    const result = Schema.decodeUnknownSync(ClawRoleSchema)("DEVELOPER");
    expect(result).toBe("DEVELOPER");
  });

  it("accepts VIEWER role", () => {
    const result = Schema.decodeUnknownSync(ClawRoleSchema)("VIEWER");
    expect(result).toBe("VIEWER");
  });

  it("accepts ANNOTATOR role", () => {
    const result = Schema.decodeUnknownSync(ClawRoleSchema)("ANNOTATOR");
    expect(result).toBe("ANNOTATOR");
  });

  it("rejects invalid role", () => {
    expect(() => Schema.decodeUnknownSync(ClawRoleSchema)("OWNER")).toThrow();
    expect(() => Schema.decodeUnknownSync(ClawRoleSchema)("MEMBER")).toThrow();
  });
});

describe("AddClawMemberRequestSchema validation", () => {
  it("accepts valid request with ADMIN role", () => {
    const result = Schema.decodeUnknownSync(AddClawMemberRequestSchema)({
      memberId: "user-123",
      role: "ADMIN",
    });
    expect(result.memberId).toBe("user-123");
    expect(result.role).toBe("ADMIN");
  });

  it("accepts valid request with DEVELOPER role", () => {
    const result = Schema.decodeUnknownSync(AddClawMemberRequestSchema)({
      memberId: "user-456",
      role: "DEVELOPER",
    });
    expect(result.memberId).toBe("user-456");
    expect(result.role).toBe("DEVELOPER");
  });

  it("rejects invalid role", () => {
    expect(() =>
      Schema.decodeUnknownSync(AddClawMemberRequestSchema)({
        memberId: "user-123",
        role: "OWNER",
      }),
    ).toThrow();
  });
});

describe("UpdateClawMemberRoleRequestSchema validation", () => {
  it("accepts valid role update", () => {
    const result = Schema.decodeUnknownSync(UpdateClawMemberRoleRequestSchema)({
      role: "VIEWER",
    });
    expect(result.role).toBe("VIEWER");
  });

  it("accepts all valid roles", () => {
    for (const role of ["ADMIN", "DEVELOPER", "VIEWER", "ANNOTATOR"] as const) {
      const result = Schema.decodeUnknownSync(
        UpdateClawMemberRoleRequestSchema,
      )({ role });
      expect(result.role).toBe(role);
    }
  });

  it("rejects invalid role", () => {
    expect(() =>
      Schema.decodeUnknownSync(UpdateClawMemberRoleRequestSchema)({
        role: "MEMBER",
      }),
    ).toThrow();
  });
});

describe("ClawMemberWithUserSchema validation", () => {
  it("accepts valid member with all fields", () => {
    const result = Schema.decodeUnknownSync(ClawMemberWithUserSchema)({
      memberId: "user-123",
      email: "user@example.com",
      name: "Test User",
      role: "DEVELOPER",
      createdAt: new Date().toISOString(),
    });
    expect(result.memberId).toBe("user-123");
    expect(result.email).toBe("user@example.com");
    expect(result.name).toBe("Test User");
    expect(result.role).toBe("DEVELOPER");
  });

  it("accepts member with null name", () => {
    const result = Schema.decodeUnknownSync(ClawMemberWithUserSchema)({
      memberId: "user-123",
      email: "user@example.com",
      name: null,
      role: "ADMIN",
      createdAt: null,
    });
    expect(result.name).toBeNull();
    expect(result.createdAt).toBeNull();
  });

  it("accepts all valid roles", () => {
    for (const role of ["ADMIN", "DEVELOPER", "VIEWER", "ANNOTATOR"] as const) {
      const result = Schema.decodeUnknownSync(ClawMemberWithUserSchema)({
        memberId: "user-123",
        email: "user@example.com",
        name: null,
        role,
        createdAt: null,
      });
      expect(result.role).toBe(role);
    }
  });
});

describe("ClawMembershipResponseSchema validation", () => {
  it("accepts valid membership response", () => {
    const result = Schema.decodeUnknownSync(ClawMembershipResponseSchema)({
      memberId: "user-123",
      organizationId: "org-456",
      clawId: "claw-789",
      role: "DEVELOPER",
      createdAt: new Date().toISOString(),
    });
    expect(result.memberId).toBe("user-123");
    expect(result.organizationId).toBe("org-456");
    expect(result.clawId).toBe("claw-789");
    expect(result.role).toBe("DEVELOPER");
  });

  it("accepts response with null createdAt", () => {
    const result = Schema.decodeUnknownSync(ClawMembershipResponseSchema)({
      memberId: "user-123",
      organizationId: "org-456",
      clawId: "claw-789",
      role: "ADMIN",
      createdAt: null,
    });
    expect(result.createdAt).toBeNull();
  });
});

describe.sequential("Claw Memberships API", (it) => {
  let claw: PublicClaw;

  // First, create a claw for the membership tests
  it.effect("setup - create a claw for membership tests", () =>
    Effect.gen(function* () {
      const { client, org } = yield* TestApiContext;
      claw = yield* client.claws.create({
        path: { organizationId: org.id },
        payload: { name: "Membership Test Claw", slug: "membership-test-claw" },
      });
      expect(claw.id).toBeDefined();
    }),
  );

  // Test list endpoint
  it.effect(
    "GET /organizations/:id/claws/:id/members - lists members with user info",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const members = yield* client["claw-memberships"].list({
          path: { organizationId: org.id, clawId: claw.id },
        });

        expect(Array.isArray(members)).toBe(true);
        // The claw creator is automatically added as ADMIN
        expect(members.length).toBeGreaterThanOrEqual(1);

        // Verify member structure includes user info
        const member = members[0];
        expect(member).toHaveProperty("memberId");
        expect(member).toHaveProperty("email");
        expect(member).toHaveProperty("name");
        expect(member).toHaveProperty("role");
        expect(member).toHaveProperty("createdAt");
      }),
  );

  // Test that owner can see members (org OWNER has implicit claw ADMIN access)
  it.effect(
    "GET /organizations/:id/claws/:id/members - owner can list members",
    () =>
      Effect.gen(function* () {
        const { client, org, owner } = yield* TestApiContext;
        const members = yield* client["claw-memberships"].list({
          path: { organizationId: org.id, clawId: claw.id },
        });

        // Owner should be in the list (as claw creator)
        const ownerMember = members.find((m) => m.memberId === owner.id);
        expect(ownerMember).toBeDefined();
        expect(ownerMember?.role).toBe("ADMIN");
      }),
  );

  // Test update endpoint
  it.effect(
    "PATCH /organizations/:id/claws/:id/members/:memberId - update member role",
    () =>
      Effect.gen(function* () {
        const { client, org, owner } = yield* TestApiContext;

        // Update the owner's role to DEVELOPER
        const updated = yield* client["claw-memberships"].update({
          path: {
            organizationId: org.id,
            clawId: claw.id,
            memberId: owner.id,
          },
          payload: { role: "DEVELOPER" },
        });

        expect(updated.memberId).toBe(owner.id);
        expect(updated.role).toBe("DEVELOPER");
      }),
  );

  // Test that the role was actually updated
  it.effect(
    "GET /organizations/:id/claws/:id/members/:id - verifies role update persisted",
    () =>
      Effect.gen(function* () {
        const { client, org, owner } = yield* TestApiContext;
        const updatedMember = yield* client["claw-memberships"].get({
          path: {
            organizationId: org.id,
            clawId: claw.id,
            memberId: owner.id,
          },
        });

        expect(updatedMember?.role).toBe("DEVELOPER");
      }),
  );

  // Update back to ADMIN so we can continue with delete tests
  it.effect("PATCH - restore owner to ADMIN", () =>
    Effect.gen(function* () {
      const { client, org, owner } = yield* TestApiContext;

      const updated = yield* client["claw-memberships"].update({
        path: {
          organizationId: org.id,
          clawId: claw.id,
          memberId: owner.id,
        },
        payload: { role: "ADMIN" },
      });

      expect(updated.role).toBe("ADMIN");
    }),
  );

  // Test delete endpoint - owner can remove their own explicit claw membership
  // (they still have access via org OWNER implicit ADMIN access)
  it.effect(
    "DELETE /organizations/:id/claws/:id/members/:memberId - remove member from claw",
    () =>
      Effect.gen(function* () {
        const { client, org, owner } = yield* TestApiContext;

        // Remove owner from claw (they still have access via org role)
        yield* client["claw-memberships"].delete({
          path: {
            organizationId: org.id,
            clawId: claw.id,
            memberId: owner.id,
          },
        });

        // Verify they're removed from explicit membership list
        const members = yield* client["claw-memberships"].list({
          path: { organizationId: org.id, clawId: claw.id },
        });

        const ownerMember = members.find((m) => m.memberId === owner.id);
        expect(ownerMember).toBeUndefined();
      }),
  );

  // Test create endpoint - add owner back to claw as explicit member
  it.effect(
    "POST /organizations/:id/claws/:id/members - add member to claw",
    () =>
      Effect.gen(function* () {
        const { client, org, owner } = yield* TestApiContext;

        // Add owner back as explicit DEVELOPER
        const membership = yield* client["claw-memberships"].create({
          path: { organizationId: org.id, clawId: claw.id },
          payload: { memberId: owner.id, role: "DEVELOPER" },
        });

        expect(membership.memberId).toBe(owner.id);
        expect(membership.clawId).toBe(claw.id);
        expect(membership.role).toBe("DEVELOPER");
      }),
  );

  // Verify the create persisted
  it.effect(
    "GET /organizations/:id/claws/:id/members - verifies member was added",
    () =>
      Effect.gen(function* () {
        const { client, org, owner } = yield* TestApiContext;
        const members = yield* client["claw-memberships"].list({
          path: { organizationId: org.id, clawId: claw.id },
        });

        const ownerMember = members.find((m) => m.memberId === owner.id);
        expect(ownerMember).toBeDefined();
        expect(ownerMember?.role).toBe("DEVELOPER");
      }),
  );

  // Restore ADMIN role for cleanup
  it.effect("restore ADMIN role for claw cleanup", () =>
    Effect.gen(function* () {
      const { client, org, owner } = yield* TestApiContext;
      yield* client["claw-memberships"].update({
        path: {
          organizationId: org.id,
          clawId: claw.id,
          memberId: owner.id,
        },
        payload: { role: "ADMIN" },
      });
    }),
  );

  // Cleanup - delete the claw
  it.effect("cleanup - delete test claw", () =>
    Effect.gen(function* () {
      const { client, org } = yield* TestApiContext;
      yield* client.claws.delete({
        path: { organizationId: org.id, clawId: claw.id },
      });

      // Verify it's gone
      const claws = yield* client.claws.list({
        path: { organizationId: org.id },
      });
      const found = claws.find((c) => c.id === claw.id);
      expect(found).toBeUndefined();
    }),
  );
});
