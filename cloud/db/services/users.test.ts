import { describe, it, expect } from "vitest";
import { withTestDatabase } from "@/tests/db";
import { Effect } from "effect";

describe("UserService", () => {
  it(
    "should support basic CRUD",
    withTestDatabase((db) =>
      Effect.gen(function* () {
        // --- Create ---
        const created = yield* db.users.create({
          email: "test@example.com",
          name: "Test User",
        });
        expect(created).toBeDefined();
        expect(created.id).toBeDefined();
        expect(created.email).toBe("test@example.com");
        expect(created.name).toBe("Test User");
        // Public fields should not include internal fields
        expect(created).not.toHaveProperty("createdAt");
        expect(created).not.toHaveProperty("updatedAt");

        const userId = created.id;

        // --- Get (findById) ---
        const found = yield* db.users.findById(userId);
        expect(found).toBeDefined();
        expect(found.id).toBe(userId);
        expect(found.email).toBe("test@example.com");
        expect(found.name).toBe("Test User");

        // --- FindAll should include our user ---
        const all = yield* db.users.findAll();
        expect(Array.isArray(all)).toBe(true);
        expect(all.find((u) => u.id === userId)).toBeDefined();

        // --- Update (name and email) ---
        const updated = yield* db.users.update(userId, {
          name: "Updated User",
          email: "updated@example.com",
        });
        expect(updated).toBeDefined();
        expect(updated.id).toBe(userId);
        expect(updated.name).toBe("Updated User");
        expect(updated.email).toBe("updated@example.com");

        // --- Get again after update ---
        const afterUpdate = yield* db.users.findById(userId);
        expect(afterUpdate).toBeDefined();
        expect(afterUpdate.name).toBe("Updated User");
        expect(afterUpdate.email).toBe("updated@example.com");

        // --- Delete ---
        yield* db.users.delete(userId);

        // --- Should not be able to get after delete ---
        const afterDeleteResult = yield* Effect.either(
          db.users.findById(userId),
        );
        expect(afterDeleteResult._tag).toBe("Left");
        if (afterDeleteResult._tag === "Left") {
          expect(afterDeleteResult.left._tag).toBe("NotFoundError");
        }

        // --- FindAll should not include our deleted user ---
        const afterDeleteAll = yield* db.users.findAll();
        expect(afterDeleteAll.find((u) => u.id === userId)).toBeUndefined();
      }),
    ),
  );
});
