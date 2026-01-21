import { Effect } from "effect";
import { describe, it, expect, TestAuthFixture } from "@/tests/auth";
import { Database } from "@/db/database";
import {
  getSessionIdFromCookie,
  getOAuthStateFromCookie,
  setSessionCookie,
  clearSessionCookie,
  setOAuthStateCookie,
  clearOAuthStateCookie,
  authenticate,
  type PathParameters,
} from "@/auth/utils";
import { UnauthorizedError } from "@/errors";
import { createMockSettings } from "@/tests/settings";

describe("getSessionIdFromCookie", () => {
  it("should extract session ID from cookie", () => {
    const request = new Request("http://localhost/api", {
      headers: { Cookie: "session=test-session-id" },
    });

    expect(getSessionIdFromCookie(request)).toBe("test-session-id");
  });

  it("should return null if no cookie header", () => {
    const request = new Request("http://localhost/api");

    expect(getSessionIdFromCookie(request)).toBeNull();
  });

  it("should return null if session cookie not present", () => {
    const request = new Request("http://localhost/api", {
      headers: { Cookie: "other=value" },
    });

    expect(getSessionIdFromCookie(request)).toBeNull();
  });

  it("should handle multiple cookies", () => {
    const request = new Request("http://localhost/api", {
      headers: { Cookie: "other=value; session=my-session; another=test" },
    });

    expect(getSessionIdFromCookie(request)).toBe("my-session");
  });

  it("should return null for empty cookie value", () => {
    const request = new Request("http://localhost/api", {
      headers: { Cookie: "session=" },
    });

    expect(getSessionIdFromCookie(request)).toBeNull();
  });
});

describe("getOAuthStateFromCookie", () => {
  it("should extract oauth_state from cookie", () => {
    const request = new Request("http://localhost/api", {
      headers: { Cookie: "oauth_state=random-state-value" },
    });

    expect(getOAuthStateFromCookie(request)).toBe("random-state-value");
  });

  it("should return null if oauth_state not present", () => {
    const request = new Request("http://localhost/api", {
      headers: { Cookie: "session=test" },
    });

    expect(getOAuthStateFromCookie(request)).toBeNull();
  });
});

describe("setSessionCookie", () => {
  it("should create a session cookie string", () => {
    const settings = createMockSettings();
    const cookie = setSessionCookie("test-session-id", settings);

    expect(cookie).toContain("session=test-session-id");
    expect(cookie).toContain("HttpOnly");
    expect(cookie).toContain("SameSite=Lax");
    expect(cookie).toContain("Max-Age=604800"); // 7 days
    expect(cookie).toContain("Path=/");
  });

  it("should include Secure flag in production", () => {
    const settings = createMockSettings({
      env: "production",
      siteUrl: "http://localhost:3000", // Even with http, production should be secure
    });

    const cookie = setSessionCookie("test-session-id", settings);
    expect(cookie).toContain("Secure");
  });

  it("should include Secure flag when siteUrl is https", () => {
    const settings = createMockSettings({
      env: "development",
      siteUrl: "https://example.com",
    });

    const cookie = setSessionCookie("test-session-id", settings);
    expect(cookie).toContain("Secure");
  });

  it("should not include Secure flag in development with http", () => {
    const settings = createMockSettings({
      env: "development",
      siteUrl: "http://localhost:3000",
    });

    const cookie = setSessionCookie("test-session-id", settings);
    expect(cookie).not.toContain("Secure");
  });
});

describe("clearSessionCookie", () => {
  it("should create an expired session cookie", () => {
    const settings = createMockSettings();
    const cookie = clearSessionCookie(settings);

    expect(cookie).toContain("session=;");
    expect(cookie).toContain("Expires=Thu, 01 Jan 1970 00:00:00 GMT");
    expect(cookie).toContain("HttpOnly");
    expect(cookie).toContain("SameSite=Lax");
    expect(cookie).toContain("Path=/");
  });

  it("should include Secure flag in production", () => {
    const settings = createMockSettings({
      env: "production",
      siteUrl: "http://localhost:3000", // Even with http, production should be secure
    });

    const cookie = clearSessionCookie(settings);
    expect(cookie).toContain("Secure");
  });

  it("should include Secure flag when siteUrl is https", () => {
    const settings = createMockSettings({
      env: "development",
      siteUrl: "https://example.com",
    });

    const cookie = clearSessionCookie(settings);
    expect(cookie).toContain("Secure");
  });

  it("should not include Secure flag in development with http", () => {
    const settings = createMockSettings({
      env: "development",
      siteUrl: "http://localhost:3000",
    });

    const cookie = clearSessionCookie(settings);
    expect(cookie).not.toContain("Secure");
  });
});

