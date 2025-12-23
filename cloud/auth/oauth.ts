/* v8 ignore start -- OAuth flows require network requests to external providers */
/**
 * @fileoverview OAuth authentication flow implementation.
 *
 * This module handles OAuth flows for GitHub and Google providers, including:
 * - Provider configuration creation
 * - OAuth flow initiation and callbacks
 * - Token exchange and user info fetching
 * - Session creation and redirect handling
 *
 * These functions involve network requests to external OAuth providers and are
 * tested via integration tests rather than unit tests.
 */
import { Effect, Schema } from "effect";
import { EffectDatabase, DEFAULT_SESSION_DURATION } from "@/db";
import { NotFoundError, AlreadyExistsError, DatabaseError } from "@/errors";
import { SettingsService } from "@/settings";
import {
  OAuthError,
  InvalidStateError,
  MissingCredentialsError,
  AuthenticationFailedError,
} from "@/auth/errors";
import type {
  AuthenticatedUserInfo,
  OAuthProviderConfig,
  GitHubUser,
  GitHubEmail,
  GoogleUser,
  TokenData,
} from "@/auth/types";
import { 
  TokenDataSchema,
  GitHubUserSchema,
  GitHubEmailSchema,
  GoogleUserSchema,
} from "@/auth/types";
import {
  getOAuthStateFromCookie,
  clearOAuthStateCookie,
  setSessionCookie,
  setOAuthStateCookie,
} from "@/auth/utils";

// =============================================================================
// User Data Mappers
// =============================================================================

/**
 * Maps GitHub API user data to our internal user info format.
 *
 * Falls back to the primary email from the emails list if the user's
 * public email is not set.
 */
function mapGitHubUserData(
  apiResponse: GitHubUser,
  emails: readonly GitHubEmail[],
): AuthenticatedUserInfo {
  let userEmail = apiResponse.email;

  if (!userEmail && emails.length > 0) {
    const primaryEmail = emails.find((email) => email.primary);
    userEmail = primaryEmail ? primaryEmail.email : null;
  }

  return {
    email: userEmail,
    name: apiResponse.name,
  };
}

/**
 * Maps Google API user data to our internal user info format.
 */
function mapGoogleUserData(apiResponse: GoogleUser): AuthenticatedUserInfo {
  return {
    email: apiResponse.email,
    name: apiResponse.name,
  };
}

// =============================================================================
// OAuth Provider Configuration
// =============================================================================

/**
 * Creates a GitHub OAuth provider configuration from environment settings.
 *
 * Requires the following environment variables:
 * - `GITHUB_CLIENT_ID` - GitHub OAuth app client ID
 * - `GITHUB_CLIENT_SECRET` - GitHub OAuth app client secret
 * - `GITHUB_CALLBACK_URL` - Callback URL registered with GitHub
 *
 * @throws MissingCredentialsError - If any required environment variable is missing
 */
export const createGitHubProvider = Effect.gen(function* () {
  const settings = yield* SettingsService;

  if (
    !settings.GITHUB_CLIENT_ID ||
    !settings.GITHUB_CLIENT_SECRET ||
    !settings.GITHUB_CALLBACK_URL
  ) {
    return yield* Effect.fail(
      new MissingCredentialsError({
        message: "Missing required GitHub OAuth environment variables",
        provider: "github",
      }),
    );
  }

  return {
    name: "github" as const,
    authUrl: "https://github.com/login/oauth/authorize",
    tokenUrl: "https://github.com/login/oauth/access_token",
    userUrl: "https://api.github.com/user",
    scopes: ["user:email"],
    clientId: settings.GITHUB_CLIENT_ID,
    clientSecret: settings.GITHUB_CLIENT_SECRET,
    callbackUrl: settings.GITHUB_CALLBACK_URL,
  };
});

/**
 * Creates a Google OAuth provider configuration from environment settings.
 *
 * Requires the following environment variables:
 * - `GOOGLE_CLIENT_ID` - Google OAuth client ID
 * - `GOOGLE_CLIENT_SECRET` - Google OAuth client secret
 * - `GOOGLE_CALLBACK_URL` - Callback URL registered with Google
 *
 * @throws MissingCredentialsError - If any required environment variable is missing
 */
