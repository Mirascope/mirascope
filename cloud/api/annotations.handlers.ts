import { Effect } from "effect";
import { Database } from "@/db";
import { Authentication } from "@/auth";
import type { PublicAnnotation } from "@/db/schema/annotations";
import type {
  CreateAnnotationRequest,
  UpdateAnnotationRequest,
} from "@/api/annotations.schemas";

export * from "@/api/annotations.schemas";

export const toAnnotation = (annotation: PublicAnnotation) => {
  return {
    ...annotation,
    tags: annotation.tags ?? [],
    spanId: annotation.otelSpanId,
    traceId: annotation.otelTraceId,
    createdAt: annotation.createdAt?.toISOString() ?? null,
    updatedAt: annotation.updatedAt?.toISOString() ?? null,
  };
};

/**
 * Handler for listing annotations with optional filters.
 * Returns annotations for the authenticated environment.
 */
export const listAnnotationsHandler = (params: {
  otelTraceId?: string;
  otelSpanId?: string;
  label?: "pass" | "fail";
  limit?: number;
  offset?: number;
}) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const { user, apiKeyInfo } = yield* Authentication.ApiKey;

    const results =
      yield* db.organizations.projects.environments.traces.annotations.findAll({
        userId: user.id,
        organizationId: apiKeyInfo.organizationId,
        projectId: apiKeyInfo.projectId,
        environmentId: apiKeyInfo.environmentId,
        filters: {
          otelTraceId: params.otelTraceId,
          otelSpanId: params.otelSpanId,
          label: params.label,
          limit: params.limit,
          offset: params.offset,
        },
      });

    return {
      annotations: results.map(toAnnotation),
      total: results.length,
    };
  });

/**
 * Handler for creating a new annotation.
 * Associates an annotation with a span in the authenticated environment.
 */
export const createAnnotationHandler = (payload: CreateAnnotationRequest) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const { user, apiKeyInfo } = yield* Authentication.ApiKey;

    const tags =
      payload.tags === null ? null : payload.tags ? [...payload.tags] : null;

    const result =
      yield* db.organizations.projects.environments.traces.annotations.create({
        userId: user.id,
        organizationId: apiKeyInfo.organizationId,
        projectId: apiKeyInfo.projectId,
        environmentId: apiKeyInfo.environmentId,
        data: {
          otelSpanId: payload.otelSpanId,
          otelTraceId: payload.otelTraceId,
          label: payload.label ?? null,
          reasoning: payload.reasoning ?? null,
          metadata: payload.metadata ?? null,
          tags,
        },
      });

    return toAnnotation(result);
  });

/**
 * Handler for retrieving an annotation by ID.
 * Returns the annotation if found in the authenticated environment.
 */
export const getAnnotationHandler = (id: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const { user, apiKeyInfo } = yield* Authentication.ApiKey;

    const result =
      yield* db.organizations.projects.environments.traces.annotations.findById(
        {
          userId: user.id,
          organizationId: apiKeyInfo.organizationId,
          projectId: apiKeyInfo.projectId,
          environmentId: apiKeyInfo.environmentId,
          annotationId: id,
        },
      );

    return toAnnotation(result);
  });

/**
 * Handler for updating an existing annotation.
 * Updates the annotation fields in the authenticated environment.
 */
export const updateAnnotationHandler = (
  id: string,
  payload: UpdateAnnotationRequest,
) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const { user, apiKeyInfo } = yield* Authentication.ApiKey;

    const tags =
      payload.tags === null
        ? null
        : payload.tags
          ? [...payload.tags]
          : undefined;

    const result =
      yield* db.organizations.projects.environments.traces.annotations.update({
        userId: user.id,
        organizationId: apiKeyInfo.organizationId,
        projectId: apiKeyInfo.projectId,
        environmentId: apiKeyInfo.environmentId,
        annotationId: id,
        data: {
          label: payload.label,
          reasoning: payload.reasoning,
          metadata: payload.metadata,
          tags,
        },
      });

    return toAnnotation(result);
  });

/**
 * Handler for deleting an annotation.
 * Removes the annotation from the authenticated environment.
 */
export const deleteAnnotationHandler = (id: string) =>
  Effect.gen(function* () {
    const db = yield* Database;
    const { user, apiKeyInfo } = yield* Authentication.ApiKey;

    yield* db.organizations.projects.environments.traces.annotations.delete({
      userId: user.id,
      organizationId: apiKeyInfo.organizationId,
      projectId: apiKeyInfo.projectId,
      environmentId: apiKeyInfo.environmentId,
      annotationId: id,
    });
  });