describe("setOAuthStateCookie", () => {
  it("should create an OAuth state cookie string", () => {
    const settings = createMockSettings();
    const cookie = setOAuthStateCookie("random-state", settings);

    expect(cookie).toContain("oauth_state=random-state");
    expect(cookie).toContain("HttpOnly");
    expect(cookie).toContain("SameSite=Lax");
    expect(cookie).toContain("Max-Age=600"); // 10 minutes
    expect(cookie).toContain("Path=/");
  });

  it("should include Secure flag in production", () => {
    const settings = createMockSettings({
      env: "production",
      siteUrl: "http://localhost:3000", // Even with http, production should be secure
    });

    const cookie = setOAuthStateCookie("random-state", settings);
    expect(cookie).toContain("Secure");
  });

  it("should include Secure flag when siteUrl is https", () => {
    const settings = createMockSettings({
      env: "development",
      siteUrl: "https://example.com",
    });

    const cookie = setOAuthStateCookie("random-state", settings);
    expect(cookie).toContain("Secure");
  });

  it("should not include Secure flag in development with http", () => {
    const settings = createMockSettings({
      env: "development",
      siteUrl: "http://localhost:3000",
    });

    const cookie = setOAuthStateCookie("random-state", settings);
    expect(cookie).not.toContain("Secure");
  });
});

describe("clearOAuthStateCookie", () => {
  it("should create an expired OAuth state cookie", () => {
    const settings = createMockSettings();
    const cookie = clearOAuthStateCookie(settings);

    expect(cookie).toContain("oauth_state=;");
    expect(cookie).toContain("Expires=Thu, 01 Jan 1970 00:00:00 GMT");
    expect(cookie).toContain("HttpOnly");
    expect(cookie).toContain("SameSite=Lax");
    expect(cookie).toContain("Path=/");
  });

  it("should include Secure flag in production", () => {
    const settings = createMockSettings({
      env: "production",
      siteUrl: "http://localhost:3000", // Even with http, production should be secure
    });

    const cookie = clearOAuthStateCookie(settings);
    expect(cookie).toContain("Secure");
  });

  it("should include Secure flag when siteUrl is https", () => {
    const settings = createMockSettings({
      env: "development",
      siteUrl: "https://example.com",
    });

    const cookie = clearOAuthStateCookie(settings);
    expect(cookie).toContain("Secure");
  });

  it("should not include Secure flag in development with http", () => {
    const settings = createMockSettings({
      env: "development",
      siteUrl: "http://localhost:3000",
    });

    const cookie = clearOAuthStateCookie(settings);
    expect(cookie).not.toContain("Secure");
  });
});

