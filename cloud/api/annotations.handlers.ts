import { Effect } from "effect";
import { Database } from "@/db";
import {
  UnauthorizedError,
  NotFoundError,
  AlreadyExistsError,
  DatabaseError,
  PermissionDeniedError,
} from "@/errors";
import { requireApiKeyAuth } from "@/auth";
import type { PublicAnnotation as DbPublicAnnotation } from "@/db/schema/annotations";
import type {
  CreateAnnotationRequest,
  UpdateAnnotationRequest,
  AnnotationResponse,
  ListAnnotationsResponse,
  DeleteAnnotationResponse,
} from "@/api/annotations.schemas";

export * from "@/api/annotations.schemas";

const toAnnotationResponse = (ann: DbPublicAnnotation): AnnotationResponse => ({
  ...ann,
  createdAt: ann.createdAt?.toISOString() ?? null,
  updatedAt: ann.updatedAt?.toISOString() ?? null,
});

export const createAnnotationHandler = (
  payload: CreateAnnotationRequest,
): Effect.Effect<
  AnnotationResponse,
  | UnauthorizedError
  | NotFoundError
  | AlreadyExistsError
  | DatabaseError
  | PermissionDeniedError,
  Database
> =>
  Effect.gen(function* () {
    const apiKeyInfo = yield* requireApiKeyAuth;
    const db = yield* Database;

    const result = yield* db.annotations.create({
      userId: apiKeyInfo.ownerId,
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

export const getAnnotationHandler = (
  id: string,
): Effect.Effect<
  AnnotationResponse,
  UnauthorizedError | NotFoundError | DatabaseError | PermissionDeniedError,
  Database
> =>
  Effect.gen(function* () {
    const apiKeyInfo = yield* requireApiKeyAuth;
    const db = yield* Database;

    const result = yield* db.annotations.getById({
      userId: apiKeyInfo.ownerId,
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
): Effect.Effect<
  AnnotationResponse,
  UnauthorizedError | NotFoundError | DatabaseError | PermissionDeniedError,
  Database
> =>
  Effect.gen(function* () {
    const apiKeyInfo = yield* requireApiKeyAuth;
    const db = yield* Database;

    const result = yield* db.annotations.update({
      userId: apiKeyInfo.ownerId,
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

export const deleteAnnotationHandler = (
  id: string,
): Effect.Effect<
  DeleteAnnotationResponse,
  UnauthorizedError | NotFoundError | DatabaseError | PermissionDeniedError,
  Database
> =>
  Effect.gen(function* () {
    const apiKeyInfo = yield* requireApiKeyAuth;
    const db = yield* Database;

    yield* db.annotations.delete({
      userId: apiKeyInfo.ownerId,
      organizationId: apiKeyInfo.organizationId,
      projectId: apiKeyInfo.projectId,
      environmentId: apiKeyInfo.environmentId,
      annotationId: id,
    });
    return { success: true };
  });

export const listAnnotationsHandler = (params: {
  traceId?: string;
  spanId?: string;
  label?: string;
  limit?: number;
  offset?: number;
}): Effect.Effect<
  ListAnnotationsResponse,
  UnauthorizedError | NotFoundError | DatabaseError | PermissionDeniedError,
  Database
> =>
  Effect.gen(function* () {
    const apiKeyInfo = yield* requireApiKeyAuth;
    const db = yield* Database;

    const result = yield* db.annotations.list({
      userId: apiKeyInfo.ownerId,
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
