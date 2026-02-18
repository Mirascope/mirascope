import { eq } from "drizzle-orm";
import { Effect, Layer, Schema } from "effect";
import { ParseError } from "effect/ParseResult";

import type { PublicClaw } from "@/db/schema";

import { Analytics } from "@/analytics";
import {
  resolveClawHandler,
  bootstrapClawHandler,
  reportClawStatusHandler,
  validateSessionHandler,
} from "@/api/claws-internal.handlers";
import {
  createClawHandler,
  deleteClawHandler,
  restartClawHandler,
  CreateClawRequestSchema,
} from "@/api/claws.handlers";
import { AuthenticatedUser } from "@/auth";
import { encryptSecrets } from "@/claws/crypto";
import { ClawDeploymentError } from "@/claws/deployment/errors";
import { DrizzleORM } from "@/db/client";
import { Database } from "@/db/database";
import { claws } from "@/db/schema";
import {
  DatabaseError,
  NotFoundError,
  PermissionDeniedError,
  UnauthorizedError,
} from "@/errors";
import { describe, it, expect, TestApiContext } from "@/tests/api";
import { MockClawDeployment } from "@/tests/clawDeployment";
import { MockSettingsLayer } from "@/tests/settings";

describe("CreateClawRequestSchema validation", () => {
  it("rejects empty name", () => {
    expect(() =>
      Schema.decodeUnknownSync(CreateClawRequestSchema)({
        name: "",
        slug: "test-claw",
      }),
    ).toThrow("Claw name is required");
  });

  it("rejects name > 100 chars", () => {
    const longName = "a".repeat(101);
    expect(() =>
      Schema.decodeUnknownSync(CreateClawRequestSchema)({
        name: longName,
        slug: "test-claw",
      }),
    ).toThrow("Claw name must be at most 100 characters");
  });

  it("accepts valid name", () => {
    const result = Schema.decodeUnknownSync(CreateClawRequestSchema)({
      name: "Valid Claw Name",
      slug: "valid-claw",
    });
    expect(result.name).toBe("Valid Claw Name");
  });
});

describe("Internal handlers", () => {
  it.effect("resolveClawHandler returns NotFoundError for unknown slugs", () =>
    Effect.gen(function* () {
      const error = yield* resolveClawHandler(
        "no-such-org",
        "no-such-claw",
      ).pipe(Effect.flip);
      expect(error).toBeInstanceOf(NotFoundError);
    }),
  );

  it.effect(
    "bootstrapClawHandler returns NotFoundError for unknown clawId",
    () =>
      Effect.gen(function* () {
        const error = yield* bootstrapClawHandler(
          "00000000-0000-0000-0000-000000000000",
        ).pipe(Effect.flip);
        expect(error).toBeInstanceOf(NotFoundError);
      }),
  );

  it.effect(
    "reportClawStatusHandler returns NotFoundError for unknown clawId",
    () =>
      Effect.gen(function* () {
        const error = yield* reportClawStatusHandler(
          "00000000-0000-0000-0000-000000000000",
          { status: "active" },
        ).pipe(Effect.flip);
        expect(error).toBeInstanceOf(NotFoundError);
      }),
  );
});

