import { Effect } from "effect";
import { Database } from "@/db";
import { AuthenticatedUser } from "@/auth";
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

export const createAnnotationHandler = (
  organizationId: string,
  projectId: string,
  environmentId: string,
  payload: CreateAnnotationRequest,
) =>
  Effect.gen(function* () {
    const user = yield* AuthenticatedUser;
    const db = yield* Database;

    const result =
      yield* db.organizations.projects.environments.annotations.create({
        userId: user.id,
        organizationId,
        projectId,
        environmentId,
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
  organizationId: string,
  projectId: string,
  environmentId: string,
  id: string,
) =>
  Effect.gen(function* () {
    const user = yield* AuthenticatedUser;
    const db = yield* Database;

    const result =
      yield* db.organizations.projects.environments.annotations.getById({
        userId: user.id,
        organizationId,
        projectId,
        environmentId,
        annotationId: id,
      });
    return toAnnotationResponse(result);
  });

export const updateAnnotationHandler = (
  organizationId: string,
  projectId: string,
  environmentId: string,
  id: string,
  payload: UpdateAnnotationRequest,
) =>
  Effect.gen(function* () {
    const user = yield* AuthenticatedUser;
    const db = yield* Database;

    const result =
      yield* db.organizations.projects.environments.annotations.update({
        userId: user.id,
        organizationId,
        projectId,
        environmentId,
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
  organizationId: string,
  projectId: string,
  environmentId: string,
  id: string,
) =>
  Effect.gen(function* () {
    const user = yield* AuthenticatedUser;
    const db = yield* Database;

    yield* db.organizations.projects.environments.annotations.delete({
      userId: user.id,
      organizationId,
      projectId,
      environmentId,
      annotationId: id,
    });
  });

export const listAnnotationsHandler = (
  organizationId: string,
  projectId: string,
  environmentId: string,
  params: {
    traceId?: string;
    spanId?: string;
    label?: string;
    limit?: number;
    offset?: number;
  },
) =>
  Effect.gen(function* () {
    const user = yield* AuthenticatedUser;
    const db = yield* Database;

    const result =
      yield* db.organizations.projects.environments.annotations.list({
        userId: user.id,
        organizationId,
        projectId,
        environmentId,
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
