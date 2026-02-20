import { describe, it, expect } from "@effect/vitest";
import { Effect, Either } from "effect";
import { afterEach, beforeEach, vi } from "vitest";

import {
  DedicatedWorkspaceProvisioningError,
  createAccount,
  deleteAccount,
  getAccount,
  listAccounts,
  suspendAccount,
} from "@/integrations/dedicated-workspace/provisioning";
import { MockSettingsLayer } from "@/tests/settings";

// Valid RSA private key in PKCS8 PEM format generated for unit tests only.
const TEST_PRIVATE_KEY = `-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCV0J6OqdZtDWtc
ZTHfey9xVwZn4Ja+3MSPtkM93MxqaQYutkNoLeY89K7DedQnYTcAv4I4Z4USjmxp
8IecJTvEzNwFWm2GWoJeVQHyMScDqymW/qNrJSumM1a+qutLKITK+IK8aTsVOwi2
0KpD1hjryIR7zAkNA7rW7WtwATRgd1V8EZrQ3DaNd1rBHtRnCyHGPxjjNYGCXDf9
BenTlFH+Sg/6uPTkHlzDEnfHU70NcXTRwz5XchGy8uqGG1J0h+bO1KD9XUFy6xP0
VBcqxeYDy6MIjrN2R0uoVGPJXyiJuHPukH35Kwh40UIcpo8t31XHjQujHZKx1I/C
Jy5yJq5vAgMBAAECggEAStybBqYGoKrGfb6Re9+V9vhqGolHOqudy0Rj+Gs3eGrv
rHLmXw4kkUwhckuUAHObJRQNcbsE659gvFV1pkiSw8Ysob4soajjoViwJsJ6AOLM
XwfySC2kUKIx1AgbmIxwQu6IgbbBz9uWgKfnlQtMm7Gwxh3QXgEBobm06JypfBQR
SFDpeLSOnvcAPmTKFT6J4oJuEYpTk8ysigfqYwSxdHMByFaKVgknaG4U+E/7DByW
vkIFHjrZHJ9VuQDLHcb7Jtyf5Y7/ep/046Sx8L7X7Q5dYbmxQ7vy9GcQXKSQ8mX9
W+1R8kEeH3JDbwS8J7nhpgbagsxQJhfRpEvJngYzRQKBgQDTXRPdmXrIuDdQlrYG
fmAjuttObcQNrrZ7lbQrr/JDMOqEoKI4Cpl1GqLzfN4pHv9rgTaMZqcc/chkvqYv
WponAORsVPxHdeJMHK24BBUTpzqiGIMRkwOLpuN1d+k++JAJSTwsLlMUZyQ5Mw+c
8VPRwR0lr8NoHDbZSRxUg7umZQKBgQC1dAtOtU+OdS0o30xLnMAvA8D/gJVcD8Zk
s4xyPzQZGqhk/I3XpXL+Cq2A7yjEgqlYB9kX09Cb4rGQqXCIKS7g3kok15phqJUL
LrV3SHxnCGqaNjcsiojOJeRyYyrA8An/fywl7QMH4JDH2R0ZU5Pzj5zKtuZPCluP
7PCmHOZ6QwKBgQDImfZYw2n9Rpl5KxDnaNnmD1pFPXhtY/xdnt+49ux/SNXLuok7
lxO+SOGPJlvTu0+/wIr9BhBlO5gNxcQD/YGAsyAYkTA+wmtcwXs+wuEeHgFQBuOe
smETEfmfa4c79Lz/kzpA1FaVbq66evO+iGx9D0OSmRZkoSKNZw40SDK44QKBgAf+
R6088Xc+FDIzvAGssw6fJLZcrLe0fjHbcvlpbVsZwIdKVNlGEY29XK1MW8hkVR9q
oRaanxru3pGX1Tw6TDVdtXhwAv4AVih680WA7PIA/ekzMDUHGUWzh5++XJjJOjeG
G6TEDxkevGIBX3XJJ8BX+Dk522Vp+GSbtHIs3b5PAoGBALjstbgj+PQF1re94WgY
wo6hiqgnepR96zOOduNsoRYMbdZquTLsRyRNr5tN4xA6xhI6akaFN6ONaZXFKeLm
Tw6zChcGe676iDDVMLUx1Hs+uEB020DW0jwT+PSoFGAqWy3endvslDzhz3OCn02d
AXkRlstVmZ+ojaI5zpG80Alt
-----END PRIVATE KEY-----`;