describe.sequential("Claws API", (it) => {
  let claw: any;

  it.effect(
    "GET /organizations/:organizationId/claws - list claws (initially empty)",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const claws = yield* client.claws.list({
          path: { organizationId: org.id },
        });
        expect(Array.isArray(claws)).toBe(true);
        expect(claws).toHaveLength(0);
      }),
  );

  it.effect("POST /organizations/:organizationId/claws - create claw", () =>
    Effect.gen(function* () {
      const { client, org } = yield* TestApiContext;
      claw = yield* client.claws.create({
        path: { organizationId: org.id },
        payload: { name: "Test Claw", slug: "test-claw" },
      });

      expect(claw.displayName).toBe("Test Claw");
      expect(claw.slug).toBe("test-claw");
      expect(claw.organizationId).toBe(org.id);
      expect(claw.createdByUserId).toBeDefined();
      expect(claw.id).toBeDefined();
      // Provisioning sets status and persists Mac deployment info
      expect(claw.status).toBe("provisioning");
      expect(claw.macId).toBeDefined();
      expect(claw.secretsEncrypted).toBeDefined();
    }),
  );

  it.effect(
    "POST /organizations/:organizationId/claws - rejects invalid slug pattern",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.claws
          .create({
            path: { organizationId: org.id },
            payload: { name: "Test Claw", slug: "Invalid Slug!" },
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(ParseError);
        expect(result.message).toContain(
          "Claw slug must start and end with a letter or number, and only contain lowercase letters, numbers, hyphens, and underscores",
        );
      }),
  );

  it.effect(
    "POST /organizations/:organizationId/claws - rejects empty name",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const result = yield* client.claws
          .create({
            path: { organizationId: org.id },
            payload: { name: "", slug: "test-claw-2" },
          })
          .pipe(Effect.flip);

        expect(result._tag).toBe("ParseError");
      }),
  );

  it.effect(
    "POST /organizations/:organizationId/claws - rejects name > 100 chars",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const longName = "a".repeat(101);
        const result = yield* client.claws
          .create({
            path: { organizationId: org.id },
            payload: { name: longName, slug: "test-claw-3" },
          })
          .pipe(Effect.flip);

        expect(result._tag).toBe("ParseError");
      }),
  );

  it.effect(
    "GET /organizations/:organizationId/claws - list claws (after create)",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const claws = yield* client.claws.list({
          path: { organizationId: org.id },
        });
        expect(claws).toHaveLength(1);
        expect(claws[0].id).toBe(claw.id);
        expect(claws[0].displayName).toBe("Test Claw");
      }),
  );

  it.effect("GET /organizations/:organizationId/claws/:clawId - get claw", () =>
    Effect.gen(function* () {
      const { client, org } = yield* TestApiContext;
      const fetched = yield* client.claws.get({
        path: { organizationId: org.id, clawId: claw.id },
      });

      expect(fetched.id).toBe(claw.id);
      expect(fetched.displayName).toBe("Test Claw");
      expect(fetched.organizationId).toBe(org.id);
    }),
  );

  it.effect(
    "PUT /organizations/:organizationId/claws/:clawId - update claw",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const updated = yield* client.claws.update({
          path: { organizationId: org.id, clawId: claw.id },
          payload: { name: "Updated Claw Name" },
        });

        expect(updated.id).toBe(claw.id);
        expect(updated.displayName).toBe("Updated Claw Name");
        expect(updated.organizationId).toBe(org.id);
      }),
  );

  it.effect(
    "POST /organizations/:organizationId/claws - create claw with spending guardrail",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const created = yield* client.claws.create({
          path: { organizationId: org.id },
          payload: {
            name: "Guardrail Claw",
            slug: "guardrail-claw",
            weeklySpendingGuardrailCenticents: 50000n,
          },
        });

        expect(created.displayName).toBe("Guardrail Claw");
        expect(created.weeklySpendingGuardrailCenticents).toBe(50000n);

        // Clean up
        yield* client.claws.delete({
          path: { organizationId: org.id, clawId: created.id },
        });
      }),
  );

  it.effect(
    "POST /organizations/:organizationId/claws - create claw with existing project",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;

        // Create a project to use as the home project
        const project = yield* client.projects.create({
          path: { organizationId: org.id },
          payload: { name: "Existing Project", slug: "existing-project" },
        });

        const created = yield* client.claws.create({
          path: { organizationId: org.id },
          payload: {
            name: "Linked Claw",
            slug: "linked-claw",
            homeProjectId: project.id,
          },
        });

        expect(created.displayName).toBe("Linked Claw");
        expect(created.homeProjectId).toBe(project.id);

        // Clean up
        yield* client.claws.delete({
          path: { organizationId: org.id, clawId: created.id },
        });
        yield* client.projects.delete({
          path: { organizationId: org.id, projectId: project.id },
        });
      }),
  );

  it.effect(
    "PUT /organizations/:organizationId/claws/:clawId - set spending guardrail",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const updated = yield* client.claws.update({
          path: { organizationId: org.id, clawId: claw.id },
          payload: { weeklySpendingGuardrailCenticents: 50000n },
        });

        expect(updated.id).toBe(claw.id);
        expect(updated.weeklySpendingGuardrailCenticents).toBe(50000n);
      }),
  );

  it.effect(
    "PUT /organizations/:organizationId/claws/:clawId - update spending guardrail",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const updated = yield* client.claws.update({
          path: { organizationId: org.id, clawId: claw.id },
          payload: { weeklySpendingGuardrailCenticents: 100000n },
        });

        expect(updated.id).toBe(claw.id);
        expect(updated.weeklySpendingGuardrailCenticents).toBe(100000n);
      }),
  );

  it.effect(
    "PUT /organizations/:organizationId/claws/:clawId - clear spending guardrail",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const updated = yield* client.claws.update({
          path: { organizationId: org.id, clawId: claw.id },
          payload: { weeklySpendingGuardrailCenticents: null },
        });

        expect(updated.id).toBe(claw.id);
        expect(updated.weeklySpendingGuardrailCenticents).toBeNull();
      }),
  );

  it.effect(
    "GET /organizations/:organizationId/claws/:clawId/usage - get usage",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const usage = yield* client.claws.getUsage({
          path: { organizationId: org.id, clawId: claw.id },
        });

        expect(usage.weeklyUsageCenticents).toBe(0n);
        expect(usage.burstUsageCenticents).toBe(0n);
        expect(usage.weeklySpendingGuardrailCenticents).toBeNull();
        expect(usage.poolUsageCenticents).toBe(0n);
        expect(usage.poolLimitCenticents).toBeGreaterThan(0);
        expect(usage.poolPercentUsed).toBe(0);
      }),
  );

  it.effect(
    "GET /organizations/:organizationId/claws/:clawId/secrets - get secrets (provisioned secrets)",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const secrets = yield* client.claws.getSecrets({
          path: { organizationId: org.id, clawId: claw.id },
        });
        // Provisioning stores gateway token and API key as secrets
        expect(secrets.OPENCLAW_GATEWAY_TOKEN).toBeDefined();
        expect(secrets.ANTHROPIC_API_KEY).toBeDefined();
      }),
  );

  it.effect(
    "PUT /organizations/:organizationId/claws/:clawId/secrets - set secrets",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const updated = yield* client.claws.updateSecrets({
          path: { organizationId: org.id, clawId: claw.id },
          payload: { API_KEY: "test-key", DB_URL: "postgres://localhost" },
        });
        expect(updated).toEqual({
          API_KEY: "test-key",
          DB_URL: "postgres://localhost",
        });
      }),
  );

  it.effect(
    "GET /organizations/:organizationId/claws/:clawId/secrets - get secrets (after set)",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const secrets = yield* client.claws.getSecrets({
          path: { organizationId: org.id, clawId: claw.id },
        });
        expect(secrets).toEqual({
          API_KEY: "test-key",
          DB_URL: "postgres://localhost",
        });
      }),
  );

  it.effect(
    "PUT /organizations/:organizationId/claws/:clawId/secrets - overwrite secrets",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        const updated = yield* client.claws.updateSecrets({
          path: { organizationId: org.id, clawId: claw.id },
          payload: { NEW_KEY: "new-value" },
        });
        expect(updated).toEqual({ NEW_KEY: "new-value" });

        // Verify old secrets are gone
        const secrets = yield* client.claws.getSecrets({
          path: { organizationId: org.id, clawId: claw.id },
        });
        expect(secrets).toEqual({ NEW_KEY: "new-value" });
      }),
  );

  it.effect(
    "POST /organizations/:organizationId/claws/:clawId/restart - restart claw",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        yield* client.claws.restart({
          path: { organizationId: org.id, clawId: claw.id },
        });
      }),
  );

  it.effect(
    "DELETE /organizations/:organizationId/claws/:clawId - delete claw",
    () =>
      Effect.gen(function* () {
        const { client, org } = yield* TestApiContext;
        yield* client.claws.delete({
          path: { organizationId: org.id, clawId: claw.id },
        });

        // Verify it's gone by listing and checking it's not there
        const claws = yield* client.claws.list({
          path: { organizationId: org.id },
        });
        const found = claws.find((c) => c.id === claw.id);
        expect(found).toBeUndefined();
      }),
  );
});

