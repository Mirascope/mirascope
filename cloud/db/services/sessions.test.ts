import { describe, it, expect } from "vitest";
import { withTestDatabase } from "@/tests/db";
import { Effect } from "effect";

describe("SessionService", () => {
  it(
    "should support basic CRUD",
    withTestDatabase((db) =>
      Effect.gen(function* () {
        // First create a user (sessions require a valid user ID)
        const user = yield* db.users.create({
          email: "test@example.com",
          name: "Test User",
        });

        const expiresAt = new Date(Date.now() + 1000 * 60 * 60 * 24);

        // --- Create ---
        const created = yield* db.sessions.create({
          id: "123",
          userId: user.id,
          expiresAt,
        });
        expect(created).toBeDefined();
        expect(created.id).toBe("123");
        expect(created.expiresAt).toBeInstanceOf(Date);

        // --- Get (findById) ---
        const found = yield* db.sessions.findById("123");
        expect(found).toBeDefined();
        expect(found?.id).toBe("123");
        expect(found?.expiresAt.getTime()).toBe(expiresAt.getTime());

        // --- FindAll should include our session ---
        const all = yield* db.sessions.findAll();
        expect(Array.isArray(all)).toBe(true);
        expect(all.find((s) => s.id === "123")).toBeDefined();

        // --- Update (expiresAt) ---
        const newExpiresAt = new Date(Date.now() + 1000 * 60 * 60 * 48); // +2 days
        const updated = yield* db.sessions.update("123", {
          expiresAt: newExpiresAt,
        });
        expect(updated).toBeDefined();
        expect(updated?.id).toBe("123");
        expect(updated?.expiresAt.getTime()).toBe(newExpiresAt.getTime());

        // --- Get again after update ---
        const afterUpdate = yield* db.sessions.findById("123");
        expect(afterUpdate).toBeDefined();
        expect(afterUpdate?.expiresAt.getTime()).toBe(newExpiresAt.getTime());

        // --- Delete ---
        yield* db.sessions.delete("123");

        // --- Should not be able to get after delete ---
        const afterDeleteResult = yield* Effect.either(
          db.sessions.findById("123"),
        );
        expect(afterDeleteResult._tag).toBe("Left");
        if (afterDeleteResult._tag === "Left") {
          expect(afterDeleteResult.left._tag).toBe("NotFoundError");
        }

        // --- FindAll should not include our deleted session ---
        const afterDeleteAll = yield* db.sessions.findAll();
        expect(afterDeleteAll.find((s) => s.id === "123")).toBeUndefined();
      }),
    ),
  );
});
