/**
 * SDK Flat API Schemas
 *
 * These endpoints provide flat paths for SDK usage with API key authentication.
 * The organizationId, projectId, and environmentId are derived from the API key.
 */
import { HttpApiEndpoint, HttpApiGroup } from "@effect/platform";
import {
  NotFoundError,
  PermissionDeniedError,
  DatabaseError,
  AlreadyExistsError,
  UnauthorizedError,
} from "@/errors";
import {
  CreateTraceRequestSchema,
  CreateTraceResponseSchema,
} from "@/api/traces.schemas";

// Re-export request/response types from traces module
export {
  CreateTraceRequestSchema,
  CreateTraceResponseSchema,
  type CreateTraceRequest,
  type CreateTraceResponse,
} from "@/api/traces.schemas";

/**
 * SDK Traces API - Flat paths for SDK usage
 */
export class SdkTracesApi extends HttpApiGroup.make("sdkTraces").add(
  HttpApiEndpoint.post("create", "/traces")
    .setPayload(CreateTraceRequestSchema)
    .addSuccess(CreateTraceResponseSchema)
    .addError(UnauthorizedError, { status: UnauthorizedError.status })
    .addError(NotFoundError, { status: NotFoundError.status })
    .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
    .addError(DatabaseError, { status: DatabaseError.status })
    .addError(AlreadyExistsError, { status: AlreadyExistsError.status }),
) {}
