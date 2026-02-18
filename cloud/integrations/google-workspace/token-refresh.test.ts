import { eq } from "drizzle-orm";
import { Effect, Either } from "effect";
import { afterEach, beforeEach, vi } from "vitest";

import { encryptSecrets } from "@/claws/crypto";
import { DrizzleORM } from "@/db/client";
import { googleWorkspaceConnections } from "@/db/schema";
import {
  TokenDecryptionError,
  TokenNotFoundError,
  TokenRefreshError,
  refreshAccessToken,
} from "@/integrations/google-workspace/token-refresh";
import { describe, expect, it, TestClawFixture } from "@/tests/db";

// Mock global fetch for Google token endpoint
const mockFetch = vi.fn();

beforeEach(() => {
  vi.stubGlobal("fetch", mockFetch);
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("Token Refresh", () => {
  describe("error classes", () => {
    it("TokenNotFoundError has correct tag", () => {
      const error = new TokenNotFoundError({
        message: "test",
        clawId: "claw-1",
      });
      expect(error._tag).toBe("TokenNotFoundError");
      expect(error.clawId).toBe("claw-1");
    });

    it("TokenRefreshError has correct tag", () => {
      const error = new TokenRefreshError({ message: "test" });
      expect(error._tag).toBe("TokenRefreshError");
    });

    it("TokenDecryptionError has correct tag", () => {
      const error = new TokenDecryptionError({ message: "test" });
      expect(error._tag).toBe("TokenDecryptionError");
    });
  });

  describe("refreshAccessToken", () => {
    it.effect("returns TokenNotFoundError when no connection exists", () =>
      Effect.gen(function* () {
        const { claw } = yield* TestClawFixture;
        const result = yield* refreshAccessToken(claw.id).pipe(Effect.either);
        expect(Either.isLeft(result)).toBe(true);
        if (Either.isLeft(result)) {
          expect(result.left._tag).toBe("TokenNotFoundError");
        }
      }),
    );

    it.effect("refreshes access token successfully", () =>
      Effect.gen(function* () {
        const { claw, owner } = yield* TestClawFixture;
        const client = yield* DrizzleORM;

        // Encrypt a real refresh token
        const { ciphertext, keyId } = yield* encryptSecrets({
          refresh_token: "test-refresh-token",
        });

        // Insert a connection with encrypted token
        yield* client.insert(googleWorkspaceConnections).values({
          clawId: claw.id,
          userId: owner.id,
          encryptedRefreshToken: ciphertext,
          refreshTokenKeyId: keyId,
          scopes: "gmail.send",
          connectedEmail: "test@example.com",
        });

        // Mock the Google token endpoint
        mockFetch.mockResolvedValueOnce(
          new Response(
            JSON.stringify({
              access_token: "new-access-token",
              expires_in: 3600,
            }),
          ),
        );

        const result = yield* refreshAccessToken(claw.id);
        expect(result.accessToken).toBe("new-access-token");
        expect(result.expiresIn).toBe(3600);

        // Verify fetch was called with correct params
        expect(mockFetch).toHaveBeenCalledWith(
          "https://oauth2.googleapis.com/token",
          expect.objectContaining({
            method: "POST",
          }),
        );
      }),
    );

    it.effect("returns TokenRefreshError when Google rejects the token", () =>
      Effect.gen(function* () {
        const { claw, owner } = yield* TestClawFixture;
        const client = yield* DrizzleORM;

        const { ciphertext, keyId } = yield* encryptSecrets({
          refresh_token: "expired-refresh-token",
        });

        yield* client.insert(googleWorkspaceConnections).values({
          clawId: claw.id,
          userId: owner.id,
          encryptedRefreshToken: ciphertext,
          refreshTokenKeyId: keyId,
          scopes: "gmail.send",
          connectedEmail: "test@example.com",
        });

        // Mock Google returning an error
        mockFetch.mockResolvedValueOnce(
          new Response(
            JSON.stringify({
              error: "invalid_grant",
              error_description: "Token has been revoked",
            }),
          ),
        );

        const result = yield* refreshAccessToken(claw.id).pipe(Effect.either);
        expect(Either.isLeft(result)).toBe(true);
        if (Either.isLeft(result)) {
          expect(result.left._tag).toBe("TokenRefreshError");
          expect(result.left.message).toContain("Token has been revoked");
        }
      }),
    );

    it.effect("returns TokenRefreshError when fetch fails", () =>
      Effect.gen(function* () {
        const { claw, owner } = yield* TestClawFixture;
        const client = yield* DrizzleORM;

        const { ciphertext, keyId } = yield* encryptSecrets({
          refresh_token: "test-refresh-token",
        });

        yield* client.insert(googleWorkspaceConnections).values({
          clawId: claw.id,
          userId: owner.id,
          encryptedRefreshToken: ciphertext,
          refreshTokenKeyId: keyId,
          scopes: "gmail.send",
          connectedEmail: "test@example.com",
        });

        // Mock fetch throwing
        mockFetch.mockRejectedValueOnce(new Error("Network error"));

        const result = yield* refreshAccessToken(claw.id).pipe(Effect.either);
        expect(Either.isLeft(result)).toBe(true);
        if (Either.isLeft(result)) {
          expect(result.left._tag).toBe("TokenRefreshError");
        }
      }),
    );

    it.effect("returns TokenDecryptionError when decryption fails", () =>
      Effect.gen(function* () {
        const { claw, owner } = yield* TestClawFixture;
        const client = yield* DrizzleORM;

        // Insert connection with valid base64 but invalid encrypted data
        yield* client.insert(googleWorkspaceConnections).values({
          clawId: claw.id,
          userId: owner.id,
          encryptedRefreshToken: btoa("not-valid-aes-gcm-ciphertext"),
          refreshTokenKeyId: "CLAW_SECRETS_ENCRYPTION_KEY_V1",
          scopes: "gmail.send",
          connectedEmail: "test@example.com",
        });

        const result = yield* refreshAccessToken(claw.id).pipe(Effect.either);
        expect(Either.isLeft(result)).toBe(true);
        if (Either.isLeft(result)) {
          expect(result.left._tag).toBe("TokenDecryptionError");
        }
      }),
    );

    it.effect(
      "updates tokenExpiresAt in database after successful refresh",
      () =>
        Effect.gen(function* () {
          const { claw, owner } = yield* TestClawFixture;
          const client = yield* DrizzleORM;

          const { ciphertext, keyId } = yield* encryptSecrets({
            refresh_token: "test-refresh-token",
          });

          yield* client.insert(googleWorkspaceConnections).values({
            clawId: claw.id,
            userId: owner.id,
            encryptedRefreshToken: ciphertext,
            refreshTokenKeyId: keyId,
            scopes: "gmail.send",
            connectedEmail: "test@example.com",
          });

          mockFetch.mockResolvedValueOnce(
            new Response(
              JSON.stringify({
                access_token: "new-access-token",
                expires_in: 7200,
              }),
            ),
          );

          yield* refreshAccessToken(claw.id);

          // Check that tokenExpiresAt was updated
          const [updated] = yield* client
            .select({
              tokenExpiresAt: googleWorkspaceConnections.tokenExpiresAt,
            })
            .from(googleWorkspaceConnections)
            .where(eq(googleWorkspaceConnections.clawId, claw.id))
            .limit(1);

          // tokenExpiresAt should be set (not null)
          expect(updated?.tokenExpiresAt).toBeDefined();
        }),
    );
  });
});
