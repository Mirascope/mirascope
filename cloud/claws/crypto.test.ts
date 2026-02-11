import { Effect, Layer } from "effect";
import { describe, it, expect, vi } from "vitest";

import { encryptSecrets, decryptSecrets } from "@/claws/crypto";
import { EncryptionError } from "@/errors";
import { Settings } from "@/settings";
import { MockSettingsLayer } from "@/tests/settings";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const TestSettings = MockSettingsLayer();

const run = <A>(effect: Effect.Effect<A, EncryptionError, Settings>) =>
  Effect.runPromise(effect.pipe(Effect.provide(TestSettings)));

const runFail = (effect: Effect.Effect<unknown, EncryptionError, Settings>) =>
  Effect.runPromise(effect.pipe(Effect.flip, Effect.provide(TestSettings)));

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("encryptSecrets / decryptSecrets", () => {
  it("round-trips secrets through encrypt then decrypt", async () => {
    const original = {
      R2_ACCESS_KEY_ID: "ak-123",
      R2_SECRET_ACCESS_KEY: "sk-456",
      CUSTOM_VAR: "hello",
    };

    const { ciphertext, keyId } = await run(encryptSecrets(original));

    expect(typeof ciphertext).toBe("string");
    expect(ciphertext.length).toBeGreaterThan(0);
    expect(keyId).toBe("CLAW_SECRETS_ENCRYPTION_KEY_V1");

    // Ciphertext should NOT contain plaintext
    expect(ciphertext).not.toContain("ak-123");
    expect(ciphertext).not.toContain("sk-456");

    const decrypted = await run(decryptSecrets(ciphertext, keyId));
    expect(decrypted).toEqual(original);
  });

  it("round-trips empty secrets", async () => {
    const original = {};
    const { ciphertext, keyId } = await run(encryptSecrets(original));
    const decrypted = await run(decryptSecrets(ciphertext, keyId));
    expect(decrypted).toEqual(original);
  });

  it("produces different ciphertexts for the same input (random IV)", async () => {
    const secrets = { KEY: "value" };
    const a = await run(encryptSecrets(secrets));
    const b = await run(encryptSecrets(secrets));
    expect(a.ciphertext).not.toBe(b.ciphertext);
  });

  it("returns EncryptionError for unknown keyId on decrypt", async () => {
    const { ciphertext } = await run(encryptSecrets({ KEY: "value" }));

    const error = await runFail(decryptSecrets(ciphertext, "NONEXISTENT_KEY"));
    expect(error).toBeInstanceOf(EncryptionError);
    expect(error.message).toContain("Unknown encryption key ID");
  });

  it("returns EncryptionError for corrupted ciphertext", async () => {
    const error = await runFail(
      decryptSecrets(
        // valid base64 but not valid AES-GCM ciphertext
        btoa("x".repeat(20)),
        "CLAW_SECRETS_ENCRYPTION_KEY_V1",
      ),
    );
    expect(error).toBeInstanceOf(EncryptionError);
    expect(error.message).toContain("Decryption failed");
  });

  it("returns EncryptionError for ciphertext too short", async () => {
    const error = await runFail(
      decryptSecrets(
        btoa("short"), // only 5 bytes — less than IV_LENGTH + 1
        "CLAW_SECRETS_ENCRYPTION_KEY_V1",
      ),
    );
    expect(error).toBeInstanceOf(EncryptionError);
    expect(error.message).toContain("too short");
  });

  it("returns EncryptionError for invalid key length", async () => {
    const BadKeySettings = Layer.succeed(Settings, {
      encryptionKeys: {
        BAD_KEY: btoa("only-16-bytes!!"), // 15 bytes, not 32
      },
      activeEncryptionKeyId: "BAD_KEY",
    } as never);

    const error = await Effect.runPromise(
      encryptSecrets({ KEY: "value" }).pipe(
        Effect.flip,
        Effect.provide(BadKeySettings),
      ),
    );
    expect(error).toBeInstanceOf(EncryptionError);
    expect(error.message).toContain("Failed to import encryption key");
  });

  it("returns EncryptionError when crypto.subtle.encrypt fails", async () => {
    const spy = vi
      .spyOn(crypto.subtle, "encrypt")
      .mockRejectedValueOnce(new Error("simulated encrypt failure"));

    const error = await runFail(encryptSecrets({ KEY: "value" }));
    expect(error).toBeInstanceOf(EncryptionError);
    expect(error.message).toContain("Encryption failed");

    spy.mockRestore();
  });

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

  it("returns EncryptionError for unknown keyId on encrypt", async () => {
    const MissingActiveKey = Layer.succeed(Settings, {
      encryptionKeys: {},
      activeEncryptionKeyId: "DOES_NOT_EXIST",
    } as never);

    const error = await Effect.runPromise(
      encryptSecrets({ KEY: "value" }).pipe(
        Effect.flip,
        Effect.provide(MissingActiveKey),
      ),
    );
    expect(error).toBeInstanceOf(EncryptionError);
    expect(error.message).toContain("Unknown encryption key ID");
  });
});