export const createGoogleProvider = Effect.gen(function* () {
  const settings = yield* SettingsService;

  if (
    !settings.GOOGLE_CLIENT_ID ||
    !settings.GOOGLE_CLIENT_SECRET ||
    !settings.GOOGLE_CALLBACK_URL
  ) {
    return yield* Effect.fail(
      new MissingCredentialsError({
        message: "Missing required Google OAuth environment variables",
        provider: "google",
      }),
    );
  }

  return {
    name: "google" as const,
    authUrl: "https://accounts.google.com/o/oauth2/v2/auth",
    tokenUrl: "https://oauth2.googleapis.com/token",
    userUrl: "https://www.googleapis.com/oauth2/v1/userinfo",
    scopes: ["openid", "email", "profile"],
    clientId: settings.GOOGLE_CLIENT_ID,
    clientSecret: settings.GOOGLE_CLIENT_SECRET,
    callbackUrl: settings.GOOGLE_CALLBACK_URL,
  };
});

// =============================================================================
// OAuth Validation Helpers
// =============================================================================

/**
 * Validates the OAuth callback URL parameters.
 *
 * Extracts and validates the authorization code and state from the callback URL.
 *
 * @throws OAuthError - If the provider returned an error or no code
 * @throws InvalidStateError - If no state parameter was received
 */
const validateOAuthParams = (
  url: URL,
  provider: OAuthProviderConfig,
): Effect.Effect<
  { code: string; encodedState: string },
  OAuthError | InvalidStateError
> => {
  const error = url.searchParams.get("error");
  const code = url.searchParams.get("code");
  const encodedState = url.searchParams.get("state");

  return Effect.gen(function* () {
    if (error) {
      return yield* Effect.fail(
        new OAuthError({
          message: `OAuth Error: ${error}`,
          provider: provider.name,
        }),
      );
    }

    if (!code) {
      return yield* Effect.fail(
        new OAuthError({
          message: "No authorization code received",
          provider: provider.name,
        }),
      );
    }

    if (!encodedState) {
      return yield* Effect.fail(
        new InvalidStateError({
          message: "No state received",
        }),
      );
    }

    return { code, encodedState };
  });
};

/**
 * Decodes the base64-encoded OAuth state parameter.
 *
 * The state contains CSRF protection data and optional return URL.
 *
 * @throws InvalidStateError - If the state cannot be decoded
 */
const decodeState = (
  encodedState: string,
): Effect.Effect<
  { randomState: string; returnUrl?: string },
  InvalidStateError
> =>
  Effect.try({
    try: () =>
      JSON.parse(atob(encodedState)) as {
        randomState: string;
        returnUrl?: string;
      },
    catch: (e) =>
      new InvalidStateError({
        message: `Failed to decode state: ${String(e)}`,
      }),
  });

/**
 * Validates that the state parameter matches the stored cookie value.
 *
 * This provides CSRF protection by ensuring the callback originated
 * from a request we initiated.
 *
 * @throws InvalidStateError - If the states don't match
 */
const validateStateMatch = (
  storedState: string | null,
  randomState: string,
): Effect.Effect<void, InvalidStateError> => {
  if (storedState !== randomState) {
    return Effect.fail(
      new InvalidStateError({
        message: "Invalid state parameter",
      }),
    );
  }
  return Effect.void;
};

/**
 * Validates the token exchange response from the OAuth provider.
 *
 * @throws OAuthError - If the token exchange failed or no token received
 */
const validateTokenResponse = (
  tokenData: TokenData,
  provider: OAuthProviderConfig,
): Effect.Effect<string, OAuthError> => {
  if (tokenData.error) {
    return Effect.fail(
      new OAuthError({
        message: `Token exchange failed: ${tokenData.error}`,
        provider: provider.name,
      }),
    );
  }

  if (!tokenData.access_token) {
    return Effect.fail(
      new OAuthError({
        message: "No access token received",
        provider: provider.name,
      }),
    );
  }

  return Effect.succeed(tokenData.access_token);
};

// =============================================================================
// Token Exchange
// =============================================================================

/**
 * Exchanges an authorization code for an access token.
 *
 * Makes a POST request to the provider's token endpoint with the
 * authorization code and client credentials.
 *
 * @throws OAuthError - If the token exchange fails
 */
