import { Context } from "effect";

import {
  createGitHubProvider,
  createGoogleProvider,
  initiateOAuth,
  handleOAuthCallback,
  handleOAuthProxyCallback,
} from "@/auth/oauth";

export * from "@/auth/errors";

type Auth = {
  readonly createGitHubProvider: typeof createGitHubProvider;
  readonly createGoogleProvider: typeof createGoogleProvider;
  readonly initiateOAuth: typeof initiateOAuth;
  readonly handleCallback: typeof handleOAuthCallback;
  readonly handleProxyCallback: typeof handleOAuthProxyCallback;
};

export class AuthService extends Context.Tag("AuthService")<
  AuthService,
  Auth
>() {}

export function createAuthService(): Auth {
  return {
    createGitHubProvider,
    createGoogleProvider,
    initiateOAuth,
    handleCallback: handleOAuthCallback,
    handleProxyCallback: handleOAuthProxyCallback,
  };
}
