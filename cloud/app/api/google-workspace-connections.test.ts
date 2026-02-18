import { Either } from "effect";
import { Effect } from "effect";

import {
  deleteConnection,
  getConnectionByClaw,
  hasConnection,
} from "@/app/api/google-workspace-connections";
import { DrizzleORM } from "@/db/client";
import { googleWorkspaceConnections } from "@/db/schema";
import { describe, expect, it, TestClawFixture } from "@/tests/db";

describe("Google Workspace Connections API", () => {
  describe("getConnectionByClaw", () => {
    it.effect("returns NotFoundError when no connection exists", () =>
      Effect.gen(function* () {
        const { claw } = yield* TestClawFixture;
        const result = yield* getConnectionByClaw(claw.id).pipe(Effect.either);
        expect(Either.isLeft(result)).toBe(true);
        if (Either.isLeft(result)) {
          expect(result.left._tag).toBe("NotFoundError");
        }
      }),
    );

    it.effect("returns connection when it exists", () =>
      Effect.gen(function* () {
        const { claw, owner } = yield* TestClawFixture;
        const client = yield* DrizzleORM;

        yield* client.insert(googleWorkspaceConnections).values({
          clawId: claw.id,
          userId: owner.id,
          encryptedRefreshToken: "encrypted-token",
          refreshTokenKeyId: "CLAW_SECRETS_ENCRYPTION_KEY_V1",
          scopes: "gmail.send calendar",
          connectedEmail: "test@example.com",
        });

        const connection = yield* getConnectionByClaw(claw.id);
        expect(connection.clawId).toBe(claw.id);
        expect(connection.connectedEmail).toBe("test@example.com");
        expect(connection.scopes).toBe("gmail.send calendar");
        expect(connection.userId).toBe(owner.id);
      }),
    );

    it.effect("does not return encrypted fields in public connection", () =>
      Effect.gen(function* () {
        const { claw, owner } = yield* TestClawFixture;
        const client = yield* DrizzleORM;

        yield* client.insert(googleWorkspaceConnections).values({
          clawId: claw.id,
          userId: owner.id,
          encryptedRefreshToken: "encrypted-token",
          refreshTokenKeyId: "CLAW_SECRETS_ENCRYPTION_KEY_V1",
          scopes: "gmail.send",
          connectedEmail: "test@example.com",
        });

        const connection = yield* getConnectionByClaw(claw.id);
        // Public type should not include sensitive fields
        expect("encryptedRefreshToken" in connection).toBe(false);
        expect("refreshTokenKeyId" in connection).toBe(false);
      }),
    );
  });

  describe("hasConnection", () => {
    it.effect("returns false when no connection exists", () =>
      Effect.gen(function* () {
        const { claw } = yield* TestClawFixture;
        const exists = yield* hasConnection(claw.id);
        expect(exists).toBe(false);
      }),
    );

    it.effect("returns true when connection exists", () =>
      Effect.gen(function* () {
        const { claw, owner } = yield* TestClawFixture;
        const client = yield* DrizzleORM;

        yield* client.insert(googleWorkspaceConnections).values({
          clawId: claw.id,
          userId: owner.id,
          encryptedRefreshToken: "encrypted-token",
          refreshTokenKeyId: "CLAW_SECRETS_ENCRYPTION_KEY_V1",
          scopes: "gmail.send",
          connectedEmail: "test@example.com",
        });

        const exists = yield* hasConnection(claw.id);
        expect(exists).toBe(true);
      }),
    );

    it.effect("returns false for non-existent claw ID", () =>
      Effect.gen(function* () {
        const exists = yield* hasConnection(
          "00000000-0000-0000-0000-000000000000",
        );
        expect(exists).toBe(false);
      }),
    );
  });

  describe("deleteConnection", () => {
    it.effect("deletes an existing connection", () =>
      Effect.gen(function* () {
        const { claw, owner } = yield* TestClawFixture;
        const client = yield* DrizzleORM;

        yield* client.insert(googleWorkspaceConnections).values({
          clawId: claw.id,
          userId: owner.id,
          encryptedRefreshToken: "encrypted-token",
          refreshTokenKeyId: "CLAW_SECRETS_ENCRYPTION_KEY_V1",
          scopes: "gmail.send",
          connectedEmail: "test@example.com",
        });

        // Verify it exists
        const existsBefore = yield* hasConnection(claw.id);
        expect(existsBefore).toBe(true);

        yield* deleteConnection(claw.id);

        // Verify it's deleted
        const existsAfter = yield* hasConnection(claw.id);
        expect(existsAfter).toBe(false);
      }),
    );

    it.effect("succeeds when no connection exists (no-op)", () =>
      Effect.gen(function* () {
        const { claw } = yield* TestClawFixture;
        // Should not throw
        yield* deleteConnection(claw.id);
      }),
    );
  });
});