// ---------------------------------------------------------------------------
// Internal handler integration tests
// ---------------------------------------------------------------------------

/**
 * Creates a user, organization, and claw for internal handler tests.
 * Returns the org and claw so handlers can be tested against real DB rows.
 */
const createTestFixture = Effect.gen(function* () {
  const db = yield* Database;

  const user = yield* db.users.create({
    data: {
      email: `internal-handler-${Date.now()}@example.com`,
      name: "Handler Test User",
    },
  });

  const org = yield* db.organizations.create({
    userId: user.id,
    data: {
      name: "Handler Test Org",
      slug: `handler-test-${Date.now()}`,
    },
  });

  const claw = yield* db.organizations.claws.create({
    userId: user.id,
    organizationId: org.id,
    data: {
      slug: "handler-claw",
      displayName: "Handler Test Claw",
    },
  });

  return { user, org, claw };
});

describe("Internal handler database errors", () => {
  const failingSelect = () => {
    const fail = Effect.fail({ _tag: "SqlError", cause: new Error("db down") });
    const chain = (): unknown =>
      new Proxy(fail, {
        get: (target, prop) => {
          if (prop === "pipe")
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            return (...fns: Array<(e: any) => any>) =>
              fns.reduce((acc, fn) => fn(acc), fail);
          if (
            typeof prop === "string" &&
            ["from", "where", "limit", "innerJoin"].includes(prop)
          )
            return () => chain();
          return Reflect.get(target, prop);
        },
      });
    return chain();
  };

  const failingUpdate = () => {
    const fail = Effect.fail({ _tag: "SqlError", cause: new Error("db down") });
    const chain = (): unknown =>
      new Proxy(fail, {
        get: (target, prop) => {
          if (prop === "pipe")
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            return (...fns: Array<(e: any) => any>) =>
              fns.reduce((acc, fn) => fn(acc), fail);
          if (
            typeof prop === "string" &&
            ["set", "where", "returning"].includes(prop)
          )
            return () => chain();
          return Reflect.get(target, prop);
        },
      });
    return chain();
  };

  it.effect("resolveClawHandler returns DatabaseError when query fails", () =>
    Effect.gen(function* () {
      const error = yield* resolveClawHandler("org", "claw").pipe(
        Effect.flip,
        Effect.provide(
          Layer.succeed(DrizzleORM, {
            select: () => failingSelect(),
          } as never),
        ),
      );
      expect(error).toBeInstanceOf(DatabaseError);
      expect((error as DatabaseError).message).toBe("Failed to resolve claw");
    }),
  );

  it.effect("bootstrapClawHandler returns DatabaseError when query fails", () =>
    Effect.gen(function* () {
      const error = yield* bootstrapClawHandler("some-id").pipe(
        Effect.flip,
        Effect.provide(
          Layer.mergeAll(
            Layer.succeed(DrizzleORM, {
              select: () => failingSelect(),
            } as never),
            MockSettingsLayer(),
          ),
        ),
      );
      expect(error).toBeInstanceOf(DatabaseError);
      expect((error as DatabaseError).message).toBe(
        "Failed to fetch claw for bootstrap",
      );
    }),
  );

  it.effect(
    "reportClawStatusHandler returns DatabaseError when update fails",
    () =>
      Effect.gen(function* () {
        const error = yield* reportClawStatusHandler("some-id", {
          status: "active",
        }).pipe(
          Effect.flip,
          Effect.provide(
            Layer.succeed(DrizzleORM, {
              update: () => failingUpdate(),
            } as never),
          ),
        );
        expect(error).toBeInstanceOf(DatabaseError);
        expect((error as DatabaseError).message).toBe(
          "Failed to update claw status",
        );
      }),
  );
});

