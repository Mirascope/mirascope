export * from "./sessions";
export * from "./users";

export type { PublicSession } from "./sessions";
export type { PublicUser } from "./users";

// Export table types for use in service constraints
import { users } from "./users";
import { sessions } from "./sessions";

/**
 * Union type of all database tables
 * This allows BaseService to have better type safety by constraining TTable
 * to actual table instances rather than the generic PgTable type
 */
export type DatabaseTable = typeof users | typeof sessions;
