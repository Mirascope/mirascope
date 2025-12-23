import { Effect } from "effect";
import { describe, it, expect, TestAuthFixture } from "@/tests/auth";
import { Database } from "@/db";
import {
  getSessionIdFromCookie,
  getOAuthStateFromCookie,
  setSessionCookie,
  clearSessionCookie,
  setOAuthStateCookie,
  clearOAuthStateCookie,
  getAuthenticatedUser,
  type PathParameters,
} from "@/auth/utils";
import { UnauthorizedError } from "@/errors";

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
    const cookie = setSessionCookie("test-session-id");

    expect(cookie).toContain("session=test-session-id");
    expect(cookie).toContain("HttpOnly");
    expect(cookie).toContain("SameSite=Lax");
    expect(cookie).toContain("Max-Age=604800"); // 7 days
    expect(cookie).toContain("Path=/");
  });

  it("should include Secure flag in production", () => {
    const originalEnv = process.env.ENVIRONMENT;
    process.env.ENVIRONMENT = "production";

    const cookie = setSessionCookie("test-session-id");
    expect(cookie).toContain("Secure");

    process.env.ENVIRONMENT = originalEnv;
  });

  it("should include Secure flag when SITE_URL is https", () => {
    const originalEnv = process.env.ENVIRONMENT;
    const originalSiteUrl = process.env.SITE_URL;
    process.env.ENVIRONMENT = "development";
    process.env.SITE_URL = "https://example.com";

    const cookie = setSessionCookie("test-session-id");
    expect(cookie).toContain("Secure");

    process.env.ENVIRONMENT = originalEnv;
    process.env.SITE_URL = originalSiteUrl;
  });
});

describe("clearSessionCookie", () => {
  it("should create an expired session cookie", () => {
    const cookie = clearSessionCookie();

    expect(cookie).toContain("session=;");
    expect(cookie).toContain("Expires=Thu, 01 Jan 1970 00:00:00 GMT");
    expect(cookie).toContain("HttpOnly");
    expect(cookie).toContain("SameSite=Lax");
    expect(cookie).toContain("Path=/");
  });

  it("should include Secure flag in production", () => {
    const originalEnv = process.env.ENVIRONMENT;
    process.env.ENVIRONMENT = "production";

    const cookie = clearSessionCookie();
    expect(cookie).toContain("Secure");

    process.env.ENVIRONMENT = originalEnv;
  });
});

describe("setOAuthStateCookie", () => {
  it("should create an OAuth state cookie string", () => {
    const cookie = setOAuthStateCookie("random-state");

    expect(cookie).toContain("oauth_state=random-state");
    expect(cookie).toContain("HttpOnly");
    expect(cookie).toContain("SameSite=Lax");
    expect(cookie).toContain("Max-Age=600"); // 10 minutes
    expect(cookie).toContain("Path=/");
  });

  it("should include Secure flag in production", () => {
    const originalEnv = process.env.ENVIRONMENT;
    process.env.ENVIRONMENT = "production";

    const cookie = setOAuthStateCookie("random-state");
    expect(cookie).toContain("Secure");

    process.env.ENVIRONMENT = originalEnv;
  });
});

describe("clearOAuthStateCookie", () => {
  it("should create an expired OAuth state cookie", () => {
    const cookie = clearOAuthStateCookie();

    expect(cookie).toContain("oauth_state=;");
    expect(cookie).toContain("Expires=Thu, 01 Jan 1970 00:00:00 GMT");
    expect(cookie).toContain("HttpOnly");
    expect(cookie).toContain("SameSite=Lax");
    expect(cookie).toContain("Path=/");
  });

  it("should include Secure flag in production", () => {
    const originalEnv = process.env.ENVIRONMENT;
    process.env.ENVIRONMENT = "production";

    const cookie = clearOAuthStateCookie();
    expect(cookie).toContain("Secure");

    process.env.ENVIRONMENT = originalEnv;
  });
});

describe("getAuthenticatedUser - path parameter validation", () => {
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

        const user = yield* getAuthenticatedUser(request, pathParams);

        expect(user).not.toBeNull();
        expect(user.id).toBe(owner.id);
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

      const result = yield* getAuthenticatedUser(request, pathParams).pipe(
        Effect.flip,
      );

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

        const user = yield* getAuthenticatedUser(request, pathParams);

        expect(user).not.toBeNull();
        expect(user.id).toBe(owner.id);
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

      const result = yield* getAuthenticatedUser(request, pathParams).pipe(
        Effect.flip,
      );

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

        const user = yield* getAuthenticatedUser(request, pathParams);

        expect(user).not.toBeNull();
        expect(user.id).toBe(owner.id);
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

      const result = yield* getAuthenticatedUser(request, pathParams).pipe(
        Effect.flip,
      );

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

        const user = yield* getAuthenticatedUser(request, pathParams);

        expect(user).not.toBeNull();
        expect(user.id).toBe(owner.id);
      }),
  );

  it.effect("should reject API key when any parameter mismatches", () =>
    Effect.gen(function* () {
      const { org, project, otherEnvironment, apiKey } =
        yield* TestAuthFixture;

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

      const result = yield* getAuthenticatedUser(request, pathParams).pipe(
        Effect.flip,
      );

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

        const user = yield* getAuthenticatedUser(request, undefined);

        expect(user).not.toBeNull();
        expect(user.id).toBe(owner.id);
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

      const user = yield* getAuthenticatedUser(request, pathParams);

      expect(user).not.toBeNull();
      expect(user.id).toBe(owner.id);
    }),
  );

  it.effect("should reject invalid API key", () =>
    Effect.gen(function* () {
      const request = new Request("https://example.com/api/test", {
        headers: {
          "X-API-Key": "mk_invalid_key_12345678901234567890123456789012",
        },
      });

      const result = yield* getAuthenticatedUser(request).pipe(Effect.flip);

      expect(result).toBeInstanceOf(UnauthorizedError);
      expect(result.message).toBe("Invalid API key");
    }),
  );

  it.effect("should reject request with no authentication", () =>
    Effect.gen(function* () {
      const request = new Request("https://example.com/api/test");

      const result = yield* getAuthenticatedUser(request).pipe(Effect.flip);

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

      const result = yield* getAuthenticatedUser(request).pipe(Effect.flip);

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

      const user = yield* getAuthenticatedUser(request);

      expect(user).not.toBeNull();
      expect(user.id).toBe(owner.id);
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

      const result = yield* getAuthenticatedUser(request);

      // Should return the API key owner, not the session user
      expect(result.id).toBe(owner.id);
    }),
  );
});
