/**
 * Internal handlers for the dispatch worker API.
 *
 * WARNING: These handlers are NOT part of the public HTTP API. They must NOT
 * be wired into the public router (router.ts) or registered in
 * MirascopeCloudApi. The dispatch worker calls these via Cloudflare service
 * binding (in-process RPC, never hits the public internet).
 *
 * The bootstrap handler returns SECURITY-SENSITIVE data (R2 credentials,
 * API keys, integration tokens). The service binding is the only auth
 * boundary — there is no token or network-level isolation beyond it.
 */
import { and, eq } from "drizzle-orm";
import { Effect } from "effect";
import { Schema } from "effect";

import { DrizzleORM } from "@/db/client";
import { claws, organizations } from "@/db/schema";
import { DatabaseError, NotFoundError } from "@/errors";

// ---------------------------------------------------------------------------
// Schemas
// ---------------------------------------------------------------------------

export const ClawResolveResponseSchema = Schema.Struct({
  clawId: Schema.String,
  organizationId: Schema.String,
});

export type ClawResolveResponse = typeof ClawResolveResponseSchema.Type;

const ClawR2ConfigSchema = Schema.Struct({
  bucketName: Schema.String,
  accessKeyId: Schema.String,
  secretAccessKey: Schema.String,
});

export const OpenClawConfigSchema = Schema.Struct({
  clawId: Schema.String,
  clawSlug: Schema.String,
  organizationId: Schema.String,
  organizationSlug: Schema.String,
  instanceType: Schema.String,
  r2: ClawR2ConfigSchema,
  containerEnv: Schema.Record({
    key: Schema.String,
    value: Schema.Union(Schema.String, Schema.Undefined),
  }),
});

export type OpenClawConfigResponse = typeof OpenClawConfigSchema.Type;

export const ClawStatusReportSchema = Schema.Struct({
  status: Schema.Literal(
    "pending",
    "provisioning",
    "active",
    "paused",
    "error",
  ),
  errorMessage: Schema.optional(Schema.NullOr(Schema.String)),
  startedAt: Schema.optional(Schema.NullOr(Schema.String)),
});

export type ClawStatusReport = typeof ClawStatusReportSchema.Type;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Decrypt secretsEncrypted from the DB.
 *
 * TODO: Implement real AES-256-GCM decryption using Web Crypto API.
 * For now, secretsEncrypted is treated as plain JSON.
 */
export function decryptSecrets(
  secretsEncrypted: string | null,
): Record<string, string | undefined> {
  if (!secretsEncrypted) return {};
  try {
    return JSON.parse(secretsEncrypted) as Record<string, string | undefined>;
  } catch {
    return {};
  }
}

// ---------------------------------------------------------------------------
// Handlers
// ---------------------------------------------------------------------------

/**
 * Resolve org/claw slugs to a stable clawId.
 *
 * The dispatch worker extracts slugs from the incoming hostname
 * ({clawSlug}.{orgSlug}.mirascope.com) and calls this to get the clawId
 * used as the Durable Object key. Results are LRU-cached by the worker.
 */
export const resolveClawHandler = (
  orgSlug: string,
  clawSlug: string,
): Effect.Effect<
  ClawResolveResponse,
  NotFoundError | DatabaseError,
  DrizzleORM
> =>
  Effect.gen(function* () {
    const client = yield* DrizzleORM;

    const [claw] = yield* client
      .select({
        clawId: claws.id,
        organizationId: claws.organizationId,
      })
      .from(claws)
      .innerJoin(organizations, eq(claws.organizationId, organizations.id))
      .where(and(eq(organizations.slug, orgSlug), eq(claws.slug, clawSlug)))
      .limit(1)
      .pipe(
        Effect.mapError(
          (e) =>
            new DatabaseError({
              message: "Failed to resolve claw",
              cause: e,
            }),
        ),
      );

    if (!claw) {
      return yield* Effect.fail(
        new NotFoundError({
          message: `Claw ${clawSlug} not found in organization ${orgSlug}`,
          resource: "claw",
        }),
      );
    }

    return claw;
  });

/**
 * Return the full OpenClawConfig for a given clawId.
 *
 * Called by the dispatch worker on cold start to get R2 credentials,
 * container env vars, and instance type. The implementation must decrypt
 * secretsEncrypted from the DB before including them in the response.
 *
 * SECURITY-SENSITIVE — the response contains R2 scoped credentials
 * (accessKeyId, secretAccessKey) and container env vars (API keys,
 * integration tokens).
 */
export const bootstrapClawHandler = (
  clawId: string,
): Effect.Effect<
  OpenClawConfigResponse,
  NotFoundError | DatabaseError,
  DrizzleORM
> =>
  Effect.gen(function* () {
    const client = yield* DrizzleORM;

    const [claw] = yield* client
      .select({
        clawId: claws.id,
        clawSlug: claws.slug,
        organizationId: claws.organizationId,
        organizationSlug: organizations.slug,
        instanceType: claws.instanceType,
        bucketName: claws.bucketName,
        secretsEncrypted: claws.secretsEncrypted,
      })
      .from(claws)
      .innerJoin(organizations, eq(claws.organizationId, organizations.id))
      .where(eq(claws.id, clawId))
      .limit(1)
      .pipe(
        Effect.mapError(
          (e) =>
            new DatabaseError({
              message: "Failed to fetch claw for bootstrap",
              cause: e,
            }),
        ),
      );

    if (!claw) {
      return yield* Effect.fail(
        new NotFoundError({
          message: `Claw ${clawId} not found`,
          resource: "claw",
        }),
      );
    }

    const secrets = decryptSecrets(claw.secretsEncrypted);

    return {
      clawId: claw.clawId,
      clawSlug: claw.clawSlug,
      organizationId: claw.organizationId,
      organizationSlug: claw.organizationSlug,
      instanceType: claw.instanceType,
      r2: {
        bucketName: claw.bucketName ?? "",
        accessKeyId: (secrets.R2_ACCESS_KEY_ID as string) ?? "",
        secretAccessKey: (secrets.R2_SECRET_ACCESS_KEY as string) ?? "",
      },
      containerEnv: secrets,
    } satisfies OpenClawConfigResponse;
  });

/**
 * Accept a status report from the dispatch worker.
 *
 * Updates the claw's status in the DB (e.g. "active", "error")
 * along with optional error message and startedAt timestamp.
 */
export const reportClawStatusHandler = (
  clawId: string,
  payload: ClawStatusReport,
): Effect.Effect<void, NotFoundError | DatabaseError, DrizzleORM> =>
  Effect.gen(function* () {
    const client = yield* DrizzleORM;

    const [updated] = yield* client
      .update(claws)
      .set({
        status: payload.status,
        lastError: payload.errorMessage ?? null,
        lastDeployedAt: payload.startedAt
          ? new Date(payload.startedAt)
          : undefined,
        updatedAt: new Date(),
      })
      .where(eq(claws.id, clawId))
      .returning({ id: claws.id })
      .pipe(
        Effect.mapError(
          (e) =>
            new DatabaseError({
              message: "Failed to update claw status",
              cause: e,
            }),
        ),
      );

    if (!updated) {
      return yield* Effect.fail(
        new NotFoundError({
          message: `Claw ${clawId} not found`,
          resource: "claw",
        }),
      );
    }
  });
