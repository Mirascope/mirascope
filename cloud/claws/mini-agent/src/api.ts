/**
 * HttpApi definition — all endpoints, request/response schemas, and security.
 */
import {
  HttpApi,
  HttpApiEndpoint,
  HttpApiGroup,
  HttpApiMiddleware,
  HttpApiSecurity,
} from "@effect/platform";
import { Schema } from "effect";

import {
  AuthError,
  CapacityError,
  InternalError,
  NotFoundError,
  ValidationError,
} from "./Errors.js";

// ─── Schemas ──────────────────────────────────────────────────────────────

export const HealthResponse = Schema.Struct({
  hostname: Schema.String,
  uptime: Schema.Number,
  cpu: Schema.Struct({
    usage: Schema.Number,
    cores: Schema.Number,
  }),
  memory: Schema.Struct({
    usedGb: Schema.Number,
    totalGb: Schema.Number,
  }),
  disk: Schema.Struct({
    usedGb: Schema.Number,
    totalGb: Schema.Number,
  }),
  loadAverage: Schema.Tuple(Schema.Number, Schema.Number, Schema.Number),
  claws: Schema.Struct({
    active: Schema.Number,
    max: Schema.Number,
  }),
  tunnel: Schema.Struct({
    status: Schema.Literal("connected"),
    routes: Schema.Number,
  }),
});

export const ClawListItem = Schema.Struct({
  macUsername: Schema.String,
  launchdStatus: Schema.Literal("loaded", "unloaded", "error"),
  memoryUsageMb: Schema.NullOr(Schema.Number),
  gatewayPid: Schema.NullOr(Schema.Number),
  gatewayUptime: Schema.NullOr(Schema.Number),
  chromiumPid: Schema.NullOr(Schema.Number),
  processCount: Schema.Number,
});

export const ClawListResponse = Schema.Struct({
  claws: Schema.Array(ClawListItem),
});

export const ProvisionRequestSchema = Schema.Struct({
  clawId: Schema.String,
  macUsername: Schema.String,
  localPort: Schema.Number,
  gatewayToken: Schema.String,
  tunnelHostname: Schema.String,
  envVars: Schema.optional(
    Schema.Record({ key: Schema.String, value: Schema.String }),
  ),
});

export const ProvisionResponseSchema = Schema.Struct({
  success: Schema.Boolean,
  macUsername: Schema.String,
  localPort: Schema.Number,
  tunnelRouteAdded: Schema.Boolean,
  error: Schema.optional(Schema.String),
});

export const ClawStatusResponse = Schema.Struct({
  macUsername: Schema.String,
  launchdStatus: Schema.Literal("loaded", "unloaded", "error"),
  diskMb: Schema.NullOr(Schema.Number),
  memoryUsageMb: Schema.NullOr(Schema.Number),
  gatewayPid: Schema.NullOr(Schema.Number),
  gatewayUptime: Schema.NullOr(Schema.Number),
  chromiumPid: Schema.NullOr(Schema.Number),
  processCount: Schema.Number,
});

export const RestartResponse = Schema.Struct({
  success: Schema.Literal(true),
  gatewayPid: Schema.NullOr(Schema.Number),
});

export const DeprovisionRequestSchema = Schema.Struct({
  archive: Schema.optional(Schema.Boolean),
});

export const DeprovisionResponseSchema = Schema.Struct({
  success: Schema.Boolean,
  archived: Schema.Boolean,
  error: Schema.optional(Schema.String),
});

export const BackupResponse = Schema.Struct({
  success: Schema.Literal(true),
  backupId: Schema.String,
});

// ─── Auth Middleware ─────────────────────────────────────────────────────

export class AuthMiddleware extends HttpApiMiddleware.Tag<AuthMiddleware>()(
  "MiniAgent/AuthMiddleware",
  {
    failure: AuthError,
    security: {
      bearer: HttpApiSecurity.bearer,
    },
  },
) {}

// ─── API Groups ─────────────────────────────────────────────────────────

export class HealthApi extends HttpApiGroup.make("health").add(
  HttpApiEndpoint.get("getHealth", "/health")
    .addSuccess(HealthResponse)
    .addError(InternalError, { status: 500 }),
) {}

export class ClawsApi extends HttpApiGroup.make("claws")
  .add(
    HttpApiEndpoint.get("listClaws", "/claws")
      .addSuccess(ClawListResponse)
      .addError(InternalError, { status: 500 }),
  )
  .add(
    HttpApiEndpoint.post("provision", "/claws")
      .setPayload(ProvisionRequestSchema)
      .addSuccess(ProvisionResponseSchema, { status: 201 })
      .addError(ValidationError, { status: 400 })
      .addError(CapacityError, { status: 503 })
      .addError(InternalError, { status: 500 }),
  )
  .add(
    HttpApiEndpoint.get("getClawStatus", "/claws/:clawUser/status")
      .setPath(Schema.Struct({ clawUser: Schema.String }))
      .addSuccess(ClawStatusResponse)
      .addError(NotFoundError, { status: 404 })
      .addError(InternalError, { status: 500 }),
  )
  .add(
    HttpApiEndpoint.post("restartClaw", "/claws/:clawUser/restart")
      .setPath(Schema.Struct({ clawUser: Schema.String }))
      .addSuccess(RestartResponse)
      .addError(NotFoundError, { status: 404 })
      .addError(InternalError, { status: 500 }),
  )
  .add(
    HttpApiEndpoint.del("deprovisionClaw", "/claws/:clawUser")
      .setPath(Schema.Struct({ clawUser: Schema.String }))
      .setPayload(DeprovisionRequestSchema)
      .addSuccess(DeprovisionResponseSchema)
      .addError(NotFoundError, { status: 404 })
      .addError(InternalError, { status: 500 }),
  )
  .add(
    HttpApiEndpoint.post("backupClaw", "/claws/:clawUser/backup")
      .setPath(Schema.Struct({ clawUser: Schema.String }))
      .addSuccess(BackupResponse, { status: 202 })
      .addError(NotFoundError, { status: 404 })
      .addError(InternalError, { status: 500 }),
  )
  .middleware(AuthMiddleware) {}

export class MiniAgentApi extends HttpApi.make("MiniAgentApi")
  .add(HealthApi)
  .add(ClawsApi) {}
