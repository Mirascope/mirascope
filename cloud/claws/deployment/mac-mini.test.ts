/**
 * @fileoverview Tests for the Mac Mini deployment service.
 */

import { describe, it, expect } from "@effect/vitest";
import { Effect, Layer } from "effect";

import { ClawDeploymentError } from "@/claws/deployment/errors";
import {
  MacMiniFleetService,
} from "@/claws/deployment/mac-mini-fleet";
import { MacMiniDeploymentService } from "@/claws/deployment/mac-mini";
import { ClawDeploymentService } from "@/claws/deployment/service";
import { CloudflareR2Service } from "@/cloudflare/r2/service";
import { DrizzleORM } from "@/db/client";
import { Settings } from "@/settings";

// Mock fleet service that returns predictable results
const mockFleetService = Layer.succeed(MacMiniFleetService, {
  findAvailableMini: () =>
    Effect.succeed({
      miniId: "mini-test-id",
      agentUrl: "https://agent.test.example.com",
      port: 3042,
      tunnelHostnameSuffix: "claws.test.dev",
    }),
  callAgent: (_miniId: string, _method: string, _path: string, _body?: unknown) =>
    Effect.succeed({ status: "running" }),
});

// Mock R2 service
const mockR2Service = Layer.succeed(CloudflareR2Service, {
  createBucket: (_name: string) => Effect.succeed(undefined as any),
  deleteBucket: (_name: string) => Effect.succeed(undefined as any),
  createScopedCredentials: (_bucketName: string) =>
    Effect.succeed({
      accessKeyId: "test-access-key",
      secretAccessKey: "test-secret-key",
    }),
  revokeScopedCredentials: (_accessKeyId: string) =>
    Effect.succeed(undefined as any),
} as any);

// Mock DrizzleORM — the deployment service queries claws table for deprovision/status/restart
const mockDrizzle = {
  select: () => ({
    from: () => ({
      where: () => ({
        limit: () =>
          Effect.succeed([
            { miniId: "mini-test-id", slug: "test-claw" },
          ]),
      }),
    }),
  }),
  update: () => ({
    set: () => ({
      where: () => Effect.succeed(undefined),
    }),
  }),
} as any;

const mockDrizzleLayer = Layer.succeed(DrizzleORM, mockDrizzle);

// Mock Settings for decryptSecrets dependency
const mockSettingsLayer = Layer.succeed(Settings, {
  encryptionKeys: {
    CLAW_SECRETS_ENCRYPTION_KEY_V1: "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
  },
  activeEncryptionKeyId: "CLAW_SECRETS_ENCRYPTION_KEY_V1",
} as any);

const testLayer = MacMiniDeploymentService.pipe(
  Layer.provide(mockFleetService),
  Layer.provide(mockR2Service),
  Layer.provide(mockDrizzleLayer),
  Layer.provide(mockSettingsLayer),
);

describe("MacMiniDeploymentService", () => {
  describe("provision", () => {
    it.effect("provisions a claw on a Mac Mini", () =>
      Effect.gen(function* () {
        const deployment = yield* ClawDeploymentService;
        const status = yield* deployment.provision({
          clawId: "claw-abc-123",
          instanceType: "basic",
        });

        expect(status.status).toBe("provisioning");
        expect(status.bucketName).toBe("claw-claw-abc-123");
        expect(status.r2Credentials).toBeDefined();
        expect(status.r2Credentials!.accessKeyId).toBe("test-access-key");
        expect(status.miniId).toBe("mini-test-id");
        expect(status.miniPort).toBe(3042);
        expect(status.tunnelHostname).toBe("claw-abc-123.claws.test.dev");
      }).pipe(Effect.provide(testLayer)),
    );
  });

  describe("warmUp", () => {
    it.effect("calls agent status endpoint", () =>
      Effect.gen(function* () {
        const deployment = yield* ClawDeploymentService;
        yield* deployment.warmUp("claw-abc-123");
        // If we get here without error, the warm-up succeeded
      }).pipe(Effect.provide(testLayer)),
    );
  });

  describe("restart", () => {
    it.effect("calls agent restart endpoint", () =>
      Effect.gen(function* () {
        const deployment = yield* ClawDeploymentService;
        const status = yield* deployment.restart("claw-abc-123");
        expect(status.status).toBe("provisioning");
      }).pipe(Effect.provide(testLayer)),
    );
  });

  describe("getStatus", () => {
    it.effect("returns mapped status from agent", () =>
      Effect.gen(function* () {
        const deployment = yield* ClawDeploymentService;
        const status = yield* deployment.getStatus("claw-abc-123");
        expect(status.status).toBe("active"); // agent returns "running"
      }).pipe(Effect.provide(testLayer)),
    );
  });
});
