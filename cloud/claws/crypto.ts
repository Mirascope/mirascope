/**
 * @fileoverview AES-256-GCM encryption/decryption for claw secrets.
 *
 * Uses the Web Crypto API (compatible with Cloudflare Workers) to encrypt
 * and decrypt the `secretsEncrypted` column in the claws table.
 *
 * ## Wire format
 *
 * The ciphertext stored in the DB is a base64-encoded concatenation of:
 *
 *   iv (12 bytes) || ciphertext+authTag (variable)
 *
 * GCM appends a 16-byte authentication tag to the ciphertext automatically.
 *
 * ## Key management
 *
 * Keys are versioned via `Settings.encryptionKeys` (a map of keyId → base64 key).
 * The active key for new encryptions is `Settings.activeEncryptionKeyId`.
 * On decrypt, the `keyId` stored alongside the ciphertext selects which key to use,
 * enabling seamless key rotation.
 */
import { Effect } from "effect";

import { EncryptionError } from "@/errors";
import { Settings } from "@/settings";

// 12-byte IV is the recommended size for AES-GCM
const IV_LENGTH = 12;

// ---------------------------------------------------------------------------
// Base64 helpers (safe for arbitrarily large payloads — no spread operator)
// ---------------------------------------------------------------------------

function uint8ArrayToBase64(bytes: Uint8Array): string {
  let binary = "";
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

function base64ToUint8Array(base64: string): Uint8Array {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}

// ---------------------------------------------------------------------------
// Key helpers
// ---------------------------------------------------------------------------

/**
 * Import a base64-encoded 256-bit key as a CryptoKey for AES-GCM.
 */
function importKey(
  base64Key: string,
): Effect.Effect<CryptoKey, EncryptionError> {
  return Effect.tryPromise({
    try: () => {
      const raw = base64ToUint8Array(base64Key);
      if (raw.length !== 32) {
        throw new Error(
          `Encryption key must be 32 bytes (256 bits), got ${raw.length}`,
        );
      }
      return crypto.subtle.importKey(
        "raw",
        raw.buffer as ArrayBuffer,
        "AES-GCM",
        false,
        ["encrypt", "decrypt"],
      );
    },
    catch: (cause) =>
      new EncryptionError({
        message: "Failed to import encryption key",
        cause,
      }),
  });
}

/**
 * Resolve and import the encryption key for a given keyId from Settings.
 */
function resolveKey(
  keyId: string,
): Effect.Effect<CryptoKey, EncryptionError, Settings> {
  return Effect.gen(function* () {
    const settings = yield* Settings;
    const base64Key = settings.encryptionKeys[keyId];
    if (!base64Key) {
      return yield* Effect.fail(
        new EncryptionError({
          message: `Unknown encryption key ID: ${keyId}`,
        }),
      );
    }
    return yield* importKey(base64Key);
  });
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Encrypt a secrets record using the active encryption key.
 *
 * Returns the base64-encoded ciphertext and the keyId used.
 */
export function encryptSecrets(
  secrets: Record<string, string | undefined>,
): Effect.Effect<
  { ciphertext: string; keyId: string },
  EncryptionError,
  Settings
> {
  return Effect.gen(function* () {
    const settings = yield* Settings;
    const keyId = settings.activeEncryptionKeyId;
    const cryptoKey = yield* resolveKey(keyId);

    const plaintext = new TextEncoder().encode(JSON.stringify(secrets));
    const iv = crypto.getRandomValues(new Uint8Array(IV_LENGTH));

    const encrypted = yield* Effect.tryPromise({
      try: () =>
        crypto.subtle.encrypt({ name: "AES-GCM", iv }, cryptoKey, plaintext),
      catch: (cause) =>
        new EncryptionError({ message: "Encryption failed", cause }),
    });

    // Concatenate iv + ciphertext (which includes the GCM auth tag)
    const combined = new Uint8Array(iv.length + encrypted.byteLength);
    combined.set(iv);
    combined.set(new Uint8Array(encrypted), iv.length);

    const ciphertext = uint8ArrayToBase64(combined);

    return { ciphertext, keyId };
  });
}

/**
 * Decrypt a ciphertext string using the key identified by keyId.
 *
 * Returns the original secrets record.
 */
export function decryptSecrets(
  ciphertext: string,
  keyId: string,
): Effect.Effect<
  Record<string, string | undefined>,
  EncryptionError,
  Settings
> {
  return Effect.gen(function* () {
    const cryptoKey = yield* resolveKey(keyId);

    const combined = base64ToUint8Array(ciphertext);

    if (combined.length < IV_LENGTH + 1) {
      return yield* Effect.fail(
        new EncryptionError({
          message: "Ciphertext too short to contain IV and data",
        }),
      );
    }

    const iv = new Uint8Array(
      combined.buffer as ArrayBuffer,
      combined.byteOffset,
      IV_LENGTH,
    );
    const data = new Uint8Array(
      combined.buffer as ArrayBuffer,
      combined.byteOffset + IV_LENGTH,
    );

    const decrypted = yield* Effect.tryPromise({
      try: () =>
        crypto.subtle.decrypt({ name: "AES-GCM", iv }, cryptoKey, data),
      catch: (cause) =>
        new EncryptionError({
          message: "Decryption failed (wrong key or corrupted data)",
          cause,
        }),
    });

    const json = new TextDecoder().decode(decrypted);

    return yield* Effect.try({
      try: () => JSON.parse(json) as Record<string, string | undefined>,
      catch: (cause) =>
        new EncryptionError({
          message: "Decrypted data is not valid JSON",
          cause,
        }),
    });
  });
}
