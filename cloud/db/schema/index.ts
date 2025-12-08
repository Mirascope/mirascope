export * from "@/db/schema/sessions";
export * from "@/db/schema/users";

export type { PublicSession } from "@/db/schema/sessions";
export type { PublicUser } from "@/db/schema/users";

// Export table types for use in service constraints
import { users } from "@/db/schema/users";
import { sessions } from "@/db/schema/sessions";

/**
 * Union type of all database tables
 * This allows BaseService to have better type safety by constraining TTable
 * to actual table instances rather than the generic PgTable type
 */
export type DatabaseTable = typeof users | typeof sessions;
