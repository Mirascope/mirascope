import { Effect } from "effect";
import { describe, expect, TestApiContext } from "@/tests/api";
import type { PublicOrganizationWithMembership } from "@/db/schema";

describe.sequential("Organizations API", (it) => {
  let org: PublicOrganizationWithMembership;

  it.effect("POST /organizations - create organization", () =>
    Effect.gen(function* () {
      const { client } = yield* TestApiContext;
      org = yield* client.organizations.create({
        payload: { name: "New Test Organization" },
      });
      expect(org.name).toBe("New Test Organization");
      expect(org.role).toBe("OWNER");
      expect(org.id).toBeDefined();
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
