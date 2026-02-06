import { Effect, Schema } from "effect";
import { ParseError } from "effect/ParseResult";

import type { PublicClaw } from "@/db/schema";

import { CreateClawRequestSchema } from "@/api/claws.handlers";
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
