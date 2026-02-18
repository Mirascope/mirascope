import { eq } from "drizzle-orm";
import { Effect, Either } from "effect";
import { afterEach, beforeEach, vi } from "vitest";

import {
  callbackOAuthEffect,
  revokeConnectionEffect,
  startOAuthEffect,
} from "@/app/api/google-workspace-connections.handlers";
import { encryptSecrets } from "@/claws/crypto";
import { DrizzleORM } from "@/db/client";
import { googleWorkspaceConnections, sessions } from "@/db/schema";
import { signState } from "@/integrations/google-workspace/hmac";
import { describe, expect, it, TestClawFixture } from "@/tests/db";

// Mock global fetch for Google API calls
const mockFetch = vi.fn();

beforeEach(() => {
  vi.stubGlobal("fetch", mockFetch);
});

afterEach(() => {
  vi.restoreAllMocks();
});

function buildRequest(
  url: string,
  options?: { sessionId?: string; body?: unknown; method?: string },
): Request {
  const headers: Record<string, string> = {};
  if (options?.sessionId) {
    headers["Cookie"] = `session=${options.sessionId}`;
  }
  if (options?.body) {
    headers["Content-Type"] = "application/json";
  }
  return new Request(url, {
    method: options?.method || "GET",
    headers,
    ...(options?.body ? { body: JSON.stringify(options.body) } : {}),
  });
}

describe("startOAuthEffect", () => {
  it.effect("rejects unauthenticated requests", () =>
    Effect.gen(function* () {
      const { claw } = yield* TestClawFixture;
      const request = buildRequest(
        `http://localhost:3000/api/google-workspace-connections/start?claw_id=${claw.id}`,
      );
      const result = yield* startOAuthEffect(request).pipe(Effect.either);
      expect(Either.isLeft(result)).toBe(true);
    }),
  );

  it.effect("rejects non-member users", () =>
    Effect.gen(function* () {
      const { claw, nonMember } = yield* TestClawFixture;
      const client = yield* DrizzleORM;

      // Create session for non-member
      const [session] = yield* client
        .insert(sessions)
        .values({
          userId: nonMember.id,
          expiresAt: new Date(Date.now() + 86400000),
        })
        .returning();

      const request = buildRequest(
        `http://localhost:3000/api/google-workspace-connections/start?claw_id=${claw.id}`,
        { sessionId: session.id },
      );
      const result = yield* startOAuthEffect(request).pipe(Effect.either);
      expect(Either.isLeft(result)).toBe(true);
      if (Either.isLeft(result)) {
        expect(result.left.message).toContain("Not authorized");
      }
    }),
  );

  it.effect("rejects when claw_id is missing", () =>
    Effect.gen(function* () {
      const { owner } = yield* TestClawFixture;
      const client = yield* DrizzleORM;

      const [session] = yield* client
        .insert(sessions)
        .values({
          userId: owner.id,
          expiresAt: new Date(Date.now() + 86400000),
        })
        .returning();

      const request = buildRequest(
        "http://localhost:3000/api/google-workspace-connections/start",
        { sessionId: session.id },
      );
      const result = yield* startOAuthEffect(request).pipe(Effect.either);
      expect(Either.isLeft(result)).toBe(true);
      if (Either.isLeft(result)) {
        expect(result.left.message).toContain("Missing claw_id");
      }
    }),
  );

  it.effect("rejects when claw does not exist", () =>
    Effect.gen(function* () {
      const { owner } = yield* TestClawFixture;
      const client = yield* DrizzleORM;

      const [session] = yield* client
        .insert(sessions)
        .values({
          userId: owner.id,
          expiresAt: new Date(Date.now() + 86400000),
        })
        .returning();

      const request = buildRequest(
        `http://localhost:3000/api/google-workspace-connections/start?claw_id=00000000-0000-0000-0000-000000000000`,
        { sessionId: session.id },
      );
      const result = yield* startOAuthEffect(request).pipe(Effect.either);
      expect(Either.isLeft(result)).toBe(true);
      if (Either.isLeft(result)) {
        expect(result.left.message).toBe("Claw not found");
      }
    }),
  );

  it.effect("redirects to Google OAuth for authorized users", () =>
    Effect.gen(function* () {
      const { claw, owner } = yield* TestClawFixture;
      const client = yield* DrizzleORM;

      const [session] = yield* client
        .insert(sessions)
        .values({
          userId: owner.id,
          expiresAt: new Date(Date.now() + 86400000),
        })
        .returning();

      const request = buildRequest(
        `http://localhost:3000/api/google-workspace-connections/start?claw_id=${claw.id}`,
        { sessionId: session.id },
      );
      const response = yield* startOAuthEffect(request);

      expect(response.status).toBe(302);
      const location = response.headers.get("Location");
      expect(location).toBeDefined();
      expect(location).toContain("accounts.google.com");
      expect(location).toContain("state=");

      // Verify state cookie is set
      const setCookie = response.headers.get("Set-Cookie");
      expect(setCookie).toContain("gw_oauth_state=");
    }),
  );

  it.effect("includes HMAC signature in state", () =>
    Effect.gen(function* () {
      const { claw, owner } = yield* TestClawFixture;
      const client = yield* DrizzleORM;

      const [session] = yield* client
        .insert(sessions)
        .values({
          userId: owner.id,
          expiresAt: new Date(Date.now() + 86400000),
        })
        .returning();

      const request = buildRequest(
        `http://localhost:3000/api/google-workspace-connections/start?claw_id=${claw.id}`,
        { sessionId: session.id },
      );
      const response = yield* startOAuthEffect(request);

      const location = response.headers.get("Location")!;
      const locationUrl = new URL(location);
      const stateParam = locationUrl.searchParams.get("state")!;
      const decoded = JSON.parse(atob(stateParam)) as Record<string, unknown>;
      expect(decoded.hmac).toBeDefined();
      expect(decoded.clawId).toBe(claw.id);
      expect(decoded.userId).toBe(owner.id);
    }),
  );
});

