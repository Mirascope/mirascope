/**
 * @fileoverview OAuth type definitions.
 *
 * This module contains only TypeScript type definitions with no runtime code.
 */
import { Schema } from "effect";

export type AuthenticatedUserInfo = {
  email: string | null;
  name: string | null;
};

export type OAuthTokenResponse = {
  access_token?: string;
  token_type?: string;
  scope?: string;
  error?: string;
  error_description?: string;
};

// =============================================================================
// OAuth API Response Schemas
// =============================================================================

/** Schema for OAuth token exchange response */
export const TokenDataSchema = Schema.Struct({
  access_token: Schema.optional(Schema.String),
  error: Schema.optional(Schema.String),
});
export type TokenData = Schema.Schema.Type<typeof TokenDataSchema>;

/** Schema for GitHub user profile response */
export const GitHubUserSchema = Schema.Struct({
  id: Schema.Number,
  login: Schema.String,
  name: Schema.NullOr(Schema.String),
  email: Schema.NullOr(Schema.String),
  avatar_url: Schema.String,
  bio: Schema.NullOr(Schema.String),
  created_at: Schema.String,
  updated_at: Schema.String,
});
export type GitHubUser = Schema.Schema.Type<typeof GitHubUserSchema>;

/** Schema for GitHub email response */
export const GitHubEmailSchema = Schema.Struct({
  email: Schema.String,
  primary: Schema.Boolean,
  verified: Schema.Boolean,
  visibility: Schema.NullOr(Schema.String),
});
export type GitHubEmail = Schema.Schema.Type<typeof GitHubEmailSchema>;

/** Schema for Google user profile response */
export const GoogleUserSchema = Schema.Struct({
  id: Schema.String,
  email: Schema.String,
  verified_email: Schema.Boolean,
  name: Schema.String,
  given_name: Schema.String,
  family_name: Schema.String,
  picture: Schema.String,
  locale: Schema.optional(Schema.String),
});
export type GoogleUser = Schema.Schema.Type<typeof GoogleUserSchema>;

export interface OAuthProvider {
  authUrl: string;
  tokenUrl: string;
  userUrl: string;
  scopes: string[];
  clientId: string;
  clientSecret: string;
  callbackUrl: string;
  mapUserData: (
    apiResponse: unknown,
    accessToken: string,
  ) => Promise<AuthenticatedUserInfo>;
}

type OAuthProviderBase = {
  authUrl: string;
  tokenUrl: string;
  userUrl: string;
  scopes: string[];
  clientId: string;
  clientSecret: string;
  callbackUrl: string;
};

export type OAuthProviderConfig =
  | (OAuthProviderBase & { name: "github" })
  | (OAuthProviderBase & { name: "google" });
