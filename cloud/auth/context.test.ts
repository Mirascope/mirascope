import { describe, it, expect } from "@effect/vitest";
import { Effect, Layer } from "effect";

import type { PublicUser, EnvironmentApiKeyAuth } from "@/db/schema";

import { Authentication, type AuthResult } from "@/auth/context";
import { UnauthorizedError } from "@/errors";

describe("Authentication", () => {
  const mockUser: PublicUser = {
    id: "test-user-id",
    email: "test@example.com",
    name: "Test User",
    accountType: "user" as const,
    deletedAt: null,
  };

  const mockApiKeyInfo: EnvironmentApiKeyAuth = {
    apiKeyId: "test-api-key-id",
    organizationId: "test-org-id",
    projectId: "test-project-id",
    environmentId: "test-env-id",
    ownerId: mockUser.id,
    ownerEmail: mockUser.email,
    ownerName: mockUser.name,
    ownerAccountType: "user" as const,
    ownerDeletedAt: mockUser.deletedAt,
    clawId: null,
  };

  describe("ApiKey", () => {
    it.effect("should return auth result when apiKeyInfo is present", () => {
      const authWithApiKey: AuthResult = {
        user: mockUser,
        apiKeyInfo: mockApiKeyInfo,
      };

      const layer = Layer.succeed(Authentication, authWithApiKey);
      return Effect.gen(function* () {
        const result = yield* Authentication.ApiKey;
        expect(result.user).toEqual(mockUser);
        expect(result.apiKeyInfo).toEqual(mockApiKeyInfo);
      }).pipe(Effect.provide(layer));
    });

    it.effect(
      "should fail with UnauthorizedError when apiKeyInfo is not present",
      () => {
        const authWithoutApiKey: AuthResult = {
          user: mockUser,
        };

        const layer = Layer.succeed(Authentication, authWithoutApiKey);
        return Effect.gen(function* () {
          const error = yield* Authentication.ApiKey.pipe(Effect.flip);
          expect(error).toBeInstanceOf(UnauthorizedError);
          expect(error.message).toBe(
            "API key required. Provide X-API-Key header or Bearer token.",
          );
        }).pipe(Effect.provide(layer));
      },
    );
  });
});
