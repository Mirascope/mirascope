import { Effect } from "effect";
import { Database } from "@/db";
import { AuthenticatedUser, AuthenticatedApiKey } from "@/auth";
import type { PublicAnnotation as DbPublicAnnotation } from "@/db/schema/annotations";
import type {
  CreateAnnotationRequest,
  UpdateAnnotationRequest,
  AnnotationResponse,
} from "@/api/annotations.schemas";

export * from "@/api/annotations.schemas";

export const toAnnotationResponse = (
  ann: DbPublicAnnotation,
): AnnotationResponse => ({
  ...ann,
  createdAt: ann.createdAt?.toISOString() ?? null,
  updatedAt: ann.updatedAt?.toISOString() ?? null,
});

export const createAnnotationHandler = (payload: CreateAnnotationRequest) =>
  Effect.gen(function* () {
    const user = yield* AuthenticatedUser;
    const apiKeyInfo = yield* AuthenticatedApiKey;
    const db = yield* Database;

    const result =
      yield* db.organizations.projects.environments.annotations.create({
        userId: user.id,
        organizationId: apiKeyInfo.organizationId,
        projectId: apiKeyInfo.projectId,
        environmentId: apiKeyInfo.environmentId,
        data: {
          spanId: payload.spanId,
          traceId: payload.traceId,
          label: payload.label ?? null,
          reasoning: payload.reasoning ?? null,
          data: payload.data ?? null,
        },
      });

    return toAnnotationResponse(result);
  });

export const getAnnotationHandler = (id: string) =>
  Effect.gen(function* () {
    const user = yield* AuthenticatedUser;
    const apiKeyInfo = yield* AuthenticatedApiKey;
    const db = yield* Database;

    const result =
      yield* db.organizations.projects.environments.annotations.getById({
        userId: user.id,
        organizationId: apiKeyInfo.organizationId,
        projectId: apiKeyInfo.projectId,
        environmentId: apiKeyInfo.environmentId,
        annotationId: id,
      });
    return toAnnotationResponse(result);
  });

export const updateAnnotationHandler = (
  id: string,
  payload: UpdateAnnotationRequest,
) =>
  Effect.gen(function* () {
    const user = yield* AuthenticatedUser;
    const apiKeyInfo = yield* AuthenticatedApiKey;
    const db = yield* Database;

    const result =
      yield* db.organizations.projects.environments.annotations.update({
        userId: user.id,
        organizationId: apiKeyInfo.organizationId,
        projectId: apiKeyInfo.projectId,
        environmentId: apiKeyInfo.environmentId,
        annotationId: id,
        data: {
          label: payload.label,
          reasoning: payload.reasoning,
          data: payload.data,
        },
      });

    return toAnnotationResponse(result);
  });

export const deleteAnnotationHandler = (id: string) =>
  Effect.gen(function* () {
    const user = yield* AuthenticatedUser;
    const apiKeyInfo = yield* AuthenticatedApiKey;
    const db = yield* Database;

    yield* db.organizations.projects.environments.annotations.delete({
      userId: user.id,
      organizationId: apiKeyInfo.organizationId,
      projectId: apiKeyInfo.projectId,
      environmentId: apiKeyInfo.environmentId,
      annotationId: id,
    });
  });

export const listAnnotationsHandler = (params: {
  traceId?: string;
  spanId?: string;
  label?: string;
  limit?: number;
  offset?: number;
}) =>
  Effect.gen(function* () {
    const user = yield* AuthenticatedUser;
    const apiKeyInfo = yield* AuthenticatedApiKey;
    const db = yield* Database;

    const result =
      yield* db.organizations.projects.environments.annotations.list({
        userId: user.id,
        organizationId: apiKeyInfo.organizationId,
        projectId: apiKeyInfo.projectId,
        environmentId: apiKeyInfo.environmentId,
        filters: {
          traceId: params.traceId,
          spanId: params.spanId,
          label: params.label,
          limit: params.limit,
          offset: params.offset,
        },
      });

    return {
      annotations: result.annotations.map(toAnnotationResponse),
      total: result.total,
    };
  });
