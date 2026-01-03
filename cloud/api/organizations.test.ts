import { Effect, Schema } from "effect";
import { ParseError } from "effect/ParseResult";
import { describe, it, expect, TestApiContext } from "@/tests/api";
import {
  CreateOrganizationRequestSchema,
  CreatePaymentIntentRequestSchema,
} from "@/api/organizations.schemas";
import type { PublicOrganizationWithMembership } from "@/db/schema";

describe("CreateOrganizationRequestSchema validation", () => {
  it("rejects empty name", () => {
    expect(() =>
      Schema.decodeUnknownSync(CreateOrganizationRequestSchema)({
        name: "",
        slug: "test-org",
      }),
    ).toThrow("Organization name is required");
  });

  it("rejects name > 100 chars", () => {
    const longName = "a".repeat(101);
    expect(() =>
      Schema.decodeUnknownSync(CreateOrganizationRequestSchema)({
        name: longName,
        slug: "test-org",
      }),
    ).toThrow("Organization name must be at most 100 characters");
  });

  it("accepts valid name", () => {
    const result = Schema.decodeUnknownSync(CreateOrganizationRequestSchema)({
      name: "Valid Organization Name",
      slug: "valid-org",
    });
    expect(result.name).toBe("Valid Organization Name");
  });
});

describe("CreatePaymentIntentRequestSchema validation", () => {
  it("rejects negative amount", () => {
    expect(() =>
      Schema.decodeUnknownSync(CreatePaymentIntentRequestSchema)({
        amount: -10,
      }),
    ).toThrow("Amount must be positive");
  });

  it("rejects zero amount", () => {
    expect(() =>
      Schema.decodeUnknownSync(CreatePaymentIntentRequestSchema)({
        amount: 0,
      }),
    ).toThrow("Amount must be positive");
  });

  it("accepts valid request", () => {
    const result = Schema.decodeUnknownSync(CreatePaymentIntentRequestSchema)({
      amount: 50,
    });
    expect(result.amount).toBe(50);
  });
});

describe.sequential("Organizations API", (it) => {
  let org: PublicOrganizationWithMembership;

  it.effect("POST /organizations - create organization", () =>
    Effect.gen(function* () {
      const { client } = yield* TestApiContext;
      org = yield* client.organizations.create({
        payload: {
          name: "New Test Organization",
          slug: "new-test-organization",
        },
      });
      expect(org.name).toBe("New Test Organization");
      expect(org.role).toBe("OWNER");
      expect(org.id).toBeDefined();
    }),
  );

  it.effect("POST /organizations - rejects invalid slug pattern", () =>
    Effect.gen(function* () {
      const { client } = yield* TestApiContext;
      const result = yield* client.organizations
        .create({
          payload: { name: "Test Org", slug: "Invalid Slug!" },
        })
        .pipe(Effect.flip);

      expect(result).toBeInstanceOf(ParseError);
      expect(result.message).toContain(
        "Organization slug must start and end with a letter or number, and only contain lowercase letters, numbers, hyphens, and underscores",
      );
    }),
  );

  it.effect("POST /organizations - rejects empty name", () =>
    Effect.gen(function* () {
      const { client } = yield* TestApiContext;
      const result = yield* client.organizations
        .create({
          payload: { name: "", slug: "test-org" },
        })
        .pipe(Effect.flip);

      expect(result._tag).toBe("ParseError");
    }),
  );

  it.effect("POST /organizations - rejects name > 100 chars", () =>
    Effect.gen(function* () {
      const { client } = yield* TestApiContext;
      const longName = "a".repeat(101);
      const result = yield* client.organizations
        .create({
          payload: { name: longName, slug: "test-org" },
        })
        .pipe(Effect.flip);

      expect(result._tag).toBe("ParseError");
    }),
  );

  it.effect("GET /organizations - list organizations", () =>
    Effect.gen(function* () {
      const { client } = yield* TestApiContext;
      const orgs = yield* client.organizations.list();
      // Should have at least the org we created (plus the fixture org)
      expect(orgs.length).toBeGreaterThanOrEqual(1);
      const found = orgs.find((o) => o.id === org.id);
      expect(found).toBeDefined();
      expect(found?.name).toBe("New Test Organization");
    }),
  );

  it.effect("GET /organizations/:id - get organization", () =>
    Effect.gen(function* () {
      const { client } = yield* TestApiContext;
      const fetched = yield* client.organizations.get({
        path: { id: org.id },
      });

      expect(fetched.id).toBe(org.id);
      expect(fetched.name).toBe("New Test Organization");
      expect(fetched.role).toBe("OWNER");
    }),
  );

  it.effect("PUT /organizations/:id - update organization", () =>
    Effect.gen(function* () {
      const { client } = yield* TestApiContext;
      const updated = yield* client.organizations.update({
        path: { id: org.id },
        payload: { name: "Updated Org Name" },
      });

      expect(updated.id).toBe(org.id);
      expect(updated.name).toBe("Updated Org Name");
      expect(updated.role).toBe("OWNER");
    }),
  );

  it.effect(
    "GET /organizations/:id/router-balance - get organization router balance",
    () =>
      Effect.gen(function* () {
        const { client } = yield* TestApiContext;
        const balance = yield* client.organizations.routerBalance({
          path: { id: org.id },
        });

        // MockStripe includes various grant types totaling $18
        // (see tests/db.ts MockStripe for details)
        // Balance is now in centi-cents: $18 = 180000 centi-cents
        expect(balance.balance).toBe(180000n);
        expect(typeof balance.balance).toBe("bigint");
      }),
  );

  it.effect(
    "POST /organizations/:id/credits/payment-intent - create payment intent",
    () =>
      Effect.gen(function* () {
        const { client } = yield* TestApiContext;
        const result = yield* client.organizations.createPaymentIntent({
          path: { id: org.id },
          payload: {
            amount: 50,
          },
        });

        expect(result.clientSecret).toBeDefined();
        expect(result.clientSecret).toMatch(/^pi_test_/);
        expect(result.amount).toBe(50);
      }),
  );

  it.effect("DELETE /organizations/:id - delete organization", () =>
    Effect.gen(function* () {
      const { client } = yield* TestApiContext;
      yield* client.organizations.delete({ path: { id: org.id } });

      // Verify it's gone by listing and checking it's not there
      const orgs = yield* client.organizations.list();
      const found = orgs.find((o) => o.id === org.id);
      expect(found).toBeUndefined();
    }),
  );
});
