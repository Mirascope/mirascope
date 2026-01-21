import type { Cause } from "effect";

/**
 * Type for the EffectQueryFailure wrapper from effect-query library.
 *
 * When an Effect fails, effect-query wraps it in this structure:
 * - `_tag`: Always "EffectQueryFailure"
 * - `failure`: The actual error object (e.g., PlanLimitExceededError)
 * - `failureCause`: The full Effect Cause for debugging
 */
export interface EffectQueryFailure<E = unknown> {
  _tag: "EffectQueryFailure";
  failure: E;
  failureCause: Cause.Cause<E>;
  match: <R>(
    matcher: Record<string, (e: E) => R> & {
      OrElse: (cause: Cause.Cause<E>) => R;
    },
  ) => R;
}

/**
 * Type guard to check if an error is an EffectQueryFailure.
 */
export function isEffectQueryFailure(
  error: unknown,
): error is EffectQueryFailure {
  return (
    typeof error === "object" &&
    error !== null &&
    "_tag" in error &&
    (error as { _tag: string })._tag === "EffectQueryFailure"
  );
}

/**
 * Get the failure tag from an effect-query error.
 *
 * @example
 * if (getFailureTag(err) === "PlanLimitExceededError") {
 *   // Handle plan limit error
 * }
 */
export function getFailureTag(error: unknown): string | undefined {
  if (
    isEffectQueryFailure(error) &&
    error.failure &&
    typeof error.failure === "object"
  ) {
    return (error.failure as { _tag?: string })._tag;
  }
  return undefined;
}

/**
 * Get the failure object from an effect-query error.
 *
 * @example
 * const failure = getFailure<PlanLimitExceededError>(err);
 * if (failure) {
 *   console.log(failure.limit, failure.currentUsage);
 * }
 */
export function getFailure<T>(error: unknown): T | undefined {
  if (isEffectQueryFailure(error)) {
    return error.failure as T;
  }
  return undefined;
}

/**
 * Get a user-friendly error message from an effect-query error.
 *
 * Extracts the `message` property from the nested failure object.
 * Falls back to the provided default message if extraction fails.
 *
 * @example
 * catch (err: unknown) {
 *   setError(getErrorMessage(err, "Failed to create project"));
 * }
 */
export function getErrorMessage(error: unknown, fallback: string): string {
  if (isEffectQueryFailure(error) && error.failure) {
    const failure = error.failure as { message?: string };
    if (typeof failure.message === "string") {
      return failure.message;
    }
  }
  return fallback;
}
