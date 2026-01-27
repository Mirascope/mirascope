import { Effect, Schema } from "effect";
import { describe, it, expect, TestApiContext } from "@/tests/api";
import {
  ProjectRoleSchema,
  ProjectMemberWithUserSchema,
  AddProjectMemberRequestSchema,
  UpdateProjectMemberRoleRequestSchema,
  ProjectMembershipResponseSchema,
} from "@/api/project-memberships.schemas";
import type { PublicProject } from "@/db/schema";

describe("ProjectRoleSchema validation", () => {
  it("accepts ADMIN role", () => {
    const result = Schema.decodeUnknownSync(ProjectRoleSchema)("ADMIN");
    expect(result).toBe("ADMIN");
  });

  it("accepts DEVELOPER role", () => {
    const result = Schema.decodeUnknownSync(ProjectRoleSchema)("DEVELOPER");
    expect(result).toBe("DEVELOPER");
  });

  it("accepts VIEWER role", () => {
    const result = Schema.decodeUnknownSync(ProjectRoleSchema)("VIEWER");
    expect(result).toBe("VIEWER");
  });

  it("accepts ANNOTATOR role", () => {
    const result = Schema.decodeUnknownSync(ProjectRoleSchema)("ANNOTATOR");
    expect(result).toBe("ANNOTATOR");
  });

  it("rejects invalid role", () => {
    expect(() =>
      Schema.decodeUnknownSync(ProjectRoleSchema)("OWNER"),
    ).toThrow();
    expect(() =>
      Schema.decodeUnknownSync(ProjectRoleSchema)("MEMBER"),
    ).toThrow();
  });
});

describe("AddProjectMemberRequestSchema validation", () => {
  it("accepts valid request with ADMIN role", () => {
    const result = Schema.decodeUnknownSync(AddProjectMemberRequestSchema)({
      memberId: "user-123",
      role: "ADMIN",
    });
    expect(result.memberId).toBe("user-123");
    expect(result.role).toBe("ADMIN");
  });

  it("accepts valid request with DEVELOPER role", () => {
    const result = Schema.decodeUnknownSync(AddProjectMemberRequestSchema)({
      memberId: "user-456",
      role: "DEVELOPER",
    });
    expect(result.memberId).toBe("user-456");
    expect(result.role).toBe("DEVELOPER");
  });

  it("rejects invalid role", () => {
    expect(() =>
      Schema.decodeUnknownSync(AddProjectMemberRequestSchema)({
        memberId: "user-123",
        role: "OWNER",
      }),
    ).toThrow();
  });
});

describe("UpdateProjectMemberRoleRequestSchema validation", () => {
  it("accepts valid role update", () => {
    const result = Schema.decodeUnknownSync(
      UpdateProjectMemberRoleRequestSchema,
    )({
      role: "VIEWER",
    });
    expect(result.role).toBe("VIEWER");
  });

  it("accepts all valid roles", () => {
    for (const role of ["ADMIN", "DEVELOPER", "VIEWER", "ANNOTATOR"] as const) {
      const result = Schema.decodeUnknownSync(
        UpdateProjectMemberRoleRequestSchema,
      )({ role });
      expect(result.role).toBe(role);
    }
  });

  it("rejects invalid role", () => {
    expect(() =>
      Schema.decodeUnknownSync(UpdateProjectMemberRoleRequestSchema)({
        role: "MEMBER",
      }),
    ).toThrow();
  });
});

