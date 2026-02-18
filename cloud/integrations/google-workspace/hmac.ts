import { Effect } from "effect";

import { InvalidStateError, OAuthError } from "@/auth/errors";
import { Settings } from "@/settings";

/**
 * OAuth state data passed through the Google OAuth flow.
 */
export type OAuthStateData = {
  readonly randomState: string;
  readonly clawId: string;
  readonly organizationId: string;
  readonly userId: string;
};

/**
 * HMAC-signs the OAuth state data using the active encryption key.
 * Returns a base64-encoded JSON string containing the state data and HMAC signature.
 */
export function signState(
  stateData: OAuthStateData,
): Effect.Effect<string, OAuthError, Settings> {
  return Effect.gen(function* () {
    const settings = yield* Settings;
    const keyBase64 = settings.encryptionKeys[settings.activeEncryptionKeyId];
    if (!keyBase64) {
      return yield* Effect.fail(
        new OAuthError({
          message: "Encryption key not configured",
          provider: "google-workspace",
        }),
      );
    }

    const stateJson = JSON.stringify(stateData);

    const hmac = yield* Effect.tryPromise({
      try: async () => {
        const keyBytes = Uint8Array.from(atob(keyBase64), (c) =>
          c.charCodeAt(0),
        );
        const cryptoKey = await crypto.subtle.importKey(
          "raw",
          keyBytes,
          { name: "HMAC", hash: "SHA-256" },
          false,
          ["sign"],
        );
        const sig = await crypto.subtle.sign(
          "HMAC",
          cryptoKey,
          new TextEncoder().encode(stateJson),
        );
        return btoa(String.fromCharCode(...new Uint8Array(sig)));
      },
      catch: () =>
        new OAuthError({
          message: "Failed to sign OAuth state",
          provider: "google-workspace",
        }),
    });

    return btoa(JSON.stringify({ ...stateData, hmac }));
  });
}

/**
 * Verifies the HMAC signature on an encoded OAuth state string.
 * Returns the validated state data (without the HMAC field).
 */
export function verifyState(
  encodedState: string,
): Effect.Effect<OAuthStateData, InvalidStateError, Settings> {
  return Effect.gen(function* () {
    const settings = yield* Settings;
    const keyBase64 = settings.encryptionKeys[settings.activeEncryptionKeyId];

    const parsed = yield* Effect.try({
      try: () =>
        JSON.parse(atob(encodedState)) as OAuthStateData & { hmac: string },
      catch: () =>
        new InvalidStateError({
          message: "Failed to decode state parameter",
        }),
    });

    const { hmac: stateHmac, ...stateData } = parsed;

    if (!stateHmac) {
      return yield* Effect.fail(
        new InvalidStateError({
          message: "Missing HMAC signature in state",
        }),
      );
    }

    const stateJson = JSON.stringify(stateData);

    const isValid = yield* Effect.tryPromise({
      try: async () => {
        const keyBytes = Uint8Array.from(atob(keyBase64!), (c) =>
          c.charCodeAt(0),
        );
        const cryptoKey = await crypto.subtle.importKey(
          "raw",
          keyBytes,
          { name: "HMAC", hash: "SHA-256" },
          false,
          ["verify"],
        );
        const sigBytes = Uint8Array.from(atob(stateHmac), (c) =>
          c.charCodeAt(0),
        );
        return crypto.subtle.verify(
          "HMAC",
          cryptoKey,
          sigBytes,
          new TextEncoder().encode(stateJson),
        );
      },
      catch: () =>
        new InvalidStateError({
          message: "Failed to verify state signature",
        }),
    });

    if (!isValid) {
      return yield* Effect.fail(
        new InvalidStateError({
          message: "Invalid state signature",
        }),
      );
    }

    return stateData;
  });
}