describe("authenticate - path parameter validation", () => {
  it.effect(
    "should authenticate with valid API key and matching environmentId",
    () =>
      Effect.gen(function* () {
        const { owner, environment, apiKey } = yield* TestAuthFixture;

        const request = new Request("https://example.com/api/test", {
          headers: {
            "X-API-Key": apiKey,
          },
        });

        const pathParams: PathParameters = {
          environmentId: environment.id,
        };

        const result = yield* authenticate(request, pathParams);

        expect(result.user).not.toBeNull();
        expect(result.user.id).toBe(owner.id);
        expect(result.apiKeyInfo).toBeDefined();
      }),
  );

  it.effect("should reject API key with mismatched environmentId", () =>
    Effect.gen(function* () {
      const { otherEnvironment, apiKey } = yield* TestAuthFixture;

      const request = new Request("https://example.com/api/test", {
        headers: {
          "X-API-Key": apiKey,
        },
      });

      const pathParams: PathParameters = {
        environmentId: otherEnvironment.id, // Different environment!
      };

      const result = yield* authenticate(request, pathParams).pipe(Effect.flip);

      expect(result).toBeInstanceOf(UnauthorizedError);
      expect(result.message).toBe(
        "The environment ID in the request path does not match the environment associated with this API key",
      );
    }),
  );

  it.effect(
    "should authenticate with valid API key and matching projectId",
    () =>
      Effect.gen(function* () {
        const { owner, project, apiKey } = yield* TestAuthFixture;

        const request = new Request("https://example.com/api/test", {
          headers: {
            "X-API-Key": apiKey,
          },
        });

        const pathParams: PathParameters = {
          projectId: project.id,
        };

        const result = yield* authenticate(request, pathParams);

        expect(result.user).not.toBeNull();
        expect(result.user.id).toBe(owner.id);
      }),
  );

  it.effect("should reject API key with mismatched projectId", () =>
    Effect.gen(function* () {
      const { apiKey } = yield* TestAuthFixture;

      const request = new Request("https://example.com/api/test", {
        headers: {
          "X-API-Key": apiKey,
        },
      });

      const pathParams: PathParameters = {
        projectId: "00000000-0000-0000-0000-000000000000", // Wrong project
      };

      const result = yield* authenticate(request, pathParams).pipe(Effect.flip);

      expect(result).toBeInstanceOf(UnauthorizedError);
      expect(result.message).toBe(
        "The project ID in the request path does not match the project associated with this API key",
      );
    }),
  );

  it.effect(
    "should authenticate with valid API key and matching organizationId",
    () =>
      Effect.gen(function* () {
        const { owner, org, apiKey } = yield* TestAuthFixture;

        const request = new Request("https://example.com/api/test", {
          headers: {
            "X-API-Key": apiKey,
          },
        });

        const pathParams: PathParameters = {
          organizationId: org.id,
        };

        const result = yield* authenticate(request, pathParams);

        expect(result.user).not.toBeNull();
        expect(result.user.id).toBe(owner.id);
      }),
  );

  it.effect("should reject API key with mismatched organizationId", () =>
    Effect.gen(function* () {
      const { apiKey } = yield* TestAuthFixture;

      const request = new Request("https://example.com/api/test", {
        headers: {
          "X-API-Key": apiKey,
        },
      });

      const pathParams: PathParameters = {
        organizationId: "00000000-0000-0000-0000-000000000000", // Wrong org
      };

      const result = yield* authenticate(request, pathParams).pipe(Effect.flip);

      expect(result).toBeInstanceOf(UnauthorizedError);
      expect(result.message).toBe(
        "The organization ID in the request path does not match the organization associated with this API key",
      );
    }),
  );

  it.effect(
    "should authenticate with valid API key and all matching parameters",
    () =>
      Effect.gen(function* () {
        const { owner, org, project, environment, apiKey } =
          yield* TestAuthFixture;

        const request = new Request("https://example.com/api/test", {
          headers: {
            "X-API-Key": apiKey,
          },
        });

        const pathParams: PathParameters = {
          organizationId: org.id,
          projectId: project.id,
          environmentId: environment.id,
        };

        const result = yield* authenticate(request, pathParams);

        expect(result.user).not.toBeNull();
        expect(result.user.id).toBe(owner.id);
      }),
  );

  it.effect("should reject API key when any parameter mismatches", () =>
    Effect.gen(function* () {
      const { org, project, otherEnvironment, apiKey } = yield* TestAuthFixture;

      const request = new Request("https://example.com/api/test", {
        headers: {
          "X-API-Key": apiKey,
        },
      });

      // Correct org and project, but wrong environment
      const pathParams: PathParameters = {
        organizationId: org.id,
        projectId: project.id,
        environmentId: otherEnvironment.id,
      };

      const result = yield* authenticate(request, pathParams).pipe(Effect.flip);

      expect(result).toBeInstanceOf(UnauthorizedError);
      expect(result.message).toBe(
        "The environment ID in the request path does not match the environment associated with this API key",
      );
    }),
  );

  it.effect(
    "should authenticate with valid API key when no path parameters provided",
    () =>
      Effect.gen(function* () {
        const { owner, apiKey } = yield* TestAuthFixture;

        const request = new Request("https://example.com/api/test", {
          headers: {
            "X-API-Key": apiKey,
          },
        });

        const result = yield* authenticate(request, undefined);

        expect(result.user).not.toBeNull();
        expect(result.user.id).toBe(owner.id);
      }),
  );

  it.effect("should authenticate with Authorization Bearer header", () =>
    Effect.gen(function* () {
      const { owner, environment, apiKey } = yield* TestAuthFixture;

      const request = new Request("https://example.com/api/test", {
        headers: {
          Authorization: `Bearer ${apiKey}`,
        },
      });

      const pathParams: PathParameters = {
        environmentId: environment.id,
      };

      const result = yield* authenticate(request, pathParams);

      expect(result.user).not.toBeNull();
      expect(result.user.id).toBe(owner.id);
    }),
  );

  it.effect("should reject invalid API key", () =>
    Effect.gen(function* () {
      const request = new Request("https://example.com/api/test", {
        headers: {
          "X-API-Key": "mk_invalid_key_12345678901234567890123456789012",
        },
      });

      const result = yield* authenticate(request).pipe(Effect.flip);

      expect(result).toBeInstanceOf(UnauthorizedError);
      expect(result.message).toBe("Invalid API key");
    }),
  );

  it.effect("should reject request with no authentication", () =>
    Effect.gen(function* () {
      const request = new Request("https://example.com/api/test");

      const result = yield* authenticate(request).pipe(Effect.flip);

      expect(result).toBeInstanceOf(UnauthorizedError);
      expect(result.message).toBe("Authentication required");
    }),
  );

  it.effect("should reject invalid session ID", () =>
    Effect.gen(function* () {
      const request = new Request("https://example.com/api/test", {
        headers: {
          Cookie: "session=00000000-0000-0000-0000-000000000000",
        },
      });

      const result = yield* authenticate(request).pipe(Effect.flip);

      expect(result).toBeInstanceOf(UnauthorizedError);
      expect(result.message).toBe("Invalid session");
    }),
  );

  it.effect("should authenticate with valid session cookie", () =>
    Effect.gen(function* () {
      const { owner } = yield* TestAuthFixture;
      const db = yield* Database;

      // Create a session
      const expiresAt = new Date(Date.now() + 1000 * 60 * 60); // 1 hour
      const session = yield* db.sessions.create({
        userId: owner.id,
        data: { userId: owner.id, expiresAt },
      });

      const request = new Request("https://example.com/api/test", {
        headers: {
          Cookie: `session=${session.id}`,
        },
      });

      const result = yield* authenticate(request);

      expect(result.user).not.toBeNull();
      expect(result.user.id).toBe(owner.id);
      expect(result.apiKeyInfo).toBeUndefined();
    }),
  );

  it.effect("should prefer API key over session", () =>
    Effect.gen(function* () {
      const { apiKey, owner, admin } = yield* TestAuthFixture;
      const db = yield* Database;

      // Create a session for admin
      const expiresAt = new Date(Date.now() + 1000 * 60 * 60);
      const session = yield* db.sessions.create({
        userId: admin.id,
        data: { userId: admin.id, expiresAt },
      });

      // Request with both API key and session
      const request = new Request("http://localhost/api", {
        headers: {
          "X-API-Key": apiKey,
          Cookie: `session=${session.id}`,
        },
      });

      const result = yield* authenticate(request);

      // Should return the API key owner, not the session user
      expect(result.user.id).toBe(owner.id);
      expect(result.apiKeyInfo).toBeDefined();
    }),
  );
});