describe("Claw handler errors", () => {
  const failingUpdate = () => {
    const fail = Effect.fail({ _tag: "SqlError", cause: new Error("db down") });
    const chain = (): unknown =>
      new Proxy(fail, {
        get: (target, prop) => {
          if (prop === "pipe")
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            return (...fns: Array<(e: any) => any>) =>
              fns.reduce((acc, fn) => fn(acc), fail);
          if (
            typeof prop === "string" &&
            ["set", "where", "returning"].includes(prop)
          )
            return () => chain();
          return Reflect.get(target, prop);
        },
      });
    return chain();
  };

  const succeedingUpdate = () => {
    const success = Effect.succeed([{}]);
    const chain = (): unknown =>
      new Proxy(success, {
        get: (target, prop) => {
          if (prop === "pipe")
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            return (...fns: Array<(e: any) => any>) =>
              fns.reduce((acc, fn) => fn(acc), success);
          if (
            typeof prop === "string" &&
            ["set", "where", "returning"].includes(prop)
          )
            return () => chain();
          return Reflect.get(target, prop);
        },
      });
    return chain();
  };

  /**
   * Mock user and claw fixtures for handler-level tests that don't need a
   * real database. Providing a mocked Database avoids the rollback-timeout
   * issue that occurs when mixing a real SQL transaction with a failing
   * DrizzleORM mock.
   */
  const mockUser = {
    id: "mock-user-id",
    email: "mock@example.com",
    name: "Mock User",
    accountType: "user" as const,
    deletedAt: null,
  };

  const mockClaw: PublicClaw = {
    id: "mock-claw-id",
    slug: "mock-claw",
    displayName: "Mock Claw",
    description: null,
    organizationId: "mock-org-id",
    createdByUserId: mockUser.id,
    status: "pending",
    instanceType: "basic",
    lastDeployedAt: null,
    lastError: null,
    botUserId: null,
    homeProjectId: null,
    homeEnvironmentId: null,
    secretsEncrypted: null,
    secretsKeyId: null,
    bucketName: null,
    macId: null,
    macPort: null,
    tunnelHostname: null,
    macUsername: null,
    weeklySpendingGuardrailCenticents: null,
    weeklyWindowStart: null,
    weeklyUsageCenticents: 0n,
    burstWindowStart: null,
    burstUsageCenticents: 0n,
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  const MockAnalyticsLayer = Layer.succeed(Analytics, {
    googleAnalytics: null as never,
    postHog: null as never,
    trackEvent: () => Effect.void,
    trackPageView: () => Effect.void,
    identify: () => Effect.void,
    initialize: () => Effect.void,
  });

  const MockDatabaseLayer = Layer.succeed(Database, {
    users: {} as never,
    organizations: {
      create: () => Effect.die("not implemented"),
      findById: () => Effect.die("not implemented"),
      findAll: () => Effect.die("not implemented"),
      update: () => Effect.die("not implemented"),
      delete: () => Effect.die("not implemented"),
      memberships: {} as never,
      invitations: {} as never,
      projects: {} as never,
      claws: {
        create: () => Effect.succeed(mockClaw),
        findById: () => Effect.succeed(mockClaw),
        findAll: () => Effect.succeed([mockClaw]),
        update: () => Effect.succeed(mockClaw),
        delete: () => Effect.void,
        memberships: {} as never,
        authorize: () => Effect.succeed("ADMIN" as never),
        getRole: () => Effect.die("not implemented"),
        getPoolUsage: () => Effect.die("not implemented"),
        getClawUsage: () => Effect.die("not implemented"),
        recordUsage: () => Effect.die("not implemented"),
      },
    } as never,
  } as never);

  /**
   * Common layer for handler-level tests. Provides all dependencies that
   * createClawHandler / deleteClawHandler require.
   */
  const handlerLayer = Layer.mergeAll(
    Layer.succeed(AuthenticatedUser, mockUser),
    MockAnalyticsLayer,
    MockDatabaseLayer,
    MockClawDeployment.layer(),
    MockSettingsLayer(),
  );

  it.effect(
    "createClawHandler returns DatabaseError when credential persist fails",
    () =>
      Effect.gen(function* () {
        const error = yield* createClawHandler("mock-org-id", {
          name: "Fail Claw",
          slug: "fail-claw",
        }).pipe(
          Effect.flip,
          Effect.provide(
            Layer.mergeAll(
              handlerLayer,
              Layer.succeed(DrizzleORM, {
                update: () => failingUpdate(),
              } as never),
            ),
          ),
        );
        expect(error).toBeInstanceOf(DatabaseError);
        expect((error as DatabaseError).message).toBe(
          "Failed to persist deployment credentials",
        );
      }),
  );

  it.effect(
    "createClawHandler returns ClawDeploymentError when provision fails",
    () =>
      Effect.gen(function* () {
        const error = yield* createClawHandler("mock-org-id", {
          name: "Fail Claw",
          slug: "fail-provision",
        }).pipe(
          Effect.flip,
          Effect.provide(
            Layer.mergeAll(
              Layer.succeed(AuthenticatedUser, mockUser),
              MockAnalyticsLayer,
              MockDatabaseLayer,
              MockClawDeployment.layer({
                provision: () =>
                  Effect.fail(
                    new ClawDeploymentError({
                      message: "R2 bucket creation failed",
                    }),
                  ),
              }),
              MockSettingsLayer(),
              Layer.succeed(DrizzleORM, {} as never),
            ),
          ),
        );
        expect(error).toBeInstanceOf(ClawDeploymentError);
        expect((error as ClawDeploymentError).message).toBe(
          "R2 bucket creation failed",
        );
      }),
  );

  it.effect(
    "createClawHandler returns ClawDeploymentError when warmUp fails",
    () =>
      Effect.gen(function* () {
        const error = yield* createClawHandler("mock-org-id", {
          name: "Fail WarmUp Claw",
          slug: "fail-warmup",
        }).pipe(
          Effect.flip,
          Effect.provide(
            Layer.mergeAll(
              Layer.succeed(AuthenticatedUser, mockUser),
              MockAnalyticsLayer,
              MockDatabaseLayer,
              MockClawDeployment.layer({
                warmUp: () =>
                  Effect.fail(
                    new ClawDeploymentError({
                      message: "Container dispatch failed",
                    }),
                  ),
              }),
              MockSettingsLayer(),
              Layer.succeed(DrizzleORM, {
                update: () => succeedingUpdate(),
              } as never),
            ),
          ),
        );
        expect(error).toBeInstanceOf(ClawDeploymentError);
        expect((error as ClawDeploymentError).message).toBe(
          "Container dispatch failed",
        );
      }),
  );

  it.effect(
    "createClawHandler calls provision with correct clawId and instanceType",
    () =>
      Effect.gen(function* () {
        let capturedConfig: { clawId: string; instanceType: string } | null =
          null;

        yield* createClawHandler("mock-org-id", {
          name: "Params Claw",
          slug: "params-claw",
        }).pipe(
          Effect.provide(
            Layer.mergeAll(
              Layer.succeed(AuthenticatedUser, mockUser),
              MockAnalyticsLayer,
              MockDatabaseLayer,
              MockClawDeployment.layer({
                provision: (config) =>
                  Effect.sync(() => {
                    capturedConfig = config;
                    return {
                      status: "active" as const,
                      startedAt: new Date(),
                      macId: "00000000-0000-0000-0000-000000000001",
                      macPort: 18789,
                      tunnelHostname: `claw-${config.clawId}.claws.mirascope.dev`,
                      macUsername: `claw-${config.clawId}`,
                    };
                  }),
              }),
              MockSettingsLayer(),
              Layer.succeed(DrizzleORM, {
                update: () => succeedingUpdate(),
              } as never),
            ),
          ),
        );

        expect(capturedConfig).not.toBeNull();
        expect(capturedConfig!.clawId).toBe(mockClaw.id);
        expect(capturedConfig!.instanceType).toBe(mockClaw.instanceType);
      }),
  );

  it.effect(
    "createClawHandler persists R2 credentials from provision result",
    () =>
      Effect.gen(function* () {
        let capturedSet: Record<string, unknown> | null = null;

        const CapturingDrizzle = Layer.succeed(DrizzleORM, {
          update: () => {
            const success = Effect.succeed([mockClaw]);
            const chain = (level = 0): unknown =>
              new Proxy(success, {
                get: (target, prop) => {
                  if (prop === "pipe")
                    // eslint-disable-next-line @typescript-eslint/no-explicit-any
                    return (...fns: Array<(e: any) => any>) =>
                      fns.reduce((acc, fn) => fn(acc), success);
                  if (prop === "set")
                    return (data: Record<string, unknown>) => {
                      capturedSet = data;
                      return chain(level + 1);
                    };
                  if (
                    typeof prop === "string" &&
                    ["where", "returning"].includes(prop)
                  )
                    return () => chain(level + 1);
                  return Reflect.get(target, prop);
                },
              });
            return chain();
          },
        } as never);

        yield* createClawHandler("mock-org-id", {
          name: "Persist Claw",
          slug: "persist-claw",
        }).pipe(
          Effect.provide(
            Layer.mergeAll(
              Layer.succeed(AuthenticatedUser, mockUser),
              MockAnalyticsLayer,
              MockDatabaseLayer,
              MockClawDeployment.layer(),
              MockSettingsLayer(),
              CapturingDrizzle,
            ),
          ),
        );

        expect(capturedSet).not.toBeNull();
        expect(capturedSet!.status).toBe("provisioning");
        expect(capturedSet!.macId).toBeDefined();
        expect(capturedSet!.tunnelHostname).toBeDefined();
        expect(capturedSet!.secretsKeyId).toBe(
          "CLAW_SECRETS_ENCRYPTION_KEY_V1",
        );

        // secretsEncrypted is now AES-256-GCM ciphertext, not raw JSON
        const ciphertext = capturedSet!.secretsEncrypted as string;
        expect(typeof ciphertext).toBe("string");
        expect(ciphertext.length).toBeGreaterThan(0);
        // Should NOT be parseable as JSON (it's encrypted)
        expect(() => JSON.parse(ciphertext)).toThrow();
      }),
  );

  it.effect(
    "deleteClawHandler calls deprovision before deleting from database",
    () =>
      Effect.gen(function* () {
        let deprovisionCalledWith: string | null = null;

        yield* deleteClawHandler("mock-org-id", "mock-claw-id").pipe(
          Effect.provide(
            Layer.mergeAll(
              Layer.succeed(AuthenticatedUser, mockUser),
              MockAnalyticsLayer,
              MockDatabaseLayer,
              MockClawDeployment.layer({
                deprovision: (clawId) =>
                  Effect.sync(() => {
                    deprovisionCalledWith = clawId;
                  }),
              }),
            ),
          ),
        );

        expect(deprovisionCalledWith).toBe("mock-claw-id");
      }),
  );

  it.effect(
    "deleteClawHandler returns ClawDeploymentError when deprovision fails",
    () =>
      Effect.gen(function* () {
        const error = yield* deleteClawHandler(
          "mock-org-id",
          "mock-claw-id",
        ).pipe(
          Effect.flip,
          Effect.provide(
            Layer.mergeAll(
              Layer.succeed(AuthenticatedUser, mockUser),
              MockAnalyticsLayer,
              MockDatabaseLayer,
              MockClawDeployment.layer({
                deprovision: () =>
                  Effect.fail(
                    new ClawDeploymentError({
                      message: "Failed to delete R2 bucket",
                    }),
                  ),
              }),
            ),
          ),
        );

        expect(error).toBeInstanceOf(ClawDeploymentError);
        expect((error as ClawDeploymentError).message).toBe(
          "Failed to delete R2 bucket",
        );
      }),
  );

  it.effect("restartClawHandler authorizes update and calls deployment", () =>
    Effect.gen(function* () {
      let authorizeArgs: Record<string, unknown> | null = null;
      let restartCalledWith: string | null = null;

      const RestartDatabaseLayer = Layer.succeed(Database, {
        users: {} as never,
        organizations: {
          claws: {
            authorize: (args: unknown) =>
              Effect.sync(() => {
                authorizeArgs = args as Record<string, unknown>;
                return "ADMIN" as never;
              }),
          },
        } as never,
      } as never);

      yield* restartClawHandler("mock-org-id", "mock-claw-id").pipe(
        Effect.provide(
          Layer.mergeAll(
            Layer.succeed(AuthenticatedUser, mockUser),
            RestartDatabaseLayer,
            MockClawDeployment.layer({
              restart: (clawId) =>
                Effect.sync(() => {
                  restartCalledWith = clawId;
                  return {
                    status: "active" as const,
                    startedAt: new Date(),
                    macId: "00000000-0000-0000-0000-000000000001",
                    macPort: 18789,
                    tunnelHostname: "claw-mock-claw-id.claws.mirascope.dev",
                    macUsername: "claw-mock-claw-id",
                  };
                }),
            }),
          ),
        ),
      );

      expect(authorizeArgs).toEqual({
        userId: mockUser.id,
        organizationId: "mock-org-id",
        clawId: "mock-claw-id",
        action: "update",
      });
      expect(restartCalledWith).toBe("mock-claw-id");
    }),
  );

  it.effect(
    "restartClawHandler returns PermissionDeniedError when authorize fails",
    () =>
      Effect.gen(function* () {
        const RestartDatabaseLayer = Layer.succeed(Database, {
          users: {} as never,
          organizations: {
            claws: {
              authorize: () =>
                Effect.fail(
                  new PermissionDeniedError({
                    message: "nope",
                    resource: "claw",
                  }),
                ),
            },
          } as never,
        } as never);

        const error = yield* restartClawHandler(
          "mock-org-id",
          "mock-claw-id",
        ).pipe(
          Effect.flip,
          Effect.provide(
            Layer.mergeAll(
              Layer.succeed(AuthenticatedUser, mockUser),
              RestartDatabaseLayer,
              MockClawDeployment.layer(),
            ),
          ),
        );

        expect(error).toBeInstanceOf(PermissionDeniedError);
      }),
  );

  it.effect(
    "restartClawHandler returns ClawDeploymentError when restart fails",
    () =>
      Effect.gen(function* () {
        const RestartDatabaseLayer = Layer.succeed(Database, {
          users: {} as never,
          organizations: {
            claws: {
              authorize: () => Effect.succeed("ADMIN" as never),
            },
          } as never,
        } as never);

        const error = yield* restartClawHandler(
          "mock-org-id",
          "mock-claw-id",
        ).pipe(
          Effect.flip,
          Effect.provide(
            Layer.mergeAll(
              Layer.succeed(AuthenticatedUser, mockUser),
              RestartDatabaseLayer,
              MockClawDeployment.layer({
                restart: () =>
                  Effect.fail(
                    new ClawDeploymentError({
                      message: "Failed to restart claw",
                    }),
                  ),
              }),
            ),
          ),
        );

        expect(error).toBeInstanceOf(ClawDeploymentError);
        expect((error as ClawDeploymentError).message).toBe(
          "Failed to restart claw",
        );
      }),
  );
});

describe("Internal handler integration", () => {
  it.rollback("resolveClawHandler resolves org/claw slugs to clawId", () =>
    Effect.gen(function* () {
      const { org, claw } = yield* createTestFixture;

      const result = yield* resolveClawHandler(org.slug, "handler-claw");
      expect(result.clawId).toBe(claw.id);
      expect(result.organizationId).toBe(org.id);
    }),
  );

  it.rollback("bootstrapClawHandler returns full config for a claw", () =>
    Effect.gen(function* () {
      const { org, claw } = yield* createTestFixture;

      const config = yield* bootstrapClawHandler(claw.id);
      expect(config.clawId).toBe(claw.id);
      expect(config.clawSlug).toBe("handler-claw");
      expect(config.organizationId).toBe(org.id);
      expect(config.organizationSlug).toBe(org.slug);
      expect(config.instanceType).toBeDefined();
      expect(config.r2).toBeDefined();
      expect(config.containerEnv).toBeDefined();
    }),
  );

  it.rollback(
    "bootstrapClawHandler includes decrypted secrets in containerEnv",
    () =>
      Effect.gen(function* () {
        const { claw } = yield* createTestFixture;

        // Encrypt secrets and store in DB
        const client = yield* DrizzleORM;
        const encrypted = yield* encryptSecrets({
          MIRASCOPE_API_KEY: "test-key",
          R2_ACCESS_KEY_ID: "r2-ak",
          R2_SECRET_ACCESS_KEY: "r2-sk",
        });
        yield* client
          .update(claws)
          .set({
            secretsEncrypted: encrypted.ciphertext,
            secretsKeyId: encrypted.keyId,
          })
          .where(eq(claws.id, claw.id));

        const config = yield* bootstrapClawHandler(claw.id);
        expect(config.containerEnv.MIRASCOPE_API_KEY).toBe("test-key");
      }),
  );

  it.rollback("reportClawStatusHandler updates claw status", () =>
    Effect.gen(function* () {
      const { org, user, claw } = yield* createTestFixture;

      yield* reportClawStatusHandler(claw.id, {
        status: "active",
        startedAt: "2025-01-01T00:00:00Z",
      });

      const db = yield* Database;
      const fetched = yield* db.organizations.claws.findById({
        organizationId: org.id,
        clawId: claw.id,
        userId: user.id,
      });
      expect(fetched.status).toBe("active");
      expect(fetched.lastDeployedAt).toEqual(new Date("2025-01-01T00:00:00Z"));
    }),
  );

  it.rollback("reportClawStatusHandler updates error status with message", () =>
    Effect.gen(function* () {
      const { org, user, claw } = yield* createTestFixture;

      yield* reportClawStatusHandler(claw.id, {
        status: "error",
        errorMessage: "container crashed",
      });

      const db = yield* Database;
      const fetched = yield* db.organizations.claws.findById({
        organizationId: org.id,
        clawId: claw.id,
        userId: user.id,
      });
      expect(fetched.status).toBe("error");
      expect(fetched.lastError).toBe("container crashed");
    }),
  );

  it.rollback(
    "reportClawStatusHandler clears lastError when status is not error",
    () =>
      Effect.gen(function* () {
        const { org, user, claw } = yield* createTestFixture;

        // First set error
        yield* reportClawStatusHandler(claw.id, {
          status: "error",
          errorMessage: "container crashed",
        });

        // Then clear it
        yield* reportClawStatusHandler(claw.id, {
          status: "active",
        });

        const db = yield* Database;
        const fetched = yield* db.organizations.claws.findById({
          organizationId: org.id,
          clawId: claw.id,
          userId: user.id,
        });
        expect(fetched.status).toBe("active");
        expect(fetched.lastError).toBeNull();
      }),
  );
});

describe("validateSessionHandler", () => {
  it.effect("returns UnauthorizedError for invalid session", () =>
    Effect.gen(function* () {
      const error = yield* validateSessionHandler({
        sessionId: "00000000-0000-0000-0000-000000000000",
        organizationSlug: "any-org",
        clawSlug: "any-claw",
      }).pipe(Effect.flip);
      expect(error).toBeInstanceOf(UnauthorizedError);
      expect(error.message).toBe("Invalid session");
    }),
  );

  it.rollback("returns NotFoundError for unknown org/claw slugs", () =>
    Effect.gen(function* () {
      const db = yield* Database;
      const { user } = yield* createTestFixture;

      const session = yield* db.sessions.create({
        userId: user.id,
        data: { userId: user.id, expiresAt: new Date(Date.now() + 60_000) },
      });

      const error = yield* validateSessionHandler({
        sessionId: session.id,
        organizationSlug: "nonexistent-org",
        clawSlug: "nonexistent-claw",
      }).pipe(Effect.flip);
      expect(error).toBeInstanceOf(NotFoundError);
    }),
  );

  it.rollback("returns UnauthorizedError when user has no access to claw", () =>
    Effect.gen(function* () {
      const db = yield* Database;
      const { org } = yield* createTestFixture;

      // Create a different user with no org membership
      const outsider = yield* db.users.create({
        data: {
          email: `outsider-${Date.now()}@example.com`,
          name: "Outsider",
        },
      });

      const session = yield* db.sessions.create({
        userId: outsider.id,
        data: {
          userId: outsider.id,
          expiresAt: new Date(Date.now() + 60_000),
        },
      });

      const error = yield* validateSessionHandler({
        sessionId: session.id,
        organizationSlug: org.slug,
        clawSlug: "handler-claw",
      }).pipe(Effect.flip);
      expect(error).toBeInstanceOf(UnauthorizedError);
      expect(error.message).toBe("No access to this claw");
    }),
  );

  it.rollback("returns UnauthorizedError for deleted user", () =>
    Effect.gen(function* () {
      const db = yield* Database;
      const { user } = yield* createTestFixture;

      const session = yield* db.sessions.create({
        userId: user.id,
        data: { userId: user.id, expiresAt: new Date(Date.now() + 60_000) },
      });

      // Soft-delete the user
      yield* db.users.delete({ userId: user.id });

      const error = yield* validateSessionHandler({
        sessionId: session.id,
        organizationSlug: "any-org",
        clawSlug: "any-claw",
      }).pipe(Effect.flip);
      expect(error).toBeInstanceOf(UnauthorizedError);
      expect(error.message).toBe("Invalid session");
    }),
  );

  it.rollback("returns UnauthorizedError for expired session", () =>
    Effect.gen(function* () {
      const db = yield* Database;
      const { user } = yield* createTestFixture;

      const session = yield* db.sessions.create({
        userId: user.id,
        data: {
          userId: user.id,
          expiresAt: new Date(Date.now() - 60_000), // already expired
        },
      });

      const error = yield* validateSessionHandler({
        sessionId: session.id,
        organizationSlug: "any-org",
        clawSlug: "any-claw",
      }).pipe(Effect.flip);
      expect(error).toBeInstanceOf(UnauthorizedError);
      expect(error.message).toBe("Invalid session");
    }),
  );

  it.rollback("returns role for org owner with implicit access", () =>
    Effect.gen(function* () {
      const db = yield* Database;
      const { user, org, claw } = yield* createTestFixture;

      const session = yield* db.sessions.create({
        userId: user.id,
        data: { userId: user.id, expiresAt: new Date(Date.now() + 60_000) },
      });

      const result = yield* validateSessionHandler({
        sessionId: session.id,
        organizationSlug: org.slug,
        clawSlug: "handler-claw",
      });

      expect(result.userId).toBe(user.id);
      expect(result.clawId).toBe(claw.id);
      expect(result.organizationId).toBe(org.id);
      expect(result.role).toBeDefined();
    }),
  );
});
