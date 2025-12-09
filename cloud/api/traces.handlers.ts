import { Effect } from "effect";
import { Database } from "@/db";
import { AuthenticatedUser, AuthenticatedApiKey } from "@/auth";
import type {
  CreateTraceRequest,
  CreateTraceResponse,
} from "@/api/traces.schemas";

export * from "@/api/traces.schemas";

export const createTraceHandler = (payload: CreateTraceRequest) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;
    const apiKeyInfo = yield* AuthenticatedApiKey;

    const result = yield* db.organizations.projects.environments.traces.create({
      userId: user.id,
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
