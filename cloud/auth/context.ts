import { Context } from "effect";
import type { PublicUser } from "@/db/schema";

/**
 * Context that provides the authenticated user for the current request.
 * This is set by the request handler and required by authenticated endpoints.
 */
export class AuthenticatedUser extends Context.Tag("AuthenticatedUser")<
  AuthenticatedUser,
  PublicUser
>() {}
