import { describe, it, expect } from "vitest";
import * as dotenv from "dotenv";
import { Effect, Layer } from "effect";
import { DatabaseService, type Database } from "@/db";
import { AuthenticatedUser } from "@/auth/context";
import { DatabaseError } from "@/db/errors";
import type { PublicUser } from "@/db/schema";
import {
  listOrganizationsHandler,
  createOrganizationHandler,
  deleteOrganizationHandler,
} from "@/api/organizations";
import { withApiClient } from "@/tests/api";

dotenv.config({ path: ".env.local", override: true });

describe("Organizations API", () => {
  it(
    "GET /organizations - returns empty list initially",
    withApiClient()(async ([client]) => {
      const result = await Effect.runPromise(client.organizations.list());
      expect(result.organizations).toEqual([]);
    }),
  );

  it(
    "POST /organizations - creates a new organization",
    withApiClient()(async ([client]) => {
      const result = await Effect.runPromise(
        client.organizations.create({ payload: { name: "Test Org" } }),
      );

      expect(result).toMatchObject({
        id: expect.any(String) as unknown,
        name: "Test Org",
        role: "OWNER",
      });
    }),
  );

  it(
    "POST /organizations - returns 409 for duplicate name",
    withApiClient()(async ([client]) => {
      // Create first org
      await Effect.runPromise(
        client.organizations.create({ payload: { name: "Duplicate Org" } }),
      );

      // Try to create another with the same name
      const result = await Effect.runPromise(
        client.organizations
          .create({ payload: { name: "Duplicate Org" } })
          .pipe(Effect.flip),
      );

      expect(result).toMatchObject({
        _tag: "AlreadyExistsError",
        message: "An organization with this name already exists",
      });
    }),
  );

  it(
    "DELETE /organizations/:id - deletes an organization",
    withApiClient()(async ([client]) => {
      // Create an org first
      const created = await Effect.runPromise(
        client.organizations.create({ payload: { name: "To Delete" } }),
      );

      // Delete it
      await Effect.runPromise(
        client.organizations.delete({ path: { id: created.id } }),
      );

      // Verify it's gone
      const result = await Effect.runPromise(client.organizations.list());
      expect(result.organizations).toEqual([]);
    }),
  );

  it(
    "DELETE /organizations/:id - returns 404 for non-existent org",
    withApiClient()(async ([client]) => {
      const result = await Effect.runPromise(
        client.organizations
          .delete({ path: { id: "00000000-0000-0000-0000-000000000000" } })
          .pipe(Effect.flip),
      );

      expect(result).toMatchObject({
        _tag: "NotFoundError",
      });
    }),
  );

  it(
    "GET /organizations - returns created organizations with roles",
    withApiClient()(async ([client]) => {
      // Create multiple orgs
      await Effect.runPromise(
        client.organizations.create({ payload: { name: "Org 1" } }),
      );
      await Effect.runPromise(
        client.organizations.create({ payload: { name: "Org 2" } }),
      );

      const result = await Effect.runPromise(client.organizations.list());

      expect(result.organizations).toHaveLength(2);
      expect(result.organizations).toEqual(
        expect.arrayContaining([
          expect.objectContaining({ name: "Org 1", role: "OWNER" }),
          expect.objectContaining({ name: "Org 2", role: "OWNER" }),
        ]),
      );
    }),
  );

  it(
    "DELETE /organizations/:id - returns 403 when user is not owner",
    withApiClient(2)(async ([client1, client2]) => {
      // User 1 creates an org (becomes owner)
      const created = await Effect.runPromise(
        client1.organizations.create({ payload: { name: "User1 Org" } }),
      );

      // User 2 tries to delete it (should fail with permission denied)
      const result = await Effect.runPromise(
        client2.organizations
          .delete({ path: { id: created.id } })
          .pipe(Effect.flip),
      );

      expect(result).toMatchObject({
        _tag: "PermissionDeniedError",
        message: "You do not have permission to delete this organization",
      });
    }),
  );
});

