import { describe, it, expect } from "@effect/vitest";
import { Effect, Either } from "effect";

import { signState, verifyState } from "@/integrations/google-workspace/hmac";
import { MockSettingsLayer } from "@/tests/settings";

const mockStateData = {
  randomState: "test-random-state",
  clawId: "test-claw-id",
  organizationId: "test-org-id",
  userId: "test-user-id",
} as const;

describe("HMAC state signing", () => {
  it.effect("signs and verifies state roundtrip", () =>
    Effect.gen(function* () {
      const encoded = yield* signState(mockStateData);
      const verified = yield* verifyState(encoded);
      expect(verified).toEqual(mockStateData);
    }).pipe(Effect.provide(MockSettingsLayer())),
  );

  it.effect("produces base64-encoded JSON containing HMAC", () =>
    Effect.gen(function* () {
      const encoded = yield* signState(mockStateData);
      const decoded = JSON.parse(atob(encoded)) as Record<string, unknown>;
      expect(decoded.hmac).toBeDefined();
      expect(typeof decoded.hmac).toBe("string");
      expect(decoded.clawId).toBe("test-claw-id");
    }).pipe(Effect.provide(MockSettingsLayer())),
  );

  it.effect("rejects tampered state data", () =>
    Effect.gen(function* () {
      const encoded = yield* signState(mockStateData);
      const decoded = JSON.parse(atob(encoded)) as Record<string, unknown>;
      decoded.clawId = "tampered-claw-id";
      const tampered = btoa(JSON.stringify(decoded));

      const result = yield* verifyState(tampered).pipe(Effect.either);
      expect(Either.isLeft(result)).toBe(true);
      if (Either.isLeft(result)) {
        expect(result.left.message).toBe("Invalid state signature");
      }
    }).pipe(Effect.provide(MockSettingsLayer())),
  );

  it.effect("rejects state with missing HMAC", () =>
    Effect.gen(function* () {
      const noHmac = btoa(JSON.stringify(mockStateData));
      const result = yield* verifyState(noHmac).pipe(Effect.either);
      expect(Either.isLeft(result)).toBe(true);
      if (Either.isLeft(result)) {
        expect(result.left.message).toBe("Missing HMAC signature in state");
      }
    }).pipe(Effect.provide(MockSettingsLayer())),
  );

  it.effect("rejects invalid base64 state", () =>
    Effect.gen(function* () {
      const result = yield* verifyState("not-valid!!!").pipe(Effect.either);
      expect(Either.isLeft(result)).toBe(true);
    }).pipe(Effect.provide(MockSettingsLayer())),
  );

  it.effect("rejects state with corrupted HMAC", () =>
    Effect.gen(function* () {
      const encoded = yield* signState(mockStateData);
      const decoded = JSON.parse(atob(encoded)) as Record<string, unknown>;
      decoded.hmac = btoa("corrupted-signature-data");
      const corrupted = btoa(JSON.stringify(decoded));

      const result = yield* verifyState(corrupted).pipe(Effect.either);
      expect(Either.isLeft(result)).toBe(true);
    }).pipe(Effect.provide(MockSettingsLayer())),
  );
});