describe("callbackOAuthEffect", () => {
  it.effect("rejects state with invalid HMAC", () =>
    Effect.gen(function* () {
      const forgedState = btoa(
        JSON.stringify({
          randomState: "forged",
          clawId: "claw-1",
          organizationId: "org-1",
          userId: "user-1",
          hmac: btoa("forged-hmac"),
        }),
      );
      const request = buildRequest(
        `http://localhost:3000/api/google-workspace-connections/callback?code=test-code&state=${forgedState}`,
        { sessionId: "some-session" },
      );
      // Set the CSRF cookie to match
      const headers = new Headers(request.headers);
      headers.set("Cookie", "gw_oauth_state=forged; session=some-session");
      const requestWithCookie = new Request(request.url, {
        headers,
      });

      const result = yield* callbackOAuthEffect(requestWithCookie).pipe(
        Effect.either,
      );
      expect(Either.isLeft(result)).toBe(true);
    }),
  );

  it.effect("rejects when session user does not match state", () =>
    Effect.gen(function* () {
      const { claw, owner, member } = yield* TestClawFixture;
      const client = yield* DrizzleORM;

      // Create session for member (different from owner in state)
      const [session] = yield* client
        .insert(sessions)
        .values({
          userId: member.id,
          expiresAt: new Date(Date.now() + 86400000),
        })
        .returning();

      // Create valid HMAC-signed state with owner's userId
      const randomState = "test-csrf-state";
      const encodedState = yield* signState({
        randomState,
        clawId: claw.id,
        organizationId: claw.organizationId,
        userId: owner.id, // State says owner
      });

      const request = new Request(
        `http://localhost:3000/api/google-workspace-connections/callback?code=test-code&state=${encodedState}`,
        {
          headers: {
            Cookie: `gw_oauth_state=${randomState}; session=${session.id}`,
          },
        },
      );

      const result = yield* callbackOAuthEffect(request).pipe(Effect.either);
      expect(Either.isLeft(result)).toBe(true);
      if (Either.isLeft(result)) {
        expect(result.left.message).toContain("Session user does not match");
      }
    }),
  );

  it.effect("rejects when CSRF cookie does not match state", () =>
    Effect.gen(function* () {
      const { claw, owner } = yield* TestClawFixture;
      const client = yield* DrizzleORM;

      const [session] = yield* client
        .insert(sessions)
        .values({
          userId: owner.id,
          expiresAt: new Date(Date.now() + 86400000),
        })
        .returning();

      const encodedState = yield* signState({
        randomState: "correct-csrf",
        clawId: claw.id,
        organizationId: claw.organizationId,
        userId: owner.id,
      });

      const request = new Request(
        `http://localhost:3000/api/google-workspace-connections/callback?code=test-code&state=${encodedState}`,
        {
          headers: {
            Cookie: `gw_oauth_state=wrong-csrf; session=${session.id}`,
          },
        },
      );

      const result = yield* callbackOAuthEffect(request).pipe(Effect.either);
      expect(Either.isLeft(result)).toBe(true);
      if (Either.isLeft(result)) {
        expect(result.left.message).toBe("Invalid state parameter");
      }
    }),
  );

  it.effect("creates connection and redirects on success", () =>
    Effect.gen(function* () {
      const { claw, owner, org } = yield* TestClawFixture;
      const client = yield* DrizzleORM;

      const [session] = yield* client
        .insert(sessions)
        .values({
          userId: owner.id,
          expiresAt: new Date(Date.now() + 86400000),
        })
        .returning();

      const randomState = "test-csrf";
      const encodedState = yield* signState({
        randomState,
        clawId: claw.id,
        organizationId: org.id,
        userId: owner.id,
      });

      // Mock Google token exchange
      mockFetch.mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            access_token: "test-access-token",
            refresh_token: "test-refresh-token",
            expires_in: 3600,
            scope: "gmail.send calendar",
          }),
        ),
      );

      // Mock Google userinfo
      mockFetch.mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            email: "user@example.com",
            name: "Test User",
          }),
        ),
      );

      const request = new Request(
        `http://localhost:3000/api/google-workspace-connections/callback?code=test-auth-code&state=${encodedState}`,
        {
          headers: {
            Cookie: `gw_oauth_state=${randomState}; session=${session.id}`,
          },
        },
      );

      const response = yield* callbackOAuthEffect(request);
      expect(response.status).toBe(302);

      const location = response.headers.get("Location")!;
      expect(location).toContain("/claws/");
      expect(location).toContain("status=connected");

      // Verify connection was created
      const [connection] = yield* client
        .select()
        .from(googleWorkspaceConnections)
        .where(eq(googleWorkspaceConnections.clawId, claw.id))
        .limit(1);
      expect(connection).toBeDefined();
      expect(connection.connectedEmail).toBe("user@example.com");
      expect(connection.userId).toBe(owner.id);
    }),
  );

  it.effect("rejects when Google returns error parameter", () =>
    Effect.gen(function* () {
      const request = buildRequest(
        "http://localhost:3000/api/google-workspace-connections/callback?error=access_denied",
      );
      const result = yield* callbackOAuthEffect(request).pipe(Effect.either);
      expect(Either.isLeft(result)).toBe(true);
      if (Either.isLeft(result)) {
        expect(result.left.message).toContain("access_denied");
      }
    }),
  );
});

