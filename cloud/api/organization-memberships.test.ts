import { Effect, Schema } from "effect";
import { describe, it, expect, TestApiContext } from "@/tests/api";
import {
  UpdateMemberRoleRequestSchema,
  OrganizationMemberWithUserSchema,
  MembershipResponseSchema,
} from "@/api/organization-memberships.schemas";

describe("UpdateMemberRoleRequestSchema validation", () => {
  it("accepts ADMIN role", () => {
    const result = Schema.decodeUnknownSync(UpdateMemberRoleRequestSchema)({
      role: "ADMIN",
    });
    expect(result.role).toBe("ADMIN");
  });

  it("accepts MEMBER role", () => {
    const result = Schema.decodeUnknownSync(UpdateMemberRoleRequestSchema)({
      role: "MEMBER",
    });
    expect(result.role).toBe("MEMBER");
  });

  it("rejects OWNER role", () => {
    expect(() =>
      Schema.decodeUnknownSync(UpdateMemberRoleRequestSchema)({
        role: "OWNER",
      }),
    ).toThrow();
  });

  it("rejects invalid role", () => {
    expect(() =>
      Schema.decodeUnknownSync(UpdateMemberRoleRequestSchema)({
        role: "VIEWER",
      }),
    ).toThrow();
  });
});

describe("OrganizationMemberWithUserSchema validation", () => {
  it("accepts valid member with all fields", () => {
    const result = Schema.decodeUnknownSync(OrganizationMemberWithUserSchema)({
      memberId: "user-123",
      email: "user@example.com",
      name: "Test User",
      role: "MEMBER",
      createdAt: new Date().toISOString(),
    });
    expect(result.memberId).toBe("user-123");
    expect(result.email).toBe("user@example.com");
    expect(result.name).toBe("Test User");
    expect(result.role).toBe("MEMBER");
  });

  it("accepts member with null name", () => {
    const result = Schema.decodeUnknownSync(OrganizationMemberWithUserSchema)({
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
    for (const role of ["OWNER", "ADMIN", "MEMBER"] as const) {
      const result = Schema.decodeUnknownSync(OrganizationMemberWithUserSchema)(
        {
          memberId: "user-123",
          email: "user@example.com",
          name: null,
          role,
          createdAt: null,
        },
      );
      expect(result.role).toBe(role);
    }
  });
});

describe("MembershipResponseSchema validation", () => {
  it("accepts valid membership response", () => {
    const result = Schema.decodeUnknownSync(MembershipResponseSchema)({
      memberId: "user-123",
      role: "MEMBER",
      createdAt: new Date().toISOString(),
    });
    expect(result.memberId).toBe("user-123");
    expect(result.role).toBe("MEMBER");
  });
});

describe.sequential("Organization Memberships API", (it) => {
  // Test list endpoint
  it.effect(
    "GET /organizations/:id/members - lists members with user info",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const members = yield* client["organization-memberships"].list({
          path: { organizationId: org.id },
        });

        expect(Array.isArray(members)).toBe(true);
        // Should have at least the owner
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

  // Test update endpoint - permission checks
  it.effect(
    "PATCH /organizations/:id/members/:memberId - returns 403 when trying to change OWNER role",
    () =>
      Effect.gen(function* () {
        const { client, org, owner } = yield* TestApiContext;

        // Try to change the owner's role (the test user is the owner)
        const result = yield* client["organization-memberships"]
          .update({
            path: { organizationId: org.id, memberId: owner.id },
            payload: { role: "MEMBER" },
          })
          .pipe(Effect.flip);

        expect(result._tag).toBe("PermissionDeniedError");
      }),
  );

  // Test delete endpoint - permission checks
  it.effect(
    "DELETE /organizations/:id/members/:memberId - returns 403 when owner tries to remove self",
    () =>
      Effect.gen(function* () {
        const { client, org, owner } = yield* TestApiContext;

        // Try to remove self as owner
        const result = yield* client["organization-memberships"]
          .delete({
            path: { organizationId: org.id, memberId: owner.id },
          })
          .pipe(Effect.flip);

        expect(result._tag).toBe("PermissionDeniedError");
      }),
  );
});
