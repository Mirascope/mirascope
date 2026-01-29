import { Effect, Layer } from "effect";
import { describe, it, expect } from "vitest";

import type { PublicUser, ApiKeyInfo } from "@/db/schema";

import { Authentication, type AuthResult } from "@/auth/context";
import { UnauthorizedError } from "@/errors";

describe("Authentication", () => {
  const mockUser: PublicUser = {
    id: "test-user-id",
    email: "test@example.com",
    name: "Test User",
    deletedAt: null,
  };

  const mockApiKeyInfo: ApiKeyInfo = {
    apiKeyId: "test-api-key-id",
    organizationId: "test-org-id",
    projectId: "test-project-id",
    environmentId: "test-env-id",
    ownerId: mockUser.id,
    ownerEmail: mockUser.email,
    ownerName: mockUser.name,
    ownerDeletedAt: mockUser.deletedAt,
  };

  describe("ApiKey", () => {
    it("should return auth result when apiKeyInfo is present", async () => {
      const authWithApiKey: AuthResult = {
        user: mockUser,
        apiKeyInfo: mockApiKeyInfo,
      };

      const program = Effect.gen(function* () {
        const result = yield* Authentication.ApiKey;
        return result;
      });

      const layer = Layer.succeed(Authentication, authWithApiKey);
      const result = await Effect.runPromise(
        program.pipe(Effect.provide(layer)),
      );

      expect(result.user).toEqual(mockUser);
      expect(result.apiKeyInfo).toEqual(mockApiKeyInfo);
    });

    it("should fail with UnauthorizedError when apiKeyInfo is not present", async () => {
      const authWithoutApiKey: AuthResult = {
        user: mockUser,
      };

      const program = Effect.gen(function* () {
        const result = yield* Authentication.ApiKey;
        return result;
      });

      const layer = Layer.succeed(Authentication, authWithoutApiKey);
      const error = await Effect.runPromise(
        program.pipe(Effect.provide(layer), Effect.flip),
      );

      expect(error).toBeInstanceOf(UnauthorizedError);
      expect(error.message).toBe(
        "API key required. Provide X-API-Key header or Bearer token.",
      );
    });
  });
});