const validSaKeyJson = JSON.stringify({
  client_email: "sa@test.iam.gserviceaccount.com",
  private_key: TEST_PRIVATE_KEY,
  token_uri: "https://oauth2.googleapis.com/token",
});

const dedicatedWorkspaceSettings = MockSettingsLayer({
  dedicatedWorkspace: {
    saKeyJson: validSaKeyJson,
    adminEmail: "admin@example.com",
    domain: "example.com",
  },
});

const mockFetch = vi.fn();

/**
 * Helper: mock the first fetch call (token exchange) to succeed,
 * then let subsequent calls be handled by individual tests.
 */
function mockTokenExchange() {
  mockFetch.mockResolvedValueOnce(
    new Response(
      JSON.stringify({
        access_token: "ya29.test-token",
        expires_in: 3600,
      }),
    ),
  );
}

const mockUser = {
  id: "user-123",
  primaryEmail: "my-claw@example.com",
  name: { fullName: "my-claw Claw" },
  suspended: false,
  isAdmin: false,
  creationTime: "2026-01-01T00:00:00.000Z",
};

beforeEach(() => {
  mockFetch.mockClear();
  vi.stubGlobal("fetch", mockFetch);
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("Dedicated Workspace Provisioning", () => {
  describe("error classes", () => {
    it("DedicatedWorkspaceProvisioningError has correct tag", () => {
      const error = new DedicatedWorkspaceProvisioningError({
        message: "test",
      });
      expect(error._tag).toBe("DedicatedWorkspaceProvisioningError");
    });
  });

  describe("createAccount", () => {
    it.effect("creates account successfully", () =>
      Effect.gen(function* () {
        mockTokenExchange();
        mockFetch.mockResolvedValueOnce(
          new Response(JSON.stringify(mockUser), { status: 200 }),
        );

        const result = yield* createAccount("my-claw");
        expect(result.email).toBe("my-claw@example.com");
        expect(result.password).toBeTruthy();

        // Verify the create call was made to the right endpoint
        const createCall = mockFetch.mock.calls[1] as [string, RequestInit];
        expect(createCall[0]).toBe(
          "https://admin.googleapis.com/admin/directory/v1/users",
        );
        expect(createCall[1].method).toBe("POST");
        const body = JSON.parse(createCall[1].body as string) as {
          primaryEmail: string;
        };
        expect(body.primaryEmail).toBe("my-claw@example.com");
      }).pipe(Effect.provide(dedicatedWorkspaceSettings)),
    );

    it.effect("handles collision by appending suffix", () =>
      Effect.gen(function* () {
        mockTokenExchange();
        // First attempt returns 409 (conflict)
        mockFetch.mockResolvedValueOnce(
          new Response(
            JSON.stringify({
              error: { message: "Entity already exists.", code: 409 },
            }),
            { status: 409 },
          ),
        );
        // Second attempt succeeds
        const user2 = {
          ...mockUser,
          primaryEmail: "my-claw-2@example.com",
        };
        mockFetch.mockResolvedValueOnce(
          new Response(JSON.stringify(user2), { status: 200 }),
        );

        const result = yield* createAccount("my-claw");
        expect(result.email).toBe("my-claw-2@example.com");
      }).pipe(Effect.provide(dedicatedWorkspaceSettings)),
    );

    it.effect("returns error when all collision attempts are exhausted", () =>
      Effect.gen(function* () {
        mockTokenExchange();
        // All 10 attempts return 409
        for (let i = 0; i < 10; i++) {
          mockFetch.mockResolvedValueOnce(
            new Response(
              JSON.stringify({
                error: { message: "Entity already exists.", code: 409 },
              }),
              { status: 409 },
            ),
          );
        }

        const result = yield* createAccount("popular-slug").pipe(Effect.either);
        expect(Either.isLeft(result)).toBe(true);
        if (Either.isLeft(result)) {
          expect(result.left._tag).toBe("DedicatedWorkspaceProvisioningError");
          expect(result.left.message).toContain("variations");
        }
      }).pipe(Effect.provide(dedicatedWorkspaceSettings)),
    );

    it.effect("returns error when API returns non-409 error", () =>
      Effect.gen(function* () {
        mockTokenExchange();
        mockFetch.mockResolvedValueOnce(
          new Response(
            JSON.stringify({
              error: { message: "Quota exceeded", code: 403 },
            }),
            { status: 403 },
          ),
        );

        const result = yield* createAccount("my-claw").pipe(Effect.either);
        expect(Either.isLeft(result)).toBe(true);
        if (Either.isLeft(result)) {
          expect(result.left._tag).toBe("DedicatedWorkspaceProvisioningError");
          expect(result.left.message).toContain("Quota exceeded");
        }
      }).pipe(Effect.provide(dedicatedWorkspaceSettings)),
    );

    it.effect("returns error when fetch throws", () =>
      Effect.gen(function* () {
        mockTokenExchange();
        mockFetch.mockRejectedValueOnce(new Error("Network error"));

        const result = yield* createAccount("my-claw").pipe(Effect.either);
        expect(Either.isLeft(result)).toBe(true);
        if (Either.isLeft(result)) {
          expect(result.left._tag).toBe("DedicatedWorkspaceProvisioningError");
        }
      }).pipe(Effect.provide(dedicatedWorkspaceSettings)),
    );
  });

  describe("listAccounts", () => {
    it.effect("lists accounts successfully", () =>
      Effect.gen(function* () {
        mockTokenExchange();
        mockFetch.mockResolvedValueOnce(
          new Response(JSON.stringify({ users: [mockUser] })),
        );

        const result = yield* listAccounts();
        expect(result).toHaveLength(1);
        expect(result[0]!.primaryEmail).toBe("my-claw@example.com");

        // Verify domain query parameter
        const listCall = mockFetch.mock.calls[1] as [string, RequestInit];
        expect(listCall[0]).toContain("domain=example.com");
      }).pipe(Effect.provide(dedicatedWorkspaceSettings)),
    );

    it.effect("returns empty array when no users exist", () =>
      Effect.gen(function* () {
        mockTokenExchange();
        mockFetch.mockResolvedValueOnce(new Response(JSON.stringify({})));

        const result = yield* listAccounts();
        expect(result).toHaveLength(0);
      }).pipe(Effect.provide(dedicatedWorkspaceSettings)),
    );

    it.effect("returns error when API fails", () =>
      Effect.gen(function* () {
        mockTokenExchange();
        mockFetch.mockResolvedValueOnce(
          new Response(
            JSON.stringify({
              error: { message: "Forbidden", code: 403 },
            }),
          ),
        );

        const result = yield* listAccounts().pipe(Effect.either);
        expect(Either.isLeft(result)).toBe(true);
        if (Either.isLeft(result)) {
          expect(result.left._tag).toBe("DedicatedWorkspaceProvisioningError");
        }
      }).pipe(Effect.provide(dedicatedWorkspaceSettings)),
    );
  });

  describe("getAccount", () => {
    it.effect("gets account successfully", () =>
      Effect.gen(function* () {
        mockTokenExchange();
        mockFetch.mockResolvedValueOnce(new Response(JSON.stringify(mockUser)));

        const result = yield* getAccount("my-claw@example.com");
        expect(result.primaryEmail).toBe("my-claw@example.com");

        const getCall = mockFetch.mock.calls[1] as [string, RequestInit];
        expect(getCall[0]).toContain("my-claw%40example.com");
        expect(getCall[1].method).toBe("GET");
      }).pipe(Effect.provide(dedicatedWorkspaceSettings)),
    );

    it.effect("returns error when user not found", () =>
      Effect.gen(function* () {
        mockTokenExchange();
        mockFetch.mockResolvedValueOnce(
          new Response(
            JSON.stringify({
              error: { message: "Resource Not Found: userKey", code: 404 },
            }),
          ),
        );

        const result = yield* getAccount("missing@example.com").pipe(
          Effect.either,
        );
        expect(Either.isLeft(result)).toBe(true);
        if (Either.isLeft(result)) {
          expect(result.left._tag).toBe("DedicatedWorkspaceProvisioningError");
          expect(result.left.message).toContain("Resource Not Found");
        }
      }).pipe(Effect.provide(dedicatedWorkspaceSettings)),
    );
  });

  describe("suspendAccount", () => {
    it.effect("suspends account successfully", () =>
      Effect.gen(function* () {
        mockTokenExchange();
        const suspendedUser = { ...mockUser, suspended: true };
        mockFetch.mockResolvedValueOnce(
          new Response(JSON.stringify(suspendedUser)),
        );

        const result = yield* suspendAccount("my-claw@example.com");
        expect(result.suspended).toBe(true);

        const putCall = mockFetch.mock.calls[1] as [string, RequestInit];
        expect(putCall[1].method).toBe("PUT");
        const body = JSON.parse(putCall[1].body as string) as {
          suspended: boolean;
        };
        expect(body.suspended).toBe(true);
      }).pipe(Effect.provide(dedicatedWorkspaceSettings)),
    );

    it.effect("returns error when suspend fails", () =>
      Effect.gen(function* () {
        mockTokenExchange();
        mockFetch.mockResolvedValueOnce(
          new Response(
            JSON.stringify({
              error: { message: "Forbidden", code: 403 },
            }),
          ),
        );

        const result = yield* suspendAccount("my-claw@example.com").pipe(
          Effect.either,
        );
        expect(Either.isLeft(result)).toBe(true);
        if (Either.isLeft(result)) {
          expect(result.left._tag).toBe("DedicatedWorkspaceProvisioningError");
        }
      }).pipe(Effect.provide(dedicatedWorkspaceSettings)),
    );
  });

  describe("deleteAccount", () => {
    it.effect("deletes account successfully", () =>
      Effect.gen(function* () {
        mockTokenExchange();
        mockFetch.mockResolvedValueOnce(new Response(null, { status: 204 }));

        yield* deleteAccount("my-claw@example.com");

        const deleteCall = mockFetch.mock.calls[1] as [string, RequestInit];
        expect(deleteCall[0]).toContain("my-claw%40example.com");
        expect(deleteCall[1].method).toBe("DELETE");
      }).pipe(Effect.provide(dedicatedWorkspaceSettings)),
    );

    it.effect("returns error when delete fails", () =>
      Effect.gen(function* () {
        mockTokenExchange();
        mockFetch.mockResolvedValueOnce(
          new Response(
            JSON.stringify({
              error: { message: "Resource Not Found: userKey", code: 404 },
            }),
          ),
        );

        const result = yield* deleteAccount("missing@example.com").pipe(
          Effect.either,
        );
        expect(Either.isLeft(result)).toBe(true);
        if (Either.isLeft(result)) {
          expect(result.left._tag).toBe("DedicatedWorkspaceProvisioningError");
        }
      }).pipe(Effect.provide(dedicatedWorkspaceSettings)),
    );

    it.effect("returns error when fetch throws during delete", () =>
      Effect.gen(function* () {
        mockTokenExchange();
        mockFetch.mockRejectedValueOnce(new Error("Network error"));

        const result = yield* deleteAccount("my-claw@example.com").pipe(
          Effect.either,
        );
        expect(Either.isLeft(result)).toBe(true);
        if (Either.isLeft(result)) {
          expect(result.left._tag).toBe("DedicatedWorkspaceProvisioningError");
        }
      }).pipe(Effect.provide(dedicatedWorkspaceSettings)),
    );
  });
});