const exchangeCodeForToken = (
  provider: OAuthProviderConfig,
  code: string,
): Effect.Effect<string, OAuthError> =>
  Effect.gen(function* () {
    const unknownData = yield* Effect.tryPromise({
      try: async () => {
        const response = await fetch(provider.tokenUrl, {
          method: "POST",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: new URLSearchParams({
            grant_type: "authorization_code",
            client_id: provider.clientId,
            client_secret: provider.clientSecret,
            code: code,
            redirect_uri: provider.callbackUrl,
          }),
        });
        return await response.json();
      },
      catch: (e) =>
        new OAuthError({
          message: "Failed to exchange code for token",
          provider: provider.name,
          cause: e,
        }),
    });

    // Validate the response against the TokenData schema
    const tokenData = yield* Schema.decodeUnknown(TokenDataSchema)(
      unknownData,
    ).pipe(
      Effect.mapError(
        (e) =>
          new OAuthError({
            message: `Invalid token response: ${e.message}`,
            provider: provider.name,
          }),
      ),
    );

    return yield* validateTokenResponse(tokenData, provider);
  });

// =============================================================================
// OAuth Flow - Initiation
// =============================================================================

/**
 * Initiates the OAuth flow by redirecting to the provider's authorization URL.
 *
 * Generates a random state for CSRF protection, encodes it with the return URL,
 * and redirects the user to the OAuth provider's authorization endpoint.
 *
 * The state is also stored in a cookie for validation during the callback.
 *
 * @param provider - The OAuth provider configuration
 * @param currentUrl - The URL to return to after authentication
 * @returns A redirect response to the OAuth provider
 */
export function initiateOAuth(
  provider: OAuthProviderConfig,
  currentUrl: string,
): Effect.Effect<Response> {
  return Effect.sync(() => {
    const randomState = crypto.randomUUID();

    const stateData = { randomState, returnUrl: currentUrl };
    const encodedState = btoa(JSON.stringify(stateData));

    const authUrl = new URL(provider.authUrl);
    authUrl.searchParams.set("response_type", "code");
    authUrl.searchParams.set("client_id", provider.clientId);
    authUrl.searchParams.set("redirect_uri", provider.callbackUrl);
    authUrl.searchParams.set("scope", provider.scopes.join(" "));
    authUrl.searchParams.set("state", encodedState);

    return new Response(null, {
      status: 302,
      headers: {
        Location: authUrl.toString(),
        "Set-Cookie": setOAuthStateCookie(randomState),
      },
    });
  });
}

/**
 * Handles the OAuth callback from an external OAuth provider.
 *
 * This is the main callback handler for completing the OAuth flow:
 *
 * ## Flow
 *
 * 1. Validate OAuth params (code, state) from the callback URL
 * 2. Decode and validate the state parameter (CSRF protection)
 * 3. Exchange the authorization code for an access token
 * 4. Fetch user info from the provider's API
 * 5. Create or update the user and session in the database
 * 6. Redirect to the return URL with a session cookie
 *
 * @param request - The incoming callback request from the OAuth provider
 * @param provider - The OAuth provider configuration
 * @returns A redirect response with session cookie set
 * @throws OAuthError - If any OAuth step fails
 * @throws InvalidStateError - If state validation fails (CSRF protection)
 * @throws AuthenticationFailedError - If user processing fails
 */
export function handleOAuthCallback(
  request: Request,
  provider: OAuthProviderConfig,
) {
  const url = new URL(request.url);
  const storedState = getOAuthStateFromCookie(request);

  return Effect.gen(function* () {
    // 1. Validate OAuth params from callback URL
    const { code, encodedState } = yield* validateOAuthParams(url, provider);

    // 2. Decode and validate state (CSRF protection)
    const stateData = yield* decodeState(encodedState);
    yield* validateStateMatch(storedState, stateData.randomState);

    // 3. Exchange authorization code for access token
    const accessToken = yield* exchangeCodeForToken(provider, code);

    // 4. Fetch user info from provider
    const userInfo = yield* fetchUserInfo(provider, accessToken);

    // 5. Create/update user and session
    const settings = yield* SettingsService;
    const response = yield* processAuthenticatedUser(
      userInfo,
      stateData.returnUrl,
      settings.SITE_URL || "http://localhost:3000",
    );

    // 6. Clear OAuth state cookie and return redirect
    response.headers.append("Set-Cookie", clearOAuthStateCookie());
    return response;
  });
}

