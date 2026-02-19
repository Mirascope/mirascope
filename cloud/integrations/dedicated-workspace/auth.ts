import { Data, Effect } from "effect";

import { Settings } from "@/settings";

export class DedicatedWorkspaceAuthError extends Data.TaggedError(
  "DedicatedWorkspaceAuthError",
)<{
  readonly message: string;
  readonly cause?: unknown;
}> {}

export class MissingConfigError extends Data.TaggedError("MissingConfigError")<{
  readonly message: string;
}> {}

/**
 * Parsed service account key JSON structure.
 */
type ServiceAccountKey = {
  readonly client_email: string;
  readonly private_key: string;
  readonly token_uri: string;
};

/**
 * Converts a PEM-encoded RSA private key to a CryptoKey for RS256 signing.
 */
function importPrivateKey(pem: string): Promise<CryptoKey> {
  const pemContents = pem
    .replace(/-----BEGIN PRIVATE KEY-----/, "")
    .replace(/-----END PRIVATE KEY-----/, "")
    .replace(/\s/g, "");
  const binaryDer = Uint8Array.from(atob(pemContents), (c) => c.charCodeAt(0));
  return crypto.subtle.importKey(
    "pkcs8",
    binaryDer,
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false,
    ["sign"],
  );
}

/**
 * Base64url-encodes a string (no padding).
 */
function base64url(input: string): string {
  return btoa(input).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

/**
 * Base64url-encodes a Uint8Array (no padding).
 */
function base64urlBytes(bytes: Uint8Array): string {
  return btoa(String.fromCharCode(...bytes))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

/**
 * Mints an access token for the Google Admin SDK Directory API
 * using a GCP service account with domain-wide delegation.
 *
 * Steps:
 * 1. Parse the service account JSON from settings
 * 2. Build a JWT with domain-wide delegation claims (sub = admin email)
 * 3. Sign with RS256 using Web Crypto API
 * 4. Exchange for an access token via Google's token endpoint
 */
export function getAccessToken(): Effect.Effect<
  { accessToken: string; expiresIn: number },
  MissingConfigError | DedicatedWorkspaceAuthError,
  Settings
> {
  return Effect.gen(function* () {
    const settings = yield* Settings;

    const missingFields: string[] = [];
    if (!settings.dedicatedWorkspace.saKeyJson) {
      missingFields.push(
        "DEDICATED_WORKSPACE_SA_KEY_JSON (dedicatedWorkspace.saKeyJson)",
      );
    }
    if (!settings.dedicatedWorkspace.adminEmail) {
      missingFields.push(
        "DEDICATED_WORKSPACE_ADMIN_EMAIL (dedicatedWorkspace.adminEmail)",
      );
    }
    if (!settings.dedicatedWorkspace.domain) {
      missingFields.push(
        "DEDICATED_WORKSPACE_DOMAIN (dedicatedWorkspace.domain)",
      );
    }
    if (missingFields.length > 0) {
      return yield* Effect.fail(
        new MissingConfigError({
          message: `Dedicated workspace configuration is incomplete. Missing: ${missingFields.join(", ")}`,
        }),
      );
    }

    // Parse service account key
    const saKey = yield* Effect.try({
      try: () =>
        JSON.parse(settings.dedicatedWorkspace.saKeyJson!) as ServiceAccountKey,
      catch: () =>
        new DedicatedWorkspaceAuthError({
          message: "Failed to parse DEDICATED_WORKSPACE_SA_KEY_JSON",
        }),
    });

    if (!saKey.client_email || !saKey.private_key || !saKey.token_uri) {
      return yield* Effect.fail(
        new DedicatedWorkspaceAuthError({
          message:
            "Service account key missing required fields: client_email, private_key, token_uri",
        }),
      );
    }

    const now = Math.floor(Date.now() / 1000);
    const header = { alg: "RS256", typ: "JWT" };
    const payload = {
      iss: saKey.client_email,
      scope: "https://www.googleapis.com/auth/admin.directory.user",
      sub: settings.dedicatedWorkspace.adminEmail,
      aud: saKey.token_uri,
      iat: now,
      exp: now + 3600,
    };

    const headerB64 = base64url(JSON.stringify(header));
    const payloadB64 = base64url(JSON.stringify(payload));
    const signingInput = `${headerB64}.${payloadB64}`;

    // Sign with RS256
    const signature = yield* Effect.tryPromise({
      try: async () => {
        const key = await importPrivateKey(saKey.private_key);
        const sig = await crypto.subtle.sign(
          "RSASSA-PKCS1-v1_5",
          key,
          new TextEncoder().encode(signingInput),
        );
        return base64urlBytes(new Uint8Array(sig));
      },
      catch: (e) =>
        new DedicatedWorkspaceAuthError({
          message: "Failed to sign JWT",
          cause: e,
        }),
    });

    const jwt = `${signingInput}.${signature}`;

    // Exchange JWT for access token
    const tokenResponse = yield* Effect.tryPromise({
      try: async () => {
        const response = await fetch(saKey.token_uri, {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: new URLSearchParams({
            grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer",
            assertion: jwt,
          }),
        });
        return (await response.json()) as {
          access_token?: string;
          expires_in?: number;
          error?: string;
          error_description?: string;
        };
      },
      catch: (e) =>
        new DedicatedWorkspaceAuthError({
          message: "Failed to call token endpoint",
          cause: e,
        }),
    });

    if (tokenResponse.error || !tokenResponse.access_token) {
      return yield* Effect.fail(
        new DedicatedWorkspaceAuthError({
          message: `Token exchange failed: ${tokenResponse.error_description || tokenResponse.error || "No access token"}`,
        }),
      );
    }

    return {
      accessToken: tokenResponse.access_token,
      expiresIn: tokenResponse.expires_in || 3600,
    };
  });
}