describe("authenticate - API key", () => {
  it.effect("returns user and apiKeyInfo when API key is valid", () =>
    Effect.gen(function* () {
      const { owner, environment, apiKey } = yield* TestAuthFixture;

      const request = new Request("https://example.com/api/test", {
        headers: {
          "X-API-Key": apiKey,
        },
      });

      const pathParams: PathParameters = {
        environmentId: environment.id,
      };

      const result = yield* authenticate(request, pathParams);

      expect(result.user.id).toBe(owner.id);
      expect(result.apiKeyInfo).toBeDefined();
      expect(result.apiKeyInfo?.environmentId).toBe(environment.id);
    }),
  );

  it.effect(
    "returns user with undefined apiKeyInfo when session cookie is valid",
    () =>
      Effect.gen(function* () {
        const { owner } = yield* TestAuthFixture;
        const db = yield* Database;

        const expiresAt = new Date(Date.now() + 1000 * 60 * 60);
        const session = yield* db.sessions.create({
          userId: owner.id,
          data: { userId: owner.id, expiresAt },
        });

        const request = new Request("https://example.com/api/test", {
          headers: {
            Cookie: `session=${session.id}`,
          },
        });

        const result = yield* authenticate(request);

        expect(result.user.id).toBe(owner.id);
        expect(result.apiKeyInfo).toBeUndefined();
      }),
  );

  it.effect("returns UnauthorizedError when no API key or session cookie", () =>
    Effect.gen(function* () {
      const request = new Request("https://example.com/api/test");

      const result = yield* authenticate(request).pipe(Effect.flip);

      expect(result).toBeInstanceOf(UnauthorizedError);
      expect(result.message).toBe("Authentication required");
    }),
  );

  it.effect("returns UnauthorizedError when session is invalid", () =>
    Effect.gen(function* () {
      const request = new Request("https://example.com/api/test", {
        headers: {
          Cookie: "session=invalid-session",
        },
      });

      const result = yield* authenticate(request).pipe(Effect.flip);

      expect(result).toBeInstanceOf(UnauthorizedError);
      expect(result.message).toBe("Invalid session");
    }),
  );
});
