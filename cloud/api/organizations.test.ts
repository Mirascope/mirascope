import { describe, it, expect } from "vitest";
import { Effect } from "effect";
import { withTestClientDb } from "@/tests/api";

describe("Organizations API", () => {
  it(
    "GET /organizations - list organizations",
    withTestClientDb(async (client) => {
      const orgs = await Effect.runPromise(client.organizations.list());
      expect(Array.isArray(orgs)).toBe(true);
    }),
  );

  it(
    "POST /organizations - create organization",
    withTestClientDb(async (client) => {
      const org = await Effect.runPromise(
        client.organizations.create({ payload: { name: "Test Organization" } }),
      );
      expect(org.name).toBe("Test Organization");
      expect(org.role).toBe("OWNER");
      expect(org.id).toBeDefined();
    }),
  );

  it(
    "GET /organizations/:id - get organization",
    withTestClientDb(async (client) => {
      const created = await Effect.runPromise(
        client.organizations.create({ payload: { name: "Get Test Org" } }),
      );

      const org = await Effect.runPromise(
        client.organizations.get({ path: { id: created.id } }),
      );

      expect(org.id).toBe(created.id);
      expect(org.name).toBe("Get Test Org");
      expect(org.role).toBe("OWNER");
    }),
  );

  it(
    "PUT /organizations/:id - update organization",
    withTestClientDb(async (client) => {
      const created = await Effect.runPromise(
        client.organizations.create({ payload: { name: "Update Test Org" } }),
      );

      const updated = await Effect.runPromise(
        client.organizations.update({
          path: { id: created.id },
          payload: { name: "Updated Org Name" },
        }),
      );

      expect(updated.id).toBe(created.id);
      expect(updated.name).toBe("Updated Org Name");
      expect(updated.role).toBe("OWNER");
    }),
  );

  it(
    "DELETE /organizations/:id - delete organization",
    withTestClientDb(async (client) => {
      const created = await Effect.runPromise(
        client.organizations.create({ payload: { name: "Delete Test Org" } }),
      );

      await Effect.runPromise(
        client.organizations.delete({ path: { id: created.id } }),
      );

      // Verify it's gone by listing and checking it's not there
      const orgs = await Effect.runPromise(client.organizations.list());
      const found = orgs.find((o) => o.id === created.id);
      expect(found).toBeUndefined();
    }),
  );
});
