import { Effect } from "effect";
import { Database } from "@/db";
import { AuthenticatedUser } from "@/auth";
import type {
  CreateTraceRequest,
  CreateTraceResponse,
} from "@/api/traces.schemas";

export * from "@/api/traces.schemas";

export const createTraceHandler = (
  organizationId: string,
  projectId: string,
  environmentId: string,
  payload: CreateTraceRequest,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const user = yield* AuthenticatedUser;

    const result = yield* db.organizations.projects.environments.traces.create({
      userId: user.id,
      organizationId,
      projectId,
      environmentId,
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
