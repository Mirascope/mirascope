import { describe, it, expect, TestEffectAuthFixture } from "@/tests/auth";
import { Effect } from "effect";
import { getAuthenticatedUser, type PathParameters } from "@/auth/utils";
import { UnauthorizedError } from "@/errors";

describe("getAuthenticatedUser - path parameter validation", () => {
  it.effect(
    "should authenticate with valid API key and matching environmentId",
    () =>
      Effect.gen(function* () {
        const { testUser, testEnvironment, testApiKey } =
          yield* TestEffectAuthFixture;

        const request = new Request("https://example.com/api/test", {
          headers: {
            "X-API-Key": testApiKey,
          },
        });

        const pathParams: PathParameters = {
          environmentId: testEnvironment.id,
        };

        const user = yield* getAuthenticatedUser(request, pathParams);

        expect(user).not.toBeNull();
        expect(user?.id).toBe(testUser.id);
      }),
  );

  it.effect("should reject API key with mismatched environmentId", () =>
    Effect.gen(function* () {
      const { otherEnvironment, testApiKey } = yield* TestEffectAuthFixture;

      const request = new Request("https://example.com/api/test", {
        headers: {
          "X-API-Key": testApiKey,
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
        const { testUser, testProject, testApiKey } =
          yield* TestEffectAuthFixture;

        const request = new Request("https://example.com/api/test", {
          headers: {
            "X-API-Key": testApiKey,
          },
        });

        const pathParams: PathParameters = {
          projectId: testProject.id,
        };

        const user = yield* getAuthenticatedUser(request, pathParams);

        expect(user).not.toBeNull();
        expect(user?.id).toBe(testUser.id);
      }),
  );

  it.effect("should reject API key with mismatched projectId", () =>
    Effect.gen(function* () {
      const { testApiKey } = yield* TestEffectAuthFixture;

      const request = new Request("https://example.com/api/test", {
        headers: {
          "X-API-Key": testApiKey,
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
        const { testUser, testOrg, testApiKey } = yield* TestEffectAuthFixture;

        const request = new Request("https://example.com/api/test", {
          headers: {
            "X-API-Key": testApiKey,
          },
        });

        const pathParams: PathParameters = {
          organizationId: testOrg.id,
        };

        const user = yield* getAuthenticatedUser(request, pathParams);

        expect(user).not.toBeNull();
        expect(user?.id).toBe(testUser.id);
      }),
  );

  it.effect("should reject API key with mismatched organizationId", () =>
    Effect.gen(function* () {
      const { testApiKey } = yield* TestEffectAuthFixture;

      const request = new Request("https://example.com/api/test", {
        headers: {
          "X-API-Key": testApiKey,
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
        const { testUser, testOrg, testProject, testEnvironment, testApiKey } =
          yield* TestEffectAuthFixture;

        const request = new Request("https://example.com/api/test", {
          headers: {
            "X-API-Key": testApiKey,
          },
        });

        const pathParams: PathParameters = {
          organizationId: testOrg.id,
          projectId: testProject.id,
          environmentId: testEnvironment.id,
        };

        const user = yield* getAuthenticatedUser(request, pathParams);

        expect(user).not.toBeNull();
        expect(user?.id).toBe(testUser.id);
      }),
  );

  it.effect("should reject API key when any parameter mismatches", () =>
    Effect.gen(function* () {
      const { testOrg, testProject, otherEnvironment, testApiKey } =
        yield* TestEffectAuthFixture;

      const request = new Request("https://example.com/api/test", {
        headers: {
          "X-API-Key": testApiKey,
        },
      });

      // Correct org and project, but wrong environment
      const pathParams: PathParameters = {
        organizationId: testOrg.id,
        projectId: testProject.id,
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
        const { testUser, testApiKey } = yield* TestEffectAuthFixture;

        const request = new Request("https://example.com/api/test", {
          headers: {
            "X-API-Key": testApiKey,
          },
        });

        const user = yield* getAuthenticatedUser(request, undefined);

        expect(user).not.toBeNull();
        expect(user?.id).toBe(testUser.id);
      }),
  );

  it.effect("should authenticate with Authorization Bearer header", () =>
    Effect.gen(function* () {
      const { testUser, testEnvironment, testApiKey } =
        yield* TestEffectAuthFixture;

      const request = new Request("https://example.com/api/test", {
        headers: {
          Authorization: `Bearer ${testApiKey}`,
        },
      });

      const pathParams: PathParameters = {
        environmentId: testEnvironment.id,
      };

      const user = yield* getAuthenticatedUser(request, pathParams);

      expect(user).not.toBeNull();
      expect(user?.id).toBe(testUser.id);
    }),
  );
});