describe("revokeConnectionEffect", () => {
  it.effect("returns 401 for unauthenticated requests", () =>
    Effect.gen(function* () {
      const request = buildRequest(
        "http://localhost:3000/api/google-workspace-connections/revoke",
        { method: "POST", body: { claw_id: "test" } },
      );
      const response = yield* revokeConnectionEffect(request);
      expect(response.status).toBe(401);
    }),
  );

  it.effect("returns 404 when claw not found", () =>
    Effect.gen(function* () {
      const { owner } = yield* TestClawFixture;
      const client = yield* DrizzleORM;

      const [session] = yield* client
        .insert(sessions)
        .values({
          userId: owner.id,
          expiresAt: new Date(Date.now() + 86400000),
        })
        .returning();

      const request = new Request(
        "http://localhost:3000/api/google-workspace-connections/revoke",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Cookie: `session=${session.id}`,
          },
          body: JSON.stringify({
            claw_id: "00000000-0000-0000-0000-000000000000",
          }),
        },
      );
      const response = yield* revokeConnectionEffect(request);
      expect(response.status).toBe(404);
      const body = (yield* Effect.promise(() => response.json())) as {
        error: string;
      };
      expect(body.error).toBe("Claw not found");
    }),
  );

  it.effect("returns 403 for non-member users", () =>
    Effect.gen(function* () {
      const { claw, nonMember } = yield* TestClawFixture;
      const client = yield* DrizzleORM;

      const [session] = yield* client
        .insert(sessions)
        .values({
          userId: nonMember.id,
          expiresAt: new Date(Date.now() + 86400000),
        })
        .returning();

      const request = new Request(
        "http://localhost:3000/api/google-workspace-connections/revoke",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Cookie: `session=${session.id}`,
          },
          body: JSON.stringify({ claw_id: claw.id }),
        },
      );
      const response = yield* revokeConnectionEffect(request);
      expect(response.status).toBe(403);
    }),
  );

  it.effect("returns 404 when no connection exists", () =>
    Effect.gen(function* () {
      const { claw, owner } = yield* TestClawFixture;
      const client = yield* DrizzleORM;

      const [session] = yield* client
        .insert(sessions)
        .values({
          userId: owner.id,
          expiresAt: new Date(Date.now() + 86400000),
        })
        .returning();

      const request = new Request(
        "http://localhost:3000/api/google-workspace-connections/revoke",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Cookie: `session=${session.id}`,
          },
          body: JSON.stringify({ claw_id: claw.id }),
        },
      );
      const response = yield* revokeConnectionEffect(request);
      expect(response.status).toBe(404);
      const body = (yield* Effect.promise(() => response.json())) as {
        error: string;
      };
      expect(body.error).toContain("No Google Workspace connection");
    }),
  );

  it.effect("successfully revokes and returns 200", () =>
    Effect.gen(function* () {
      const { claw, owner } = yield* TestClawFixture;
      const client = yield* DrizzleORM;

      const [session] = yield* client
        .insert(sessions)
        .values({
          userId: owner.id,
          expiresAt: new Date(Date.now() + 86400000),
        })
        .returning();

      // Create a connection with encrypted token
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

      // Mock Google revoke endpoint
      mockFetch.mockResolvedValueOnce(new Response(null, { status: 200 }));

      const request = new Request(
        "http://localhost:3000/api/google-workspace-connections/revoke",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Cookie: `session=${session.id}`,
          },
          body: JSON.stringify({ claw_id: claw.id }),
        },
      );
      const response = yield* revokeConnectionEffect(request);
      expect(response.status).toBe(200);

      // Verify connection was deleted
      const [remaining] = yield* client
        .select()
        .from(googleWorkspaceConnections)
        .where(eq(googleWorkspaceConnections.clawId, claw.id))
        .limit(1);
      expect(remaining).toBeUndefined();
    }),
  );
});
