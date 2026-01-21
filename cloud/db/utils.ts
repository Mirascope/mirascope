// PostgreSQL error codes
const PG_UNIQUE_VIOLATION = "23505";
const PG_CHECK_VIOLATION = "23514";
const PG_FOREIGN_KEY_VIOLATION = "23503";

/**
 * Helper to extract PostgreSQL error code from Drizzle-wrapped errors.
 */
function getPostgresErrorCode(error: unknown): string | undefined {
  if (typeof error !== "object" || error === null) {
    return undefined;
  }

  // Check direct error.code
  if ("code" in error && typeof error.code === "string") {
    return error.code;
  }

  // Check error.cause.code (Drizzle-wrapped error)
  if (
    "cause" in error &&
    typeof error.cause === "object" &&
    error.cause !== null &&
    "code" in error.cause &&
    typeof error.cause.code === "string"
  ) {
    return error.cause.code;
  }

  return undefined;
}

/**
 * Check if an error is a PostgreSQL unique constraint violation.
 */
export function isUniqueConstraintError(error: unknown): boolean {
  return getPostgresErrorCode(error) === PG_UNIQUE_VIOLATION;
}

/**
 * Check if an error is a PostgreSQL check constraint violation.
 */
export function isCheckConstraintError(error: unknown): boolean {
  return getPostgresErrorCode(error) === PG_CHECK_VIOLATION;
}

/**
 * Check if an error is a PostgreSQL foreign key constraint violation.
 */
export function isForeignKeyConstraintError(error: unknown): boolean {
  return getPostgresErrorCode(error) === PG_FOREIGN_KEY_VIOLATION;
}
