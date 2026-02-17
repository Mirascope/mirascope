/**
 * HttpApi definition — all endpoints, schemas, and error types.
 */
import {
  HttpApi,
  HttpApiEndpoint,
  HttpApiGroup,
  HttpApiMiddleware,
  HttpApiSecurity,
} from "@effect/platform";
import { Schema } from "effect";

// ─── Schemas ───────────────────────────────────────────────

export class ProvisionRequestBody extends Schema.Class<ProvisionRequestBody>(
  "ProvisionRequestBody",
)({
  clawId: Schema.String,
  macUsername: Schema.String.pipe(Schema.pattern(/^claw-[a-z0-9]+$/)),
  localPort: Schema.Number.pipe(Schema.int()),
  gatewayToken: Schema.String,
  tunnelHostname: Schema.String,
  envVars: Schema.optional(
    Schema.Record({ key: Schema.String, value: Schema.String }),
  ).pipe(Schema.withConstructorDefault(() => ({}))),
}) {}

export class DeprovisionRequestBody extends Schema.Class<DeprovisionRequestBody>(
  "DeprovisionRequestBody",
)({
  archive: Schema.optional(Schema.Boolean),
}) {}

export class ProvisionResponseSchema extends Schema.Class<ProvisionResponseSchema>(
  "ProvisionResponse",
)({
  success: Schema.Boolean,
  macUsername: Schema.String,
  localPort: Schema.Number,
  tunnelRouteAdded: Schema.Boolean,
  error: Schema.optional(Schema.String),
}) {}

export class DeprovisionResponseSchema extends Schema.Class<DeprovisionResponseSchema>(
  "DeprovisionResponse",
)({
  success: Schema.Boolean,
  archived: Schema.Boolean,
  error: Schema.optional(Schema.String),
}) {}

export class ClawStatusSchema extends Schema.Class<ClawStatusSchema>(
  "ClawStatus",
)({
  macUsername: Schema.String,
  launchdStatus: Schema.Literal("loaded", "unloaded", "error"),
  memoryUsageMb: Schema.NullOr(Schema.Number),
  gatewayPid: Schema.NullOr(Schema.Number),
  gatewayUptime: Schema.NullOr(Schema.Number),
  chromiumPid: Schema.NullOr(Schema.Number),
  processCount: Schema.Number,
  diskMb: Schema.optional(Schema.NullOr(Schema.Number)),
}) {}

export class ClawListResponse extends Schema.Class<ClawListResponse>(
  "ClawListResponse",
)({
  claws: Schema.Array(ClawStatusSchema),
}) {}

export class RestartResponse extends Schema.Class<RestartResponse>(
  "RestartResponse",
)({
  success: Schema.Boolean,
  gatewayPid: Schema.NullOr(Schema.Number),
}) {}

export class BackupResponse extends Schema.Class<BackupResponse>(
  "BackupResponse",
)({
  success: Schema.Boolean,
  backupId: Schema.String,
}) {}

export class HealthResponse extends Schema.Class<HealthResponse>(
  "HealthResponse",
)({
  hostname: Schema.String,
  uptime: Schema.Number,
  cpu: Schema.Struct({ usage: Schema.Number, cores: Schema.Number }),
  memory: Schema.Struct({ usedGb: Schema.Number, totalGb: Schema.Number }),
  disk: Schema.Struct({ usedGb: Schema.Number, totalGb: Schema.Number }),
  loadAverage: Schema.Tuple(Schema.Number, Schema.Number, Schema.Number),
  claws: Schema.Struct({ active: Schema.Number, max: Schema.Number }),
  tunnel: Schema.Struct({
    status: Schema.Literal("connected"),
    routes: Schema.Number,
  }),
}) {}

export class ErrorResponse extends Schema.Class<ErrorResponse>(
  "ErrorResponse",
)({
  error: Schema.String,
  details: Schema.optional(Schema.String),
}) {}

export const ClawUserPath = Schema.Struct({
  clawUser: Schema.String,
});

// ─── Security ──────────────────────────────────────────────

export const BearerSecurity = HttpApiSecurity.bearer;

export class AuthMiddleware extends HttpApiMiddleware.Tag<AuthMiddleware>()(
  "AuthMiddleware",
  {
    failure: Schema.Struct({ error: Schema.String }),
    security: { bearer: BearerSecurity },
  },
) {}

// ─── API Groups ────────────────────────────────────────────

export class HealthGroup extends HttpApiGroup.make("health").add(
  HttpApiEndpoint.get("getHealth", "/health")
    .addSuccess(HealthResponse)
    .addError(ErrorResponse, { status: 500 }),
) {}

export class ClawsGroup extends HttpApiGroup
  .make("claws")
  .add(
    HttpApiEndpoint.post("provision", "/claws")
      .setPayload(ProvisionRequestBody)
      .addSuccess(ProvisionResponseSchema, { status: 201 })
      .addError(ErrorResponse, { status: 400 })
      .addError(ErrorResponse, { status: 503 })
      .addError(ErrorResponse, { status: 500 }),
  )
  .add(
    HttpApiEndpoint.get("listClaws", "/claws")
      .addSuccess(ClawListResponse)
      .addError(ErrorResponse, { status: 500 }),
  )
  .add(
    HttpApiEndpoint.get("getClawStatus", "/claws/:clawUser/status")
      .setPath(ClawUserPath)
      .addSuccess(ClawStatusSchema)
      .addError(ErrorResponse, { status: 404 })
      .addError(ErrorResponse, { status: 500 }),
  )
  .add(
    HttpApiEndpoint.post("restartClaw", "/claws/:clawUser/restart")
      .setPath(ClawUserPath)
      .addSuccess(RestartResponse)
      .addError(ErrorResponse, { status: 404 })
      .addError(ErrorResponse, { status: 500 }),
  )
  .add(
    HttpApiEndpoint.del("deprovisionClaw", "/claws/:clawUser")
      .setPath(ClawUserPath)
      .addSuccess(DeprovisionResponseSchema)
      .addError(ErrorResponse, { status: 404 })
      .addError(ErrorResponse, { status: 500 }),
  )
  .add(
    HttpApiEndpoint.post("backupClaw", "/claws/:clawUser/backup")
      .setPath(ClawUserPath)
      .addSuccess(BackupResponse, { status: 202 })
      .addError(ErrorResponse, { status: 404 })
      .addError(ErrorResponse, { status: 500 }),
  )
  .middleware(AuthMiddleware) {}

// ─── Top-level API ─────────────────────────────────────────

export class MiniAgentApi extends HttpApi.make("MiniAgentApi")
  .add(HealthGroup)
  .add(ClawsGroup) {}
