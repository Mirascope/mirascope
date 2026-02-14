import { describe, it, expect } from "@effect/vitest";
import { Effect, Layer } from "effect";

import type {
  PublicUser,
  EnvironmentApiKeyAuth,
  OrgApiKeyAuth,
} from "@/db/schema";

import { Authentication, type AuthResult } from "@/auth/context";
import { UnauthorizedError } from "@/errors";

// ---------------------------------------------------------------------------
// Shared fixtures
// ---------------------------------------------------------------------------

const mockUser: PublicUser = {
  id: "test-user-id",
  email: "test@example.com",
  name: "Test User",
  accountType: "user" as const,
  deletedAt: null,
};

const sharedOwnerFields = {
  ownerId: mockUser.id,
  ownerEmail: mockUser.email,
  ownerName: mockUser.name,
  ownerAccountType: "user" as const,
  ownerDeletedAt: mockUser.deletedAt,
  clawId: null,
};

const envApiKeyInfo: EnvironmentApiKeyAuth = {
  apiKeyId: "test-env-key-id",
  organizationId: "test-org-id",
  projectId: "test-project-id",
  environmentId: "test-env-id",
  ...sharedOwnerFields,
};

const orgApiKeyInfo: OrgApiKeyAuth = {
  apiKeyId: "test-org-key-id",
  organizationId: "test-org-id",
  environmentId: null,
  ...sharedOwnerFields,
};

// ---------------------------------------------------------------------------
// Authentication.ApiKey — accepts both scopes
// ---------------------------------------------------------------------------

describe("Authentication.ApiKey", () => {
  it.effect("should return auth result for environment-scoped key", () => {
    const auth: AuthResult = { user: mockUser, apiKeyInfo: envApiKeyInfo };
    return Effect.gen(function* () {
      const result = yield* Authentication.ApiKey;
      expect(result.apiKeyInfo.apiKeyId).toBe("test-env-key-id");
      expect(result.apiKeyInfo.organizationId).toBe("test-org-id");
    }).pipe(Effect.provide(Layer.succeed(Authentication, auth)));
  });

  it.effect("should return auth result for org-scoped key", () => {
    const auth: AuthResult = { user: mockUser, apiKeyInfo: orgApiKeyInfo };
    return Effect.gen(function* () {
      const result = yield* Authentication.ApiKey;
      expect(result.apiKeyInfo.apiKeyId).toBe("test-org-key-id");
      expect(result.apiKeyInfo.environmentId).toBeNull();
    }).pipe(Effect.provide(Layer.succeed(Authentication, auth)));
  });

  it.effect("should fail with UnauthorizedError when no apiKeyInfo", () => {
    const auth: AuthResult = { user: mockUser };
    return Effect.gen(function* () {
      const error = yield* Authentication.ApiKey.pipe(Effect.flip);
      expect(error).toBeInstanceOf(UnauthorizedError);
      expect(error.message).toBe(
        "API key required. Provide X-API-Key header or Bearer token.",
      );
    }).pipe(Effect.provide(Layer.succeed(Authentication, auth)));
  });
});

// ---------------------------------------------------------------------------
// Authentication.EnvironmentApiKey — narrows to env-scoped only
// ---------------------------------------------------------------------------

describe("Authentication.EnvironmentApiKey", () => {
  it.effect("should succeed for environment-scoped key", () => {
    const auth: AuthResult = { user: mockUser, apiKeyInfo: envApiKeyInfo };
    return Effect.gen(function* () {
      const result = yield* Authentication.EnvironmentApiKey;
      expect(result.apiKeyInfo.environmentId).toBe("test-env-id");
      expect(result.apiKeyInfo.projectId).toBe("test-project-id");
    }).pipe(Effect.provide(Layer.succeed(Authentication, auth)));
  });

  it.effect("should reject org-scoped key", () => {
    const auth: AuthResult = { user: mockUser, apiKeyInfo: orgApiKeyInfo };
    return Effect.gen(function* () {
      const error = yield* Authentication.EnvironmentApiKey.pipe(Effect.flip);
      expect(error).toBeInstanceOf(UnauthorizedError);
      expect(error.message).toContain("Environment-scoped API key required");
    }).pipe(Effect.provide(Layer.succeed(Authentication, auth)));
  });

  it.effect("should fail when no apiKeyInfo", () => {
    const auth: AuthResult = { user: mockUser };
    return Effect.gen(function* () {
      const error = yield* Authentication.EnvironmentApiKey.pipe(Effect.flip);
      expect(error).toBeInstanceOf(UnauthorizedError);
    }).pipe(Effect.provide(Layer.succeed(Authentication, auth)));
  });
});

// ---------------------------------------------------------------------------
// Authentication.OrgApiKey — narrows to org-scoped only
// ---------------------------------------------------------------------------

describe("Authentication.OrgApiKey", () => {
  it.effect("should succeed for org-scoped key", () => {
    const auth: AuthResult = { user: mockUser, apiKeyInfo: orgApiKeyInfo };
    return Effect.gen(function* () {
      const result = yield* Authentication.OrgApiKey;
      expect(result.apiKeyInfo.environmentId).toBeNull();
      expect(result.apiKeyInfo.organizationId).toBe("test-org-id");
    }).pipe(Effect.provide(Layer.succeed(Authentication, auth)));
  });

  it.effect("should reject environment-scoped key", () => {
    const auth: AuthResult = { user: mockUser, apiKeyInfo: envApiKeyInfo };
    return Effect.gen(function* () {
      const error = yield* Authentication.OrgApiKey.pipe(Effect.flip);
      expect(error).toBeInstanceOf(UnauthorizedError);
      expect(error.message).toContain("Org-scoped API key required");
    }).pipe(Effect.provide(Layer.succeed(Authentication, auth)));
  });

  it.effect("should fail when no apiKeyInfo", () => {
    const auth: AuthResult = { user: mockUser };
    return Effect.gen(function* () {
      const error = yield* Authentication.OrgApiKey.pipe(Effect.flip);
      expect(error).toBeInstanceOf(UnauthorizedError);
    }).pipe(Effect.provide(Layer.succeed(Authentication, auth)));
  });
});
