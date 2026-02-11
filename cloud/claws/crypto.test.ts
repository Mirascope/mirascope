import { describe, it, expect, vi } from "@effect/vitest";
import { Effect, Layer } from "effect";

import { encryptSecrets, decryptSecrets } from "@/claws/crypto";
import { EncryptionError } from "@/errors";
import { Settings } from "@/settings";
import { MockSettingsLayer } from "@/tests/settings";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const TestSettings = MockSettingsLayer();

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("encryptSecrets / decryptSecrets", () => {
  it.effect("round-trips secrets through encrypt then decrypt", () =>
    Effect.gen(function* () {
      const original = {
        R2_ACCESS_KEY_ID: "ak-123",
        R2_SECRET_ACCESS_KEY: "sk-456",
        CUSTOM_VAR: "hello",
      };

      const { ciphertext, keyId } = yield* encryptSecrets(original);

      expect(typeof ciphertext).toBe("string");
      expect(ciphertext.length).toBeGreaterThan(0);
      expect(keyId).toBe("CLAW_SECRETS_ENCRYPTION_KEY_V1");

      // Ciphertext should NOT contain plaintext
      expect(ciphertext).not.toContain("ak-123");
      expect(ciphertext).not.toContain("sk-456");

      const decrypted = yield* decryptSecrets(ciphertext, keyId);
      expect(decrypted).toEqual(original);
    }).pipe(Effect.provide(TestSettings)),
  );

  it.effect("round-trips empty secrets", () =>
    Effect.gen(function* () {
      const original = {};
      const { ciphertext, keyId } = yield* encryptSecrets(original);
      const decrypted = yield* decryptSecrets(ciphertext, keyId);
      expect(decrypted).toEqual(original);
    }).pipe(Effect.provide(TestSettings)),
  );

  it.effect(
    "produces different ciphertexts for the same input (random IV)",
    () =>
      Effect.gen(function* () {
        const secrets = { KEY: "value" };
        const a = yield* encryptSecrets(secrets);
        const b = yield* encryptSecrets(secrets);
        expect(a.ciphertext).not.toBe(b.ciphertext);
      }).pipe(Effect.provide(TestSettings)),
  );

  it.effect("returns EncryptionError for unknown keyId on decrypt", () =>
    Effect.gen(function* () {
      const { ciphertext } = yield* encryptSecrets({ KEY: "value" });

      const error = yield* decryptSecrets(ciphertext, "NONEXISTENT_KEY").pipe(
        Effect.flip,
      );
      expect(error).toBeInstanceOf(EncryptionError);
      expect(error.message).toContain("Unknown encryption key ID");
    }).pipe(Effect.provide(TestSettings)),
  );

  it.effect("returns EncryptionError for corrupted ciphertext", () =>
    Effect.gen(function* () {
      const error = yield* decryptSecrets(
        // valid base64 but not valid AES-GCM ciphertext
        btoa("x".repeat(20)),
        "CLAW_SECRETS_ENCRYPTION_KEY_V1",
      ).pipe(Effect.flip);
      expect(error).toBeInstanceOf(EncryptionError);
      expect(error.message).toContain("Decryption failed");
    }).pipe(Effect.provide(TestSettings)),
  );

  it.effect("returns EncryptionError for ciphertext too short", () =>
    Effect.gen(function* () {
      const error = yield* decryptSecrets(
        btoa("short"), // only 5 bytes — less than IV_LENGTH + 1
        "CLAW_SECRETS_ENCRYPTION_KEY_V1",
      ).pipe(Effect.flip);
      expect(error).toBeInstanceOf(EncryptionError);
      expect(error.message).toContain("too short");
    }).pipe(Effect.provide(TestSettings)),
  );

  it.effect("returns EncryptionError for invalid key length", () => {
    const BadKeySettings = Layer.succeed(Settings, {
      encryptionKeys: {
        BAD_KEY: btoa("only-16-bytes!!"), // 15 bytes, not 32
      },
      activeEncryptionKeyId: "BAD_KEY",
    } as never);

    return encryptSecrets({ KEY: "value" }).pipe(
      Effect.flip,
      Effect.provide(BadKeySettings),
      Effect.tap((error) =>
        Effect.sync(() => {
          expect(error).toBeInstanceOf(EncryptionError);
          expect(error.message).toContain("Failed to import encryption key");
        }),
      ),
    );
  });

  it.effect("returns EncryptionError when crypto.subtle.encrypt fails", () =>
    Effect.gen(function* () {
      const spy = vi
        .spyOn(crypto.subtle, "encrypt")
        .mockRejectedValueOnce(new Error("simulated encrypt failure"));

      const error = yield* encryptSecrets({ KEY: "value" }).pipe(Effect.flip);
      expect(error).toBeInstanceOf(EncryptionError);
      expect(error.message).toContain("Encryption failed");

      spy.mockRestore();
    }).pipe(Effect.provide(TestSettings)),
  );

  it("returns EncryptionError when decrypted data is not valid JSON", async () => {
    // Encrypt raw non-JSON bytes using the same key, then decrypt via decryptSecrets
    const settings = Layer.succeed(Settings, {
      encryptionKeys: {
        CLAW_SECRETS_ENCRYPTION_KEY_V1:
          "S0YrcgEScoOL1ALp/w+xI90P9O8h4s3OzEXtzlhBbHQ=",
      },
      activeEncryptionKeyId: "CLAW_SECRETS_ENCRYPTION_KEY_V1",
    } as never);

    // Manually encrypt non-JSON plaintext using the Web Crypto API
    const rawKey = Uint8Array.from(
      atob("S0YrcgEScoOL1ALp/w+xI90P9O8h4s3OzEXtzlhBbHQ="),
      (c) => c.charCodeAt(0),
    );
    const cryptoKey = await crypto.subtle.importKey(
      "raw",
      rawKey.buffer as ArrayBuffer,
      "AES-GCM",
      false,
      ["encrypt"],
    );
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const plaintext = new TextEncoder().encode("not json!!!");
    const encrypted = await crypto.subtle.encrypt(
      { name: "AES-GCM", iv },
      cryptoKey,
      plaintext,
    );
    const combined = new Uint8Array(iv.length + encrypted.byteLength);
    combined.set(iv);
    combined.set(new Uint8Array(encrypted), iv.length);
    let binary = "";
    for (let i = 0; i < combined.byteLength; i++) {
      binary += String.fromCharCode(combined[i]);
    }
    const ciphertext = btoa(binary);

    const error = await Effect.runPromise(
      decryptSecrets(ciphertext, "CLAW_SECRETS_ENCRYPTION_KEY_V1").pipe(
        Effect.flip,
        Effect.provide(settings),
      ),
    );
    expect(error).toBeInstanceOf(EncryptionError);
    expect(error.message).toContain("not valid JSON");
  });

  it.effect("returns EncryptionError for unknown keyId on encrypt", () => {
    const MissingActiveKey = Layer.succeed(Settings, {
      encryptionKeys: {},
      activeEncryptionKeyId: "DOES_NOT_EXIST",
    } as never);

    return encryptSecrets({ KEY: "value" }).pipe(
      Effect.flip,
      Effect.provide(MissingActiveKey),
      Effect.tap((error) =>
        Effect.sync(() => {
          expect(error).toBeInstanceOf(EncryptionError);
          expect(error.message).toContain("Unknown encryption key ID");
        }),
      ),
    );
  });
});