// =============================================================================
// User Info Fetching
// =============================================================================

/**
 * Fetches JSON data from a URL with schema validation.
 *
 * @throws OAuthError - If the fetch fails, response is not OK, or validation fails
 */
function fetchJson<A, I, R>(
  url: string,
  schema: Schema.Schema<A, I, R>,
  options: {
    headers: Record<string, string>;
    errorMessage: string;
    provider: string;
  },
): Effect.Effect<A, OAuthError, R> {
  return Effect.gen(function* () {
    const response = yield* Effect.tryPromise({
      try: () => fetch(url, { headers: options.headers }),
      catch: (e) =>
        new OAuthError({
          message: options.errorMessage,
          provider: options.provider,
          cause: e,
        }),
    });

    if (!response.ok) {
      return yield* Effect.fail(
        new OAuthError({
          message: options.errorMessage,
          provider: options.provider,
        }),
      );
    }

    const unknownData = yield* Effect.tryPromise({
      try: () => response.json(),
      catch: (e) =>
        new OAuthError({
          message: `Failed to parse ${options.errorMessage.toLowerCase()}`,
          provider: options.provider,
          cause: e,
        }),
    });

    // Validate the response against the provided schema
    return yield* Schema.decodeUnknown(schema)(unknownData).pipe(
      Effect.mapError(
        (e) =>
          new OAuthError({
            message: `Invalid response format: ${e.message}`,
            provider: options.provider,
          }),
      ),
    );
  });
}

/**
 * Fetches the user's email addresses from GitHub.
 *
 * Returns an empty array on failure (emails are optional fallback).
 */
function fetchGitHubEmails(
  accessToken: string,
  provider: string,
): Effect.Effect<readonly GitHubEmail[], OAuthError> {
  return fetchJson(
    "https://api.github.com/user/emails",
    Schema.Array(GitHubEmailSchema),
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "Mirascope/0.1",
      },
      errorMessage: "Failed to fetch GitHub emails",
      provider,
    },
  ).pipe(Effect.catchAll(() => Effect.succeed([] as const)));
}

/**
 * Fetches user info from GitHub's API.
 *
 * Also fetches emails separately as a fallback for users without public email.
 */
function fetchGitHubUserInfo(
  provider: OAuthProviderConfig & { name: "github" },
  accessToken: string,
): Effect.Effect<AuthenticatedUserInfo, OAuthError> {
  return Effect.gen(function* () {
    const userData = yield* fetchJson(provider.userUrl, GitHubUserSchema, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        Accept: "application/json",
        "User-Agent": "Mirascope/0.1",
      },
      errorMessage: "Failed to fetch GitHub user data",
      provider: provider.name,
    });

    const emails = yield* fetchGitHubEmails(accessToken, provider.name);
    return mapGitHubUserData(userData, emails);
  });
}

/**
 * Fetches user info from Google's API.
 */
function fetchGoogleUserInfo(
  provider: OAuthProviderConfig & { name: "google" },
  accessToken: string,
): Effect.Effect<AuthenticatedUserInfo, OAuthError> {
  return Effect.gen(function* () {
    const userData = yield* fetchJson(provider.userUrl, GoogleUserSchema, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        Accept: "application/json",
        "User-Agent": "Mirascope/0.1",
      },
      errorMessage: "Failed to fetch Google user data",
      provider: provider.name,
    });

    return mapGoogleUserData(userData);
  });
}

/**
 * Fetches user info from the appropriate OAuth provider.
 *
 * Routes to the provider-specific implementation based on provider name.
 */
function fetchUserInfo(
  provider: OAuthProviderConfig,
  accessToken: string,
): Effect.Effect<AuthenticatedUserInfo, OAuthError> {
  if (provider.name === "github") {
    return fetchGitHubUserInfo(provider, accessToken);
  }
  return fetchGoogleUserInfo(provider, accessToken);
}

