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
import { Effect } from "effect";
import { Schema } from "effect";

import { NotFoundError } from "@/errors";

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
// Handlers — TODO implementations
// ---------------------------------------------------------------------------

/**
 * Resolve org/claw slugs to a stable clawId.
 *
 * The dispatch worker extracts slugs from the incoming hostname
 * ({clawSlug}.{orgSlug}.mirascope.com) and calls this to get the clawId
 * used as the Durable Object key. Results are LRU-cached by the worker.
 */
export const resolveClawHandler = (
  _orgSlug: string,
  _clawSlug: string,
): Effect.Effect<ClawResolveResponse, NotFoundError> =>
  Effect.fail(new NotFoundError({ message: "resolve: not yet implemented" }));

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
  _clawId: string,
): Effect.Effect<OpenClawConfigResponse, NotFoundError> =>
  Effect.fail(new NotFoundError({ message: "bootstrap: not yet implemented" }));

/**
 * Accept a status report from the dispatch worker.
 *
 * Updates the claw's status in the DB (e.g. "active", "error")
 * along with optional error message and startedAt timestamp.
 */
export const reportClawStatusHandler = (
  _clawId: string,
  _payload: ClawStatusReport,
): Effect.Effect<void, NotFoundError> =>
  Effect.fail(
    new NotFoundError({ message: "reportStatus: not yet implemented" }),
  );