// ============================================================================
// Unit tests for error handling paths
// ============================================================================

describe("Organization Handlers - Error Handling", () => {
  const mockUser: PublicUser = {
    id: "test-user-id",
    email: "test@example.com",
    name: "Test User",
  };

  it("listOrganizationsHandler returns DatabaseError for database failures", async () => {
    // Mock database that returns a DatabaseError
    const mockDb: Database = {
      users: {} as Database["users"],
      sessions: {} as Database["sessions"],
      organizations: {
        create: () =>
          Effect.succeed({ id: "test", name: "test", role: "OWNER" }),
        findAll: () =>
          Effect.fail(
            new DatabaseError({
              message: "Query failed",
              cause: new Error("connection reset"),
            }),
          ),
        delete: () => Effect.succeed(undefined),
        findById: () =>
          Effect.fail(new DatabaseError({ message: "Not found" })),
        update: () => Effect.fail(new DatabaseError({ message: "Not found" })),
      } as unknown as Database["organizations"],
    };

    const testLayer = Layer.mergeAll(
      Layer.succeed(AuthenticatedUser, mockUser),
      Layer.succeed(DatabaseService, mockDb),
    );

    const result = await Effect.runPromise(
      listOrganizationsHandler.pipe(Effect.flip, Effect.provide(testLayer)),
    );

    expect(result).toBeInstanceOf(DatabaseError);
    expect(result.message).toBe("Query failed");
  });

  it("createOrganizationHandler returns DatabaseError for unexpected errors", async () => {
    // Mock database that returns a DatabaseError (not AlreadyExistsError)
    const mockDb: Database = {
      users: {} as Database["users"],
      sessions: {} as Database["sessions"],
      organizations: {
        create: () =>
          Effect.fail(
            new DatabaseError({
              message: "Connection failed",
              cause: new Error("timeout"),
            }),
          ),
        findAll: () => Effect.succeed([]),
        delete: () => Effect.succeed(undefined),
        findById: () =>
          Effect.fail(new DatabaseError({ message: "Not found" })),
        update: () => Effect.fail(new DatabaseError({ message: "Not found" })),
      } as unknown as Database["organizations"],
    };

    const testLayer = Layer.mergeAll(
      Layer.succeed(AuthenticatedUser, mockUser),
      Layer.succeed(DatabaseService, mockDb),
    );

    const result = await Effect.runPromise(
      createOrganizationHandler({ name: "Test" }).pipe(
        Effect.flip,
        Effect.provide(testLayer),
      ),
    );

    expect(result).toBeInstanceOf(DatabaseError);
    expect(result.message).toBe("Connection failed");
  });

  it("deleteOrganizationHandler returns DatabaseError for unexpected errors", async () => {
    // Mock database that returns a DatabaseError (not NotFoundError or PermissionDeniedError)
    const mockDb: Database = {
      users: {} as Database["users"],
      sessions: {} as Database["sessions"],
      organizations: {
        create: () =>
          Effect.succeed({ id: "test", name: "test", role: "OWNER" }),
        findAll: () => Effect.succeed([]),
        delete: () =>
          Effect.fail(
            new DatabaseError({
              message: "Connection lost",
              cause: new Error("network error"),
            }),
          ),
        findById: () =>
          Effect.fail(new DatabaseError({ message: "Not found" })),
        update: () => Effect.fail(new DatabaseError({ message: "Not found" })),
      } as unknown as Database["organizations"],
    };

    const testLayer = Layer.mergeAll(
      Layer.succeed(AuthenticatedUser, mockUser),
      Layer.succeed(DatabaseService, mockDb),
    );

    const result = await Effect.runPromise(
      deleteOrganizationHandler({ id: "some-id" }).pipe(
        Effect.flip,
        Effect.provide(testLayer),
      ),
    );

    expect(result).toBeInstanceOf(DatabaseError);
    expect(result.message).toBe("Connection lost");
  });
});
