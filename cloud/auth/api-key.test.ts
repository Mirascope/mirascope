import { describe, it, expect } from "vitest";
import { Effect, Layer } from "effect";
import {
  getApiKeyFromRequest,
  authenticateWithApiKey,
  authenticateApiKeyWithUser,
  API_KEY_HEADER,
} from "@/auth/api-key";
import { DatabaseService, type Database } from "@/db";
import { NotFoundError } from "@/db/errors";
import { withTestDatabase } from "@/tests/db";

// Helper to run an effect with DatabaseService provided
const runWithDb = <A, E>(
  db: Database,
  effect: Effect.Effect<A, E, DatabaseService>,
) =>
  Effect.runPromise(
    effect.pipe(Effect.provide(Layer.succeed(DatabaseService, db))),
  );

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

describe("authenticateWithApiKey", () => {
  it(
    "should return null if no API key provided",
    withTestDatabase((db) =>
      Effect.gen(function* () {
        const request = new Request("http://localhost/api");

        const result = yield* Effect.promise(() =>
          runWithDb(db, authenticateWithApiKey(request)),
        );

        expect(result).toBeNull();
      }),
    ),
  );

  it(
    "should verify API key and return info",
    withTestDatabase((db) =>
      Effect.gen(function* () {
        const user = yield* db.users.create({
          email: "test@example.com",
          name: "Test User",
        });

        const org = yield* db.organizations.create(
          { name: "Test Org" },
          user.id,
        );

        const project = yield* db.projects.create(
          { name: "Test Project", organizationId: org.id },
          user.id,
        );

        const envs = yield* db.environments.findByProject(project.id, user.id);
        const devEnv = envs.find((e) => e.name === "development")!;

        const created = yield* db.apiKeys.create(
          { name: "test-key", environmentId: devEnv.id },
          user.id,
        );

        const request = new Request("http://localhost/api", {
          headers: { [API_KEY_HEADER]: created.key },
        });

        const result = yield* Effect.promise(() =>
          runWithDb(db, authenticateWithApiKey(request)),
        );

        expect(result).not.toBeNull();
        expect(result?.apiKeyId).toBe(created.id);
        expect(result?.environmentId).toBe(devEnv.id);
      }),
    ),
  );

  it(
    "should fail with NotFoundError for invalid API key",
    withTestDatabase((db) =>
      Effect.gen(function* () {
        const request = new Request("http://localhost/api", {
          headers: { [API_KEY_HEADER]: "mk_invalid_key" },
        });

        const result = yield* Effect.promise(() =>
          runWithDb(db, Effect.either(authenticateWithApiKey(request))),
        );

        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(NotFoundError);
        }
      }),
    ),
  );
});

describe("authenticateApiKeyWithUser", () => {
  it(
    "should return null if no API key provided",
    withTestDatabase((db) =>
      Effect.gen(function* () {
        const request = new Request("http://localhost/api");

        const result = yield* Effect.promise(() =>
          runWithDb(db, authenticateApiKeyWithUser(request)),
        );

        expect(result).toBeNull();
      }),
    ),
  );

  it(
    "should authenticate and return user for valid API key",
    withTestDatabase((db) =>
      Effect.gen(function* () {
        const user = yield* db.users.create({
          email: "test@example.com",
          name: "Test User",
        });

        const org = yield* db.organizations.create(
          { name: "Test Org" },
          user.id,
        );

        const project = yield* db.projects.create(
          { name: "Test Project", organizationId: org.id },
          user.id,
        );

        const envs = yield* db.environments.findByProject(project.id, user.id);
        const devEnv = envs.find((e) => e.name === "development")!;

        const created = yield* db.apiKeys.create(
          { name: "test-key", environmentId: devEnv.id },
          user.id,
        );

        const request = new Request("http://localhost/api", {
          headers: { [API_KEY_HEADER]: created.key },
        });

        const result = yield* Effect.promise(() =>
          runWithDb(db, authenticateApiKeyWithUser(request)),
        );

        expect(result).not.toBeNull();
        expect(result?.apiKeyInfo.apiKeyId).toBe(created.id);
        expect(result?.apiKeyInfo.environmentId).toBe(devEnv.id);
        expect(result?.user.id).toBe(user.id);
        expect(result?.user.email).toBe("test@example.com");
      }),
    ),
  );

  it(
    "should fail for invalid API key",
    withTestDatabase((db) =>
      Effect.gen(function* () {
        const request = new Request("http://localhost/api", {
          headers: { [API_KEY_HEADER]: "mk_invalid_key" },
        });

        const result = yield* Effect.promise(() =>
          runWithDb(db, Effect.either(authenticateApiKeyWithUser(request))),
        );

        expect(result._tag).toBe("Left");
        if (result._tag === "Left") {
          expect(result.left).toBeInstanceOf(NotFoundError);
        }
      }),
    ),
  );
});
