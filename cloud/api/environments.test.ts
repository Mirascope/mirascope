import { Effect, Schema } from "effect";
import { describe, it, expect, TestApiContext } from "@/tests/api";
import { CreateEnvironmentRequestSchema } from "@/api/environments.schemas";
import type { PublicEnvironment, PublicProject } from "@/db/schema";
import { ParseError } from "effect/ParseResult";

describe("CreateEnvironmentRequestSchema validation", () => {
  it("rejects empty name", () => {
    expect(() =>
      Schema.decodeUnknownSync(CreateEnvironmentRequestSchema)({
        name: "",
        slug: "test-env",
      }),
    ).toThrow("Environment name is required");
  });

  it("rejects name > 100 chars", () => {
    const longName = "a".repeat(101);
    expect(() =>
      Schema.decodeUnknownSync(CreateEnvironmentRequestSchema)({
        name: longName,
        slug: "test-env",
      }),
    ).toThrow("Environment name must be at most 100 characters");
  });

  it("accepts valid name", () => {
    const result = Schema.decodeUnknownSync(CreateEnvironmentRequestSchema)({
      name: "Valid Environment Name",
      slug: "valid-env",
    });
    expect(result.name).toBe("Valid Environment Name");
  });
});

describe.sequential("Environments API", (it) => {
  let project: PublicProject;
  let environment: PublicEnvironment;

  it.effect(
    "POST /organizations/:organizationId/projects - create project for environment tests",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        project = yield* client.projects.create({
          path: { organizationId: org.id },
          payload: {
            name: "Environment Test Project",
            slug: "environment-test-project",
          },
        });
        expect(project.id).toBeDefined();
      }),
  );

  it.effect(
    "GET /organizations/:organizationId/projects/:projectId/environments - list environments (initially empty)",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const environments = yield* client.environments.list({
          path: { organizationId: org.id, projectId: project.id },
        });
        expect(Array.isArray(environments)).toBe(true);
        expect(environments).toHaveLength(0);
      }),
  );

  it.effect(
    "POST /organizations/:organizationId/projects/:projectId/environments - create environment",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        environment = yield* client.environments.create({
          path: { organizationId: org.id, projectId: project.id },
          payload: { name: "production", slug: "production" },
        });

        expect(environment.name).toBe("production");
        expect(environment.projectId).toBe(project.id);
        expect(environment.id).toBeDefined();
      }),
  );

  it.effect(
    "POST /organizations/:organizationId/projects/:projectId/environments - rejects invalid slug pattern",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.environments
          .create({
            path: { organizationId: org.id, projectId: project.id },
            payload: { name: "Test Env", slug: "Invalid Slug!" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(ParseError);
        expect(String(result)).toContain(
          "Environment slug must start and end with a letter or number, and only contain lowercase letters, numbers, hyphens, and underscores",
        );
      }),
  );

  it.effect(
    "POST /organizations/:organizationId/projects/:projectId/environments - rejects empty name",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.environments
          .create({
            path: { organizationId: org.id, projectId: project.id },
            payload: { name: "", slug: "test-env" },
          })
          .pipe(Effect.flip);

        expect(result._tag).toBe("ParseError");
      }),
  );

  it.effect(
    "POST /organizations/:organizationId/projects/:projectId/environments - rejects name > 100 chars",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const longName = "a".repeat(101);
        const result = yield* client.environments
          .create({
            path: { organizationId: org.id, projectId: project.id },
            payload: { name: longName, slug: "test-env" },
          })
          .pipe(Effect.flip);

        expect(result._tag).toBe("ParseError");
      }),
  );

  it.effect(
    "GET /organizations/:organizationId/projects/:projectId/environments - list environments (after create)",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const environments = yield* client.environments.list({
          path: { organizationId: org.id, projectId: project.id },
        });
        expect(environments).toHaveLength(1);
        expect(environments[0].id).toBe(environment.id);
        expect(environments[0].name).toBe("production");
      }),
  );

  it.effect(
    "GET /organizations/:organizationId/projects/:projectId/environments/:environmentId - get environment",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const fetched = yield* client.environments.get({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
        });

        expect(fetched.id).toBe(environment.id);
        expect(fetched.name).toBe("production");
        expect(fetched.projectId).toBe(project.id);
      }),
  );

  it.effect(
    "PUT /organizations/:organizationId/projects/:projectId/environments/:environmentId - update environment",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const updated = yield* client.environments.update({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
          payload: { name: "staging" },
        });

        expect(updated.id).toBe(environment.id);
        expect(updated.name).toBe("staging");
        expect(updated.projectId).toBe(project.id);
      }),
  );

  it.effect(
    "DELETE /organizations/:organizationId/projects/:projectId/environments/:environmentId - delete environment",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        yield* client.environments.delete({
          path: {
            organizationId: org.id,
            projectId: project.id,
            environmentId: environment.id,
          },
        });

        // Verify it's gone by listing and checking it's not there
        const environments = yield* client.environments.list({
          path: { organizationId: org.id, projectId: project.id },
        });
        const found = environments.find((e) => e.id === environment.id);
        expect(found).toBeUndefined();
      }),
  );

  it.effect(
    "DELETE /organizations/:organizationId/projects/:projectId - cleanup project",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        yield* client.projects.delete({
          path: { organizationId: org.id, projectId: project.id },
        });
      }),
  );
});
