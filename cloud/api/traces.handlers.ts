import { Effect } from "effect";
import { Database } from "@/db";
import {
  UnauthorizedError,
  NotFoundError,
  PermissionDeniedError,
  DatabaseError,
  AlreadyExistsError,
} from "@/errors";
import { requireApiKeyAuth } from "@/auth";
import {
  type CreateTraceRequest,
  type CreateTraceResponse,
} from "@/api/traces.schemas";

export * from "@/api/traces.schemas";

export const createTraceHandler = (
  payload: CreateTraceRequest,
): Effect.Effect<
  CreateTraceResponse,
  | UnauthorizedError
  | NotFoundError
  | PermissionDeniedError
  | DatabaseError
  | AlreadyExistsError,
  Database
> =>
  Effect.gen(function* () {
    const apiKeyInfo = yield* requireApiKeyAuth;
    const db = yield* Database;

    // Use the API key owner's userId for authorization
    const result = yield* db.traces.create({
      userId: apiKeyInfo.ownerId,
      organizationId: apiKeyInfo.organizationId,
      projectId: apiKeyInfo.projectId,
      environmentId: apiKeyInfo.environmentId,
      data: { resourceSpans: payload.resourceSpans },
    });

    const response: CreateTraceResponse = {
      partialSuccess:
        result.rejectedSpans > 0
          ? {
              rejectedSpans: result.rejectedSpans,
              errorMessage: `${result.rejectedSpans} spans were rejected due to errors`,
            }
          : {},
    };

    return response;
  });
