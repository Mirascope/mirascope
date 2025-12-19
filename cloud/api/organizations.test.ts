import { describe, it, expect } from "@effect/vitest";
import { Effect } from "effect";
import { TestApiClient, TestClient } from "@/tests/api";
import { TestDatabase, TestOrganizationFixture } from "@/tests/db";
import type { PublicOrganizationWithMembership } from "@/db/schema";

describe("Organizations API", () => {
  // Simple test using TestClient.Authenticated (creates user automatically)
  it.effect("POST /organizations - create organization", () =>
    Effect.gen(function* () {
      const client = yield* TestApiClient;

      const org = yield* client.organizations.create({
        payload: { name: "New Test Organization" },
      });
      expect(org.name).toBe("New Test Organization");
      expect(org.role).toBe("OWNER");
      expect(org.id).toBeDefined();
    }).pipe(Effect.provide(TestClient.Authenticated)),
  );

  // Tests with fixtures use TestClient.authenticate(user) to get a client
  it.effect("GET /organizations - list organizations", () =>
    Effect.gen(function* () {
      const { owner, org } = yield* TestOrganizationFixture;
      const client = yield* TestClient.authenticate(owner);

      const orgs = yield* client.organizations.list();
      expect(orgs.length).toBe(1);
      expect(orgs[0].id).toBe(org.id);
      expect(orgs[0].name).toBe(org.name);
    }).pipe(Effect.provide(TestDatabase)),
  );

  it.effect("GET /organizations/:id - get organization", () =>
    Effect.gen(function* () {
      const { owner, org } = yield* TestOrganizationFixture;
      const client = yield* TestClient.authenticate(owner);

      const fetched = yield* client.organizations.get({
        path: { id: org.id },
      });

      expect(fetched.id).toBe(org.id);
      expect(fetched.name).toBe(org.name);
      expect(fetched.role).toBe("OWNER");
    }).pipe(Effect.provide(TestDatabase)),
  );

  it.effect("PUT /organizations/:id - update organization", () =>
    Effect.gen(function* () {
      const { owner, org } = yield* TestOrganizationFixture;
      const client = yield* TestClient.authenticate(owner);

      const updated = yield* client.organizations.update({
        path: { id: org.id },
        payload: { name: "Updated Org Name" },
      });

      expect(updated.id).toBe(org.id);
      expect(updated.name).toBe("Updated Org Name");
      expect(updated.role).toBe("OWNER");
    }).pipe(Effect.provide(TestDatabase)),
  );

  it.effect("DELETE /organizations/:id - delete organization", () =>
    Effect.gen(function* () {
      const { owner, org } = yield* TestOrganizationFixture;
      const client = yield* TestClient.authenticate(owner);

      yield* client.organizations.delete({ path: { id: org.id } });

      // Verify it's gone by listing and checking it's not there
      const orgs = yield* client.organizations.list();
      const found = orgs.find(
        (o: PublicOrganizationWithMembership) => o.id === org.id,
      );
      expect(found).toBeUndefined();
    }).pipe(Effect.provide(TestDatabase)),
  );
});
