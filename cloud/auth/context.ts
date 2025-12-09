import { Context } from "effect";
import type { PublicUser, ApiKeyInfo } from "@/db/schema";

/**
 * Context that provides the authenticated user for the current request.
 * This is set by the request handler and required by authenticated endpoints.
 */
export class AuthenticatedUser extends Context.Tag("AuthenticatedUser")<
  AuthenticatedUser,
  PublicUser
>() {}

/**
 * Context that provides the authenticated API key info for the current request.
 * This is set by API key middleware and required by API key-authenticated endpoints.
 */
export class AuthenticatedApiKey extends Context.Tag("AuthenticatedApiKey")<
  AuthenticatedApiKey,
  ApiKeyInfo
>() {}
