import * as crypto from "crypto";
import { eq } from "drizzle-orm";
import { Effect, Layer } from "effect";

import type { CreateClawRequest, UpdateClawRequest } from "@/api/claws.schemas";
import type { ClawInstanceType } from "@/claws/deployment/types";

import { Analytics } from "@/analytics";
import { AuthenticatedUser } from "@/auth";
import { encryptSecrets } from "@/claws/crypto";
import {
  ClawDeploymentService,
  type ClawDeploymentServiceInterface,
} from "@/claws/deployment/service";
import { DrizzleORM } from "@/db/client";
import { Database } from "@/db/database";
import { claws } from "@/db/schema";
import { DatabaseError } from "@/errors";
import { ExecutionContext } from "@/server-entry";
import { Settings, type SettingsConfig } from "@/settings";

export * from "@/api/claws.schemas";

export const listClawsHandler = (organizationId: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.claws.findAll({
      userId: user.id,
      organizationId,
    });
  });

/**
 * Provisions a claw in the background: creates R2 bucket, encrypts secrets,
 * updates DB, and warms up the container. On failure, marks claw as "error".
 *
 * Exported for testing. Not part of the public API.
 */
export const provisionClawBackground = (
  claw: {
    id: string;
    instanceType: ClawInstanceType;
    plaintextApiKey: string;
  },
  deps: {
    clawDeployment: ClawDeploymentServiceInterface;
    settings: SettingsConfig;
  },
) =>
  Effect.gen(function* () {
    const drizzle = yield* DrizzleORM;
    // Provision R2 bucket and scoped credentials
    const status = yield* deps.clawDeployment.provision({
      clawId: claw.id,
      instanceType: claw.instanceType,
    });

    // Generate gateway token for container auth
    const gatewayToken = crypto.randomUUID();

    // Build Mirascope Router base URL for Anthropic-compatible proxy
    const routerBaseUrl = `${deps.settings.siteUrl}/router/v2/anthropic`;

    // Encrypt all container secrets before persisting
    const encrypted = yield* encryptSecrets({
      ANTHROPIC_API_KEY: claw.plaintextApiKey,
      ANTHROPIC_BASE_URL: routerBaseUrl,
      OPENCLAW_GATEWAY_TOKEN: gatewayToken,
      R2_ACCESS_KEY_ID: status.r2Credentials?.accessKeyId ?? "",
      R2_SECRET_ACCESS_KEY: status.r2Credentials?.secretAccessKey ?? "",
    });

    yield* drizzle
      .update(claws)
      .set({
        bucketName: status.bucketName ?? null,
        secretsEncrypted: encrypted.ciphertext,
        secretsKeyId: encrypted.keyId,
        status: "provisioning",
        updatedAt: new Date(),
      })
      .where(eq(claws.id, claw.id))
      .pipe(
        Effect.mapError(
          (e) =>
            new DatabaseError({
              message: "Failed to persist deployment credentials",
              cause: e,
            }),
        ),
      );

    // Trigger cold start on dispatch worker (reads creds from DB via bootstrap API)
    yield* deps.clawDeployment.warmUp(claw.id);
  }).pipe(
    Effect.catchAll((error) =>
      Effect.flatMap(DrizzleORM, (drizzle) =>
        drizzle
          .update(claws)
          .set({
            status: "error",
            updatedAt: new Date(),
          })
          .where(eq(claws.id, claw.id))
          .pipe(
            Effect.tapError(() =>
              Effect.logError(
                `Failed to mark claw ${claw.id} as error after provisioning failure`,
              ),
            ),
            Effect.catchAll(() => Effect.void),
            Effect.tap(() =>
              Effect.logError(
                `Claw ${claw.id} provisioning failed: ${String(error)}`,
              ),
            ),
          ),
      ),
    ),
  );

export const createClawHandler = (
  organizationId: string,
  payload: CreateClawRequest,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    const analytics = yield* Analytics;
    const clawDeployment = yield* ClawDeploymentService;
    const settings = yield* Settings;
    const ctx = yield* ExecutionContext;

    const claw = yield* db.organizations.claws.create({
      userId: user.id,
      organizationId,
      data: {
        slug: payload.slug,
        displayName: payload.name,
        description: payload.description,
        weeklySpendingGuardrailCenticents:
          payload.weeklySpendingGuardrailCenticents,
        homeProjectId: payload.homeProjectId,
      },
    });

    // Track creation analytics in the fast path
    yield* analytics.trackEvent({
      name: "claw_created",
      properties: {
        clawId: claw.id,
        organizationId,
        userId: user.id,
      },
      distinctId: user.id,
    });

    // Run provisioning in the background so the response returns immediately.
    // We provide a fresh Database.Live layer because Hyperdrive connections
    // are tied to the request lifecycle and die after the response is sent.
    ctx.waitUntil(
      Effect.runPromise(
        provisionClawBackground(claw, {
          clawDeployment,
          settings,
        }).pipe(
          Effect.provide(
            Layer.mergeAll(
              Layer.succeed(Settings, settings),
              Database.Live({
                database: { connectionString: settings.databaseUrl },
                payments: settings.stripe,
              }),
            ),
          ),
        ),
      ).catch((err) => {
        console.error("[provisioning] Background task failed:", err);
      }),
    );

    return claw;
  });

export const getClawHandler = (organizationId: string, clawId: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.claws.findById({
      organizationId,
      clawId,
      userId: user.id,
    });
  });

export const updateClawHandler = (
  organizationId: string,
  clawId: string,
  payload: UpdateClawRequest,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.claws.update({
      organizationId,
      clawId,
      data: {
        displayName: payload.name,
        description: payload.description,
        weeklySpendingGuardrailCenticents:
          payload.weeklySpendingGuardrailCenticents,
      },
      userId: user.id,
    });
  });

export const deleteClawHandler = (organizationId: string, clawId: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    const analytics = yield* Analytics;
    const deployment = yield* ClawDeploymentService;

    // Deprovision infrastructure (R2 bucket, credentials, container)
    yield* deployment.deprovision(clawId);

    yield* db.organizations.claws.delete({
      organizationId,
      clawId,
      userId: user.id,
    });

    yield* analytics.trackEvent({
      name: "claw_deleted",
      properties: {
        clawId,
        organizationId,
        userId: user.id,
      },
      distinctId: user.id,
    });
  });

export const getClawUsageHandler = (organizationId: string, clawId: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.claws.getClawUsage({
      userId: user.id,
      organizationId,
      clawId,
    });
  });

export const getSecretsHandler = (organizationId: string, clawId: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.claws.getSecrets({
      userId: user.id,
      organizationId,
      clawId,
    });
  });

export const updateSecretsHandler = (
  organizationId: string,
  clawId: string,
  payload: Record<string, string>,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    return yield* db.organizations.claws.updateSecrets({
      userId: user.id,
      organizationId,
      clawId,
      secrets: payload,
    });
  });

export const restartClawHandler = (organizationId: string, clawId: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    const deployment = yield* ClawDeploymentService;

    // Restart is a write operation; use claw permission table (`update`).
    yield* db.organizations.claws.authorize({
      userId: user.id,
      organizationId,
      clawId,
      action: "update",
    });

    yield* deployment.restart(clawId);
    return;
  });
