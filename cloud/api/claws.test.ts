import { eq } from "drizzle-orm";
import { Effect, Layer, Schema } from "effect";
import { ParseError } from "effect/ParseResult";

import type { PublicClaw } from "@/db/schema";

import {
  resolveClawHandler,
  bootstrapClawHandler,
  reportClawStatusHandler,
  decryptSecrets,
} from "@/api/claws-internal.handlers";
import { CreateClawRequestSchema } from "@/api/claws.handlers";
import { DrizzleORM } from "@/db/client";
import { Database } from "@/db/database";
import { claws } from "@/db/schema";
import { DatabaseError, NotFoundError } from "@/errors";
import { describe, it, expect, TestApiContext } from "@/tests/api";

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

describe("decryptSecrets", () => {
  it("returns empty object for null", () => {
    expect(decryptSecrets(null)).toEqual({});
  });

  it("parses valid JSON", () => {
    const secrets = JSON.stringify({ KEY: "value", OTHER: "data" });
    expect(decryptSecrets(secrets)).toEqual({ KEY: "value", OTHER: "data" });
  });

  it("returns empty object for invalid JSON", () => {
    expect(decryptSecrets("not-json")).toEqual({});
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
  let claw: PublicClaw;

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
          Layer.succeed(DrizzleORM, {
            select: () => failingSelect(),
          } as never),
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

        // Store secrets as plain JSON in the DB (stub encryption)
        const client = yield* DrizzleORM;
        const secrets = JSON.stringify({
          MIRASCOPE_API_KEY: "test-key",
          R2_ACCESS_KEY_ID: "r2-ak",
          R2_SECRET_ACCESS_KEY: "r2-sk",
        });
        yield* client
          .update(claws)
          .set({ secretsEncrypted: secrets, bucketName: "claw-bucket" })
          .where(eq(claws.id, claw.id));

        const config = yield* bootstrapClawHandler(claw.id);
        expect(config.containerEnv.MIRASCOPE_API_KEY).toBe("test-key");
        expect(config.r2.accessKeyId).toBe("r2-ak");
        expect(config.r2.secretAccessKey).toBe("r2-sk");
        expect(config.r2.bucketName).toBe("claw-bucket");
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
