import { Effect, Layer } from "effect";
import {
  getApiKeyFromRequest,
  API_KEY_HEADER,
  requireApiKeyAuth,
} from "@/auth/api-key";
import { AuthenticatedApiKey } from "@/auth/context";
import { describe, it, expect } from "@/tests/auth";
import type { ApiKeyInfo } from "@/db/schema";

describe("getApiKeyFromRequest", () => {
  it("should extract API key from X-API-Key header", () => {
    const request = new Request("http://localhost/api", {
      headers: { [API_KEY_HEADER]: "mk_test_key" },
    });

    expect(getApiKeyFromRequest(request)).toBe("mk_test_key");
  });

  it("should extract API key from Authorization Bearer header", () => {
    const request = new Request("http://localhost/api", {
      headers: { Authorization: "Bearer mk_test_key" },
    });

    expect(getApiKeyFromRequest(request)).toBe("mk_test_key");
  });

  it("should prefer X-API-Key over Authorization header", () => {
    const request = new Request("http://localhost/api", {
      headers: {
        [API_KEY_HEADER]: "mk_from_header",
        Authorization: "Bearer mk_from_auth",
      },
    });

    expect(getApiKeyFromRequest(request)).toBe("mk_from_header");
  });

  it("should return null if no API key provided", () => {
    const request = new Request("http://localhost/api");

    expect(getApiKeyFromRequest(request)).toBeNull();
  });

  it("should return null for non-Bearer Authorization header", () => {
    const request = new Request("http://localhost/api", {
      headers: { Authorization: "Basic dXNlcjpwYXNz" },
    });

    expect(getApiKeyFromRequest(request)).toBeNull();
  });
});

describe("requireApiKeyAuth", () => {
  const mockApiKeyInfo: ApiKeyInfo = {
    apiKeyId: "api-key-id",
    environmentId: "env-id",
    projectId: "project-id",
    organizationId: "org-id",
    ownerId: "owner-id",
    ownerEmail: "owner@example.com",
    ownerName: "Test Owner",
    ownerDeletedAt: null,
  };

  it("should return ApiKeyInfo when AuthenticatedApiKey context is provided", async () => {
    const layer = Layer.succeed(AuthenticatedApiKey, mockApiKeyInfo);

    const result = await Effect.runPromise(
      requireApiKeyAuth.pipe(Effect.provide(layer)),
    );

    expect(result).toEqual(mockApiKeyInfo);
    expect(result.apiKeyId).toBe("api-key-id");
    expect(result.environmentId).toBe("env-id");
  });

  it("should fail with UnauthorizedError when AuthenticatedApiKey context is not provided", async () => {
    const result = await Effect.runPromise(Effect.either(requireApiKeyAuth));

    expect(result._tag).toBe("Left");
    if (result._tag === "Left") {
      expect(result.left._tag).toBe("UnauthorizedError");
      expect(result.left.message).toContain("API key required");
    }
  });
});