describe("ProjectMemberWithUserSchema validation", () => {
  it("accepts valid member with all fields", () => {
    const result = Schema.decodeUnknownSync(ProjectMemberWithUserSchema)({
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
    const result = Schema.decodeUnknownSync(ProjectMemberWithUserSchema)({
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
      const result = Schema.decodeUnknownSync(ProjectMemberWithUserSchema)({
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

describe("ProjectMembershipResponseSchema validation", () => {
  it("accepts valid membership response", () => {
    const result = Schema.decodeUnknownSync(ProjectMembershipResponseSchema)({
      memberId: "user-123",
      organizationId: "org-456",
      projectId: "proj-789",
      role: "DEVELOPER",
      createdAt: new Date().toISOString(),
    });
    expect(result.memberId).toBe("user-123");
    expect(result.organizationId).toBe("org-456");
    expect(result.projectId).toBe("proj-789");
    expect(result.role).toBe("DEVELOPER");
  });

  it("accepts response with null createdAt", () => {
    const result = Schema.decodeUnknownSync(ProjectMembershipResponseSchema)({
      memberId: "user-123",
      organizationId: "org-456",
      projectId: "proj-789",
      role: "ADMIN",
      createdAt: null,
    });
    expect(result.createdAt).toBeNull();
  });
});

describe.sequential("Project Memberships API", (it) => {
  let project: PublicProject;

  // First, create a project for the membership tests
  it.effect("setup - create a project for membership tests", () =>
    Effect.gen(function* () {
      const { client, org } = yield* TestApiContext;
      project = yield* client.projects.create({
        path: { organizationId: org.id },
        payload: { name: "Test Project", slug: "membership-test-project" },
      });
      expect(project.id).toBeDefined();
    }),
  );

  // Test list endpoint
  it.effect(
    "GET /organizations/:id/projects/:id/members - lists members with user info",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const members = yield* client["project-memberships"].list({
          path: { organizationId: org.id, projectId: project.id },
        });

        expect(Array.isArray(members)).toBe(true);
        // The project creator is automatically added as ADMIN
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

  // Test that owner can see members (org OWNER has implicit project ADMIN access)
  it.effect(
    "GET /organizations/:id/projects/:id/members - owner can list members",
    () =>
      Effect.gen(function* () {
        const { client, org, owner } = yield* TestApiContext;
        const members = yield* client["project-memberships"].list({
          path: { organizationId: org.id, projectId: project.id },
        });

        // Owner should be in the list (as project creator)
        const ownerMember = members.find((m) => m.memberId === owner.id);
        expect(ownerMember).toBeDefined();
        expect(ownerMember?.role).toBe("ADMIN");
      }),
  );

  // Test update endpoint
  it.effect(
    "PATCH /organizations/:id/projects/:id/members/:memberId - update member role",
    () =>
      Effect.gen(function* () {
        const { client, org, owner } = yield* TestApiContext;

        // Update the owner's role to DEVELOPER
        const updated = yield* client["project-memberships"].update({
          path: {
            organizationId: org.id,
            projectId: project.id,
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
    "GET /organizations/:id/projects/:id/members/:id - verifies role update persisted",
    () =>
      Effect.gen(function* () {
        const { client, org, owner } = yield* TestApiContext;
        const updatedMember = yield* client["project-memberships"].get({
          path: {
            organizationId: org.id,
            projectId: project.id,
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

      const updated = yield* client["project-memberships"].update({
        path: {
          organizationId: org.id,
          projectId: project.id,
          memberId: owner.id,
        },
        payload: { role: "ADMIN" },
      });

      expect(updated.role).toBe("ADMIN");
    }),
  );

  // Test delete endpoint - owner can remove their own explicit project membership
  // (they still have access via org OWNER implicit ADMIN access)
  it.effect(
    "DELETE /organizations/:id/projects/:id/members/:memberId - remove member from project",
    () =>
      Effect.gen(function* () {
        const { client, org, owner } = yield* TestApiContext;

        // Remove owner from project (they still have access via org role)
        yield* client["project-memberships"].delete({
          path: {
            organizationId: org.id,
            projectId: project.id,
            memberId: owner.id,
          },
        });

        // Verify they're removed from explicit membership list
        const members = yield* client["project-memberships"].list({
          path: { organizationId: org.id, projectId: project.id },
        });

        const ownerMember = members.find((m) => m.memberId === owner.id);
        expect(ownerMember).toBeUndefined();
      }),
  );

  // Test create endpoint - add owner back to project as explicit member
  it.effect(
    "POST /organizations/:id/projects/:id/members - add member to project",
    () =>
      Effect.gen(function* () {
        const { client, org, owner } = yield* TestApiContext;

        // Add owner back as explicit DEVELOPER
        const membership = yield* client["project-memberships"].create({
          path: { organizationId: org.id, projectId: project.id },
          payload: { memberId: owner.id, role: "DEVELOPER" },
        });

        expect(membership.memberId).toBe(owner.id);
        expect(membership.projectId).toBe(project.id);
        expect(membership.role).toBe("DEVELOPER");
      }),
  );

  // Verify the create persisted
  it.effect(
    "GET /organizations/:id/projects/:id/members - verifies member was added",
    () =>
      Effect.gen(function* () {
        const { client, org, owner } = yield* TestApiContext;
        const members = yield* client["project-memberships"].list({
          path: { organizationId: org.id, projectId: project.id },
        });

        const ownerMember = members.find((m) => m.memberId === owner.id);
        expect(ownerMember).toBeDefined();
        expect(ownerMember?.role).toBe("DEVELOPER");
      }),
  );

  // Restore ADMIN role for cleanup
  it.effect("restore ADMIN role for project cleanup", () =>
    Effect.gen(function* () {
      const { client, org, owner } = yield* TestApiContext;
      yield* client["project-memberships"].update({
        path: {
          organizationId: org.id,
          projectId: project.id,
          memberId: owner.id,
        },
        payload: { role: "ADMIN" },
      });
    }),
  );

  // Cleanup - delete the project
  it.effect("cleanup - delete test project", () =>
    Effect.gen(function* () {
      const { client, org } = yield* TestApiContext;
      yield* client.projects.delete({
        path: { organizationId: org.id, projectId: project.id },
      });

      // Verify it's gone
      const projects = yield* client.projects.list({
        path: { organizationId: org.id },
      });
      const found = projects.find((p) => p.id === project.id);
      expect(found).toBeUndefined();
    }),
  );
});