// =============================================================================
// User Processing
// =============================================================================

/**
 * Processes an authenticated user from OAuth.
 *
 * Creates or updates the user in the database, creates a new session,
 * and returns a redirect response with the session cookie.
 *
 * @param userInfo - The user info from the OAuth provider
 * @param returnUrl - Optional URL to redirect to after authentication
 * @param siteUrl - The default site URL if no return URL is provided
 * @returns A redirect response with session cookie
 * @throws AuthenticationFailedError - If no email is provided
 * @throws DatabaseError - If user/session creation fails
 */
function processAuthenticatedUser(
  userInfo: AuthenticatedUserInfo,
  returnUrl: string | undefined,
  siteUrl: string,
): Effect.Effect<
  Response,
  | AuthenticationFailedError
  | NotFoundError
  | AlreadyExistsError
  | DatabaseError,
  EffectDatabase
> {
  return Effect.gen(function* () {
    // 1. Validate email is present
    if (!userInfo.email) {
      return yield* Effect.fail(
        new AuthenticationFailedError({
          message: "Email is required to process an authenticated user",
        }),
      );
    }

    const db = yield* EffectDatabase;

    // 2. Try to find existing user by email, or create if not found
    const existingUser = yield* db.users.findByEmail(userInfo.email).pipe(
      Effect.map((user) => user as typeof user | null),
      Effect.catchIf(
        (e): e is NotFoundError => e instanceof NotFoundError,
        () => Effect.succeed(null),
      ),
    );

    const user = existingUser
      ? // User exists - update name if different
        existingUser.name !== userInfo.name
        ? yield* db.users.update({
            userId: existingUser.id,
            data: { name: userInfo.name },
          })
        : existingUser
      : // User doesn't exist - create new user
        yield* db.users.create({
          data: { email: userInfo.email, name: userInfo.name },
        });

    // 3. Create a new session
    const expiresAt = new Date(Date.now() + DEFAULT_SESSION_DURATION);
    const session = yield* db.sessions.create({
      userId: user.id,
      data: { userId: user.id, expiresAt },
    });

    // 4. Build redirect response with session cookie
    const redirectUrl = new URL(returnUrl || siteUrl);
    redirectUrl.searchParams.set("success", "true");

    return new Response(null, {
      status: 302,
      headers: {
        Location: redirectUrl.toString(),
        "Set-Cookie": setSessionCookie(session.id),
      },
    });
  });
}

// =============================================================================
// OAuth Proxy Helpers (for preview/staging environments)
// =============================================================================

/**
 * Validates that a URL is a valid preview or staging URL.
 *
 * Valid URLs are:
 * - `*-pr-{number}.mirascope.workers.dev` (PR preview deployments)
 * - `staging.mirascope.com`
 *
 * @throws InvalidStateError - If the URL is not a valid preview/staging URL
 */
const validatePreviewUrl = (
  url: string,
): Effect.Effect<string, InvalidStateError> =>
  Effect.try({
    try: () => {
      const parsedUrl = new URL(url);
      const isValid =
        !!parsedUrl.hostname.match(/^.*-pr-\d+\.mirascope\.workers\.dev$/) ||
        parsedUrl.hostname === "staging.mirascope.com";

      if (!isValid) {
        throw new Error("Invalid preview URL");
      }
      return url;
    },
    catch: () =>
      new InvalidStateError({
        message: "Invalid return URL",
      }),
  });

/**
 * Validates OAuth callback parameters for proxy requests.
 *
 * @throws OAuthError - If the provider returned an error or no code
 * @throws InvalidStateError - If no state parameter was received
 */
const validateProxyParams = (
  url: URL,
  providerName: string,
): Effect.Effect<
  { code: string; encodedState: string },
  OAuthError | InvalidStateError
> => {
  const error = url.searchParams.get("error");
  const errorDescription = url.searchParams.get("error_description");
  const code = url.searchParams.get("code");
  const encodedState = url.searchParams.get("state");

  return Effect.gen(function* () {
    if (error) {
      return yield* Effect.fail(
        new OAuthError({
          message: `OAuth Error: ${error} - ${errorDescription || ""}`,
          provider: providerName,
        }),
      );
    }

    if (!encodedState) {
      return yield* Effect.fail(
        new InvalidStateError({
          message: "No state parameter received",
        }),
      );
    }

    if (!code) {
      return yield* Effect.fail(
        new OAuthError({
          message: "No authorization code received",
          provider: providerName,
        }),
      );
    }

    return { code, encodedState };
  });
};

