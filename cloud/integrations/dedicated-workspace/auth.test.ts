import { describe, it, expect } from "@effect/vitest";
import { Effect, Either } from "effect";
import { afterEach, beforeEach, vi } from "vitest";

import {
  DedicatedWorkspaceAuthError,
  MissingConfigError,
  getAccessToken,
} from "@/integrations/dedicated-workspace/auth";
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

const mockFetch = vi.fn();

beforeEach(() => {
  mockFetch.mockClear();
  vi.stubGlobal("fetch", mockFetch);
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("Dedicated Workspace Auth", () => {
  describe("error classes", () => {
    it("DedicatedWorkspaceAuthError has correct tag", () => {
      const error = new DedicatedWorkspaceAuthError({ message: "test" });
      expect(error._tag).toBe("DedicatedWorkspaceAuthError");
    });

    it("MissingConfigError has correct tag", () => {
      const error = new MissingConfigError({ message: "test" });
      expect(error._tag).toBe("MissingConfigError");
    });
  });

  describe("getAccessToken", () => {
    it.effect("returns MissingConfigError when saKeyJson is not set", () =>
      Effect.gen(function* () {
        const result = yield* getAccessToken().pipe(Effect.either);
        expect(Either.isLeft(result)).toBe(true);
        if (Either.isLeft(result)) {
          expect(result.left._tag).toBe("MissingConfigError");
          expect(result.left.message).toContain(
            "DEDICATED_WORKSPACE_SA_KEY_JSON",
          );
        }
      }).pipe(
        Effect.provide(
          MockSettingsLayer({
            dedicatedWorkspace: {
              saKeyJson: undefined,
              adminEmail: "admin@example.com",
              domain: "example.com",
            },
          }),
        ),
      ),
    );

    it.effect("returns MissingConfigError when adminEmail is not set", () =>
      Effect.gen(function* () {
        const result = yield* getAccessToken().pipe(Effect.either);
        expect(Either.isLeft(result)).toBe(true);
        if (Either.isLeft(result)) {
          expect(result.left._tag).toBe("MissingConfigError");
          expect(result.left.message).toContain(
            "DEDICATED_WORKSPACE_ADMIN_EMAIL",
          );
        }
      }).pipe(
        Effect.provide(
          MockSettingsLayer({
            dedicatedWorkspace: {
              saKeyJson: validSaKeyJson,
              adminEmail: undefined,
              domain: "example.com",
            },
          }),
        ),
      ),
    );

    it.effect("returns MissingConfigError when domain is not set", () =>
      Effect.gen(function* () {
        const result = yield* getAccessToken().pipe(Effect.either);
        expect(Either.isLeft(result)).toBe(true);
        if (Either.isLeft(result)) {
          expect(result.left._tag).toBe("MissingConfigError");
          expect(result.left.message).toContain("DEDICATED_WORKSPACE_DOMAIN");
        }
      }).pipe(
        Effect.provide(
          MockSettingsLayer({
            dedicatedWorkspace: {
              saKeyJson: validSaKeyJson,
              adminEmail: "admin@example.com",
              domain: undefined,
            },
          }),
        ),
      ),
    );

    it.effect(
      "returns MissingConfigError listing all missing fields when none are set",
      () =>
        Effect.gen(function* () {
          const result = yield* getAccessToken().pipe(Effect.either);
          expect(Either.isLeft(result)).toBe(true);
          if (Either.isLeft(result)) {
            expect(result.left._tag).toBe("MissingConfigError");
            expect(result.left.message).toContain(
              "DEDICATED_WORKSPACE_SA_KEY_JSON",
            );
            expect(result.left.message).toContain(
              "DEDICATED_WORKSPACE_ADMIN_EMAIL",
            );
            expect(result.left.message).toContain("DEDICATED_WORKSPACE_DOMAIN");
          }
        }).pipe(
          Effect.provide(
            MockSettingsLayer({
              dedicatedWorkspace: {
                saKeyJson: undefined,
                adminEmail: undefined,
                domain: undefined,
              },
            }),
          ),
        ),
    );

    it.effect(
      "returns DedicatedWorkspaceAuthError when saKeyJson is invalid JSON",
      () =>
        Effect.gen(function* () {
          const result = yield* getAccessToken().pipe(Effect.either);
          expect(Either.isLeft(result)).toBe(true);
          if (Either.isLeft(result)) {
            expect(result.left._tag).toBe("DedicatedWorkspaceAuthError");
            expect(result.left.message).toContain("Failed to parse");
          }
        }).pipe(
          Effect.provide(
            MockSettingsLayer({
              dedicatedWorkspace: {
                saKeyJson: "not-valid-json{{{",
                adminEmail: "admin@example.com",
                domain: "example.com",
              },
            }),
          ),
        ),
    );

    it.effect(
      "returns DedicatedWorkspaceAuthError when saKeyJson is missing required fields",
      () =>
        Effect.gen(function* () {
          const result = yield* getAccessToken().pipe(Effect.either);
          expect(Either.isLeft(result)).toBe(true);
          if (Either.isLeft(result)) {
            expect(result.left._tag).toBe("DedicatedWorkspaceAuthError");
            expect(result.left.message).toContain("missing required fields");
          }
        }).pipe(
          Effect.provide(
            MockSettingsLayer({
              dedicatedWorkspace: {
                saKeyJson: JSON.stringify({ client_email: "test@test.com" }),
                adminEmail: "admin@example.com",
                domain: "example.com",
              },
            }),
          ),
        ),
    );

    it.effect("returns access token on successful exchange", () =>
      Effect.gen(function* () {
        mockFetch.mockResolvedValueOnce(
          new Response(
            JSON.stringify({
              access_token: "ya29.test-access-token",
              expires_in: 3600,
            }),
          ),
        );

        const result = yield* getAccessToken();
        expect(result.accessToken).toBe("ya29.test-access-token");
        expect(result.expiresIn).toBe(3600);

        // Verify fetch was called with correct endpoint and grant type
        expect(mockFetch).toHaveBeenCalledWith(
          "https://oauth2.googleapis.com/token",
          expect.objectContaining({ method: "POST" }),
        );

        const callArgs = mockFetch.mock.calls[0] as [string, RequestInit];
        const body = callArgs[1].body as URLSearchParams;
        expect(body.get("grant_type")).toBe(
          "urn:ietf:params:oauth:grant-type:jwt-bearer",
        );
        expect(body.get("assertion")).toBeTruthy();
      }).pipe(
        Effect.provide(
          MockSettingsLayer({
            dedicatedWorkspace: {
              saKeyJson: validSaKeyJson,
              adminEmail: "admin@example.com",
              domain: "example.com",
            },
          }),
        ),
      ),
    );

    it.effect("defaults expiresIn to 3600 when not provided", () =>
      Effect.gen(function* () {
        mockFetch.mockResolvedValueOnce(
          new Response(
            JSON.stringify({
              access_token: "ya29.test-access-token",
            }),
          ),
        );

        const result = yield* getAccessToken();
        expect(result.expiresIn).toBe(3600);
      }).pipe(
        Effect.provide(
          MockSettingsLayer({
            dedicatedWorkspace: {
              saKeyJson: validSaKeyJson,
              adminEmail: "admin@example.com",
              domain: "example.com",
            },
          }),
        ),
      ),
    );

    it.effect(
      "returns DedicatedWorkspaceAuthError when token exchange returns error",
      () =>
        Effect.gen(function* () {
          mockFetch.mockResolvedValueOnce(
            new Response(
              JSON.stringify({
                error: "invalid_grant",
                error_description: "Service account not authorized",
              }),
            ),
          );

          const result = yield* getAccessToken().pipe(Effect.either);
          expect(Either.isLeft(result)).toBe(true);
          if (Either.isLeft(result)) {
            expect(result.left._tag).toBe("DedicatedWorkspaceAuthError");
            expect(result.left.message).toContain(
              "Service account not authorized",
            );
          }
        }).pipe(
          Effect.provide(
            MockSettingsLayer({
              dedicatedWorkspace: {
                saKeyJson: validSaKeyJson,
                adminEmail: "admin@example.com",
                domain: "example.com",
              },
            }),
          ),
        ),
    );

    it.effect(
      "returns DedicatedWorkspaceAuthError when token exchange returns no access_token",
      () =>
        Effect.gen(function* () {
          mockFetch.mockResolvedValueOnce(new Response(JSON.stringify({})));

          const result = yield* getAccessToken().pipe(Effect.either);
          expect(Either.isLeft(result)).toBe(true);
          if (Either.isLeft(result)) {
            expect(result.left._tag).toBe("DedicatedWorkspaceAuthError");
            expect(result.left.message).toContain("No access token");
          }
        }).pipe(
          Effect.provide(
            MockSettingsLayer({
              dedicatedWorkspace: {
                saKeyJson: validSaKeyJson,
                adminEmail: "admin@example.com",
                domain: "example.com",
              },
            }),
          ),
        ),
    );

    it.effect("returns DedicatedWorkspaceAuthError when fetch throws", () =>
      Effect.gen(function* () {
        mockFetch.mockRejectedValueOnce(new Error("Network error"));

        const result = yield* getAccessToken().pipe(Effect.either);
        expect(Either.isLeft(result)).toBe(true);
        if (Either.isLeft(result)) {
          expect(result.left._tag).toBe("DedicatedWorkspaceAuthError");
          expect(result.left.message).toContain(
            "Failed to call token endpoint",
          );
        }
      }).pipe(
        Effect.provide(
          MockSettingsLayer({
            dedicatedWorkspace: {
              saKeyJson: validSaKeyJson,
              adminEmail: "admin@example.com",
              domain: "example.com",
            },
          }),
        ),
      ),
    );
  });
});
