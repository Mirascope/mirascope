/**
 * @fileoverview Internal SDK exports.
 *
 * Currently private — consumed by CLI commands only.
 * Future: promote to public `mirascope/claws` export.
 */

// Services
export { AuthService } from "./auth/service.js";
export { MirascopeHttp } from "./http/client.js";
export { ClawApi } from "./claw/service.js";

// Schemas
export type { Claw, ClawDetail, CreateClawParams } from "./claw/schemas.js";
export {
  Claw as ClawSchema,
  ClawDetail as ClawDetailSchema,
} from "./claw/schemas.js";

// Errors
export {
  ApiError,
  NotFoundError,
  AuthError,
  ValidationError,
} from "./errors.js";

// Auth config
export { readCredentials, writeCredentials } from "./auth/config.js";
