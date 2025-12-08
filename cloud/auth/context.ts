import { Context, Data } from "effect";
import type { PublicUser } from "@/db/schema";

/**
 * Error thrown when a request is not authenticated
 */
export class UnauthorizedError extends Data.TaggedError("UnauthorizedError")<{
  readonly message: string;
}> {}

/**
 * Context that provides the authenticated user for the current request.
 * This is set by the authentication middleware and required by authenticated endpoints.
 */
export class AuthenticatedUser extends Context.Tag("AuthenticatedUser")<
  AuthenticatedUser,
  PublicUser
>() {}
