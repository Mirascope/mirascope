import { Effect } from "effect";
import { HttpServerRequest } from "@effect/platform";
import { Database } from "@/db";
import { UnauthorizedError, NotFoundError, DatabaseError } from "@/errors";
import { authenticateWithApiKey } from "@/auth/api-key";
import {
  type CreateTraceRequest,
  type CreateTraceResponse,
} from "@/api/traces.schemas";

export * from "@/api/traces.schemas";

export const createTraceHandler = (
  payload: CreateTraceRequest,
): Effect.Effect<
  CreateTraceResponse,
  UnauthorizedError | NotFoundError | DatabaseError,
  Database | HttpServerRequest.HttpServerRequest
> =>
  Effect.gen(function* () {
    const request = yield* HttpServerRequest.HttpServerRequest;
    const webRequest = request.source as Request;

    const apiKeyInfo = yield* authenticateWithApiKey(webRequest);

    if (!apiKeyInfo) {
      return yield* Effect.fail(
        new UnauthorizedError({
          message:
            "API key required. Provide X-API-Key header or Bearer token.",
        }),
      );
    }

    const db = yield* Database;

    const context = yield* db.traces.getEnvironmentContext(
      apiKeyInfo.environmentId,
    );

    const result = yield* db.traces.ingest(payload.resourceSpans, context);

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
