// PostgreSQL error code for unique constraint violation
const PG_UNIQUE_VIOLATION = "23505";

/**
 * Check if an error is a PostgreSQL unique constraint violation.
 * Drizzle wraps PostgreSQL errors, so we check both the error itself
 * and its cause for the unique violation code.
 */
export function isUniqueConstraintError(error: unknown): boolean {
  if (typeof error !== "object" || error === null) {
    return false;
  }

  // Check if error.code matches (direct postgres error)
  if ("code" in error && error.code === PG_UNIQUE_VIOLATION) {
    return true;
  }

  // Check if error.cause.code matches (Drizzle-wrapped error)
  if (
    "cause" in error &&
    typeof error.cause === "object" &&
    error.cause !== null &&
    "code" in error.cause &&
    error.cause.code === PG_UNIQUE_VIOLATION
  ) {
    return true;
  }

  return false;
}
