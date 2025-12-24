import { Effect } from "effect";
import { InternalError } from "@/errors";

/**
 * Converts any error to an HTTP Response.
 */
function toErrorResponse(error: unknown): Response {
  const message =
    error instanceof Error
      ? error.message
      : typeof error === "object" && error !== null && "message" in error
        ? String((error as { message: unknown }).message)
        : "An error occurred";

  const status =
    typeof error === "object" &&
    error !== null &&
    error.constructor &&
    "status" in error.constructor
      ? (error.constructor as { status: number }).status
      : 500;

  const tag =
    typeof error === "object" && error !== null && "_tag" in error
      ? String((error as { _tag: unknown })._tag)
      : "InternalError";

  const resource =
    typeof error === "object" && error !== null && "resource" in error
      ? String((error as { resource: unknown }).resource)
      : undefined;

  return new Response(JSON.stringify({ tag, message, resource }), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

/**
 * Handles all errors, converting them to Response.
 */
export const handleErrors = <R>(
  effect: Effect.Effect<Response, unknown, R>,
): Effect.Effect<Response, never, R> =>
  effect.pipe(
    Effect.catchAll((error) => Effect.succeed(toErrorResponse(error))),
  );

/**
 * Handles defects by converting them to InternalError responses.
 */
export const handleDefects = (
  effect: Effect.Effect<Response, never, never>,
): Effect.Effect<Response, never, never> =>
  effect.pipe(
    Effect.catchAllDefect((defect) =>
      Effect.succeed(
        toErrorResponse(
          new InternalError({
            message:
              defect instanceof Error
                ? defect.message
                : "An unexpected error occurred",
            cause: defect,
          }),
        ),
      ),
    ),
  );
