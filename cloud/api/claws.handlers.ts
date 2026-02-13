import * as crypto from "crypto";
import { eq } from "drizzle-orm";
import { Effect } from "effect";

import type { CreateClawRequest, UpdateClawRequest } from "@/api/claws.schemas";

import { Analytics } from "@/analytics";
import { AuthenticatedUser } from "@/auth";
import { encryptSecrets } from "@/claws/crypto";
import { ClawDeploymentService } from "@/claws/deployment/service";
import { DrizzleORM } from "@/db/client";
import { Database } from "@/db/database";
import { claws } from "@/db/schema";
import { DatabaseError } from "@/errors";
import { Settings } from "@/settings";

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

export const createClawHandler = (
  organizationId: string,
  payload: CreateClawRequest,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    const analytics = yield* Analytics;
    const clawDeployment = yield* ClawDeploymentService;
    const drizzle = yield* DrizzleORM;
    const settings = yield* Settings;

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

    // Provision R2 bucket and scoped credentials
    const status = yield* clawDeployment.provision({
      clawId: claw.id,
      instanceType: claw.instanceType,
    });

    // Generate gateway token for container auth
    const gatewayToken = crypto.randomUUID();

    // Build Mirascope Router base URL for Anthropic-compatible proxy
    const routerBaseUrl = `${settings.siteUrl}/router/v2/anthropic`;

    // Derive the primary model from the request (defaults to haiku for free tier)
    const primaryModel = payload.model ?? "claude-haiku-4-5";

    // Encrypt all container secrets before persisting
    const encrypted = yield* encryptSecrets({
      ANTHROPIC_API_KEY: claw.plaintextApiKey,
      ANTHROPIC_BASE_URL: routerBaseUrl,
      OPENCLAW_GATEWAY_TOKEN: gatewayToken,
      OPENCLAW_PRIMARY_MODEL: `anthropic/${primaryModel}`,
      OPENCLAW_SITE_URL: settings.siteUrl,
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
    yield* clawDeployment.warmUp(claw.id);

    yield* analytics.trackEvent({
      name: "claw_created",
      properties: {
        clawId: claw.id,
        organizationId,
        userId: user.id,
      },
      distinctId: user.id,
    });

    return {
      ...claw,
      status: "provisioning" as const,
      bucketName: status.bucketName ?? null,
      secretsEncrypted: encrypted.ciphertext,
    };
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