/**
 * Validates that a return URL exists in the state.
 *
 * @throws InvalidStateError - If no return URL was found
 */
const validateReturnUrl = (
  returnUrl: string | undefined,
): Effect.Effect<string, InvalidStateError> =>
  returnUrl
    ? Effect.succeed(returnUrl)
    : Effect.fail(
        new InvalidStateError({
          message: "No return URL found in state",
        }),
      );

/**
 * Validates that the state parameter matches the stored cookie value.
 *
 * This provides CSRF protection for proxy callbacks.
 *
 * @throws InvalidStateError - If the states don't match
 */
const validateProxyStateMatch = (
  storedState: string | null,
  randomState: string,
): Effect.Effect<void, InvalidStateError> => {
  if (!storedState || storedState !== randomState) {
    return Effect.fail(
      new InvalidStateError({
        message: "Invalid state parameter - does not match stored state",
      }),
    );
  }
  return Effect.void;
};

/**
 * Builds a redirect response to forward the OAuth callback to the preview/staging URL.
 *
 * The response redirects to the target's callback endpoint with the
 * authorization code and state, and sets the OAuth state cookie.
 */
const buildProxyRedirectResponse = (
  returnUrl: string,
  code: string,
  encodedState: string,
  randomState: string,
  providerName: string,
): Effect.Effect<Response> =>
  Effect.sync(() => {
    const callbackUrl = new URL(
      `/auth/${providerName.toLowerCase()}/callback`,
      returnUrl,
    );
    callbackUrl.searchParams.set("code", code);
    callbackUrl.searchParams.set("state", encodedState);

    return new Response(null, {
      status: 302,
      headers: {
        Location: callbackUrl.toString(),
        "Set-Cookie": setOAuthStateCookie(randomState),
      },
    });
  });

// =============================================================================
// OAuth Flow - Proxy Callback
// =============================================================================

/**
 * Handles the OAuth proxy callback from an external OAuth provider.
 *
 * This is used for preview/staging environments where OAuth callbacks are
 * routed through a proxy. The proxy receives the OAuth callback, validates
 * the state, and redirects to the actual preview/staging URL with the
 * authorization code.
 *
 * ## Flow
 *
 * 1. Validate OAuth params (code, state) from the provider
 * 2. Decode and validate the state parameter (contains return URL and random state)
 * 3. Verify the return URL is a valid preview/staging URL
 * 4. Verify the state matches the stored cookie value (CSRF protection)
 * 5. Redirect to the preview/staging callback URL with the code and state
 *
 * @param request - The incoming callback request from the OAuth provider
 * @param providerName - The OAuth provider name (e.g., "github", "google")
 * @returns A redirect response to the preview/staging callback URL
 * @throws OAuthError - If the OAuth provider returned an error or no code
 * @throws InvalidStateError - If state validation fails (CSRF protection)
 */
export function handleOAuthProxyCallback(
  request: Request,
  providerName: string,
) {
  const url = new URL(request.url);
  const storedState = getOAuthStateFromCookie(request);

  return Effect.gen(function* () {
    // 1. Validate OAuth params from provider
    const { code, encodedState } = yield* validateProxyParams(
      url,
      providerName,
    );

    // 2. Decode state to get return URL and random state
    const stateData = yield* decodeState(encodedState);

    // 3. Validate return URL exists
    const returnUrl = yield* validateReturnUrl(stateData.returnUrl);

    // 4. Verify return URL is a valid preview/staging URL
    yield* validatePreviewUrl(returnUrl);

    // 5. Verify state matches stored cookie (CSRF protection)
    yield* validateProxyStateMatch(storedState, stateData.randomState);

    // 6. Build redirect response to the actual callback URL
    return yield* buildProxyRedirectResponse(
      returnUrl,
      code,
      encodedState,
      stateData.randomState,
      providerName,
    );
  });
}
