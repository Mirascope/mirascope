import { Effect } from "effect";
import { DatabaseService, DEFAULT_SESSION_DURATION } from "@/db";
import { AlreadyExistsError, DatabaseError } from "@/db/errors";
import { SettingsService } from "@/settings";
import {
  OAuthError,
  InvalidStateError,
  MissingCredentialsError,
  AuthenticationFailedError,
} from "@/auth/errors";
import type { AuthenticatedUserInfo, OAuthProviderConfig } from "@/auth/types";
import {
  getOAuthStateFromCookie,
  clearOAuthStateCookie,
  setSessionCookie,
  setOAuthStateCookie,
} from "@/auth/utils";

type GitHubUser = {
  id: number;
  login: string;
  name: string | null;
  email: string | null;
  avatar_url: string;
  bio: string | null;
  created_at: string;
  updated_at: string;
};

type GitHubEmail = {
  email: string;
  primary: boolean;
  verified: boolean;
  visibility: string | null;
};

type GoogleUser = {
  id: string;
  email: string;
  verified_email: boolean;
  name: string;
  given_name: string;
  family_name: string;
  picture: string;
  locale: string;
};

function mapGitHubUserData(
  apiResponse: GitHubUser,
  emails: GitHubEmail[],
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

function mapGoogleUserData(apiResponse: GoogleUser): AuthenticatedUserInfo {
  return {
    email: apiResponse.email,
    name: apiResponse.name,
  };
}

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
      yield* Effect.fail(
        new OAuthError({
          message: `OAuth Error: ${error}`,
          provider: provider.name,
        }),
      );
    }

    const validCode = yield* code
      ? Effect.succeed(code)
      : Effect.fail(
          new OAuthError({
            message: "No authorization code received",
            provider: provider.name,
          }),
        );

    const validState = yield* encodedState
      ? Effect.succeed(encodedState)
      : Effect.fail(
          new InvalidStateError({
            message: "No state received",
          }),
        );

    return { code: validCode, encodedState: validState };
  });
};

const decodeState = (
  encodedState: string,
): Effect.Effect<
  { randomState: string; returnUrl?: string },
  InvalidStateError
> => {
  return Effect.try({
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
};

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

const validateTokenResponse = (
  tokenData: {
    access_token?: string;
    error?: string;
  },
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

const exchangeCodeForToken = (
  provider: OAuthProviderConfig,
  code: string,
): Effect.Effect<string, OAuthError> => {
  return Effect.tryPromise({
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
      const json = await response.json();
      return json as {
        access_token?: string;
        error?: string;
      };
    },
    catch: (e) =>
      new OAuthError({
        message: "Failed to exchange code for token",
        provider: provider.name,
        cause: e,
      }),
  }).pipe(
    Effect.flatMap((tokenData) => validateTokenResponse(tokenData, provider)),
  );
};

export function initiateOAuth(
  provider: OAuthProviderConfig,
  currentUrl: string,
) {
  return Effect.sync(() => {
    const randomState = crypto.randomUUID();

    const stateData = {
      randomState,
      returnUrl: currentUrl,
    };
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

export function handleOAuthCallback(
  request: Request,
  provider: OAuthProviderConfig,
) {
  const url = new URL(request.url);
  const storedState = getOAuthStateFromCookie(request);

  return validateOAuthParams(url, provider).pipe(
    Effect.flatMap(({ code, encodedState }) =>
      decodeState(encodedState).pipe(
        Effect.flatMap((stateData) =>
          validateStateMatch(storedState, stateData.randomState).pipe(
            Effect.map(() => ({ code, returnUrl: stateData.returnUrl })),
          ),
        ),
      ),
    ),
    Effect.flatMap(({ code, returnUrl }) =>
      exchangeCodeForToken(provider, code).pipe(
        Effect.flatMap((accessToken) => fetchUserInfo(provider, accessToken)),
        Effect.flatMap((userInfo) =>
          Effect.gen(function* () {
            const settings = yield* SettingsService;
            const response = yield* processAuthenticatedUser(
              userInfo,
              returnUrl,
              settings.SITE_URL || "http://localhost:3000",
            );
            response.headers.append("Set-Cookie", clearOAuthStateCookie());
            return response;
          }),
        ),
      ),
    ),
  );
}

function fetchJson<T>(
  url: string,
  options: {
    headers: Record<string, string>;
    errorMessage: string;
    provider: string;
  },
): Effect.Effect<T, OAuthError> {
  return Effect.tryPromise({
    try: async () => {
      const response = await fetch(url, { headers: options.headers });
      return response;
    },
    catch: (e) =>
      new OAuthError({
        message: options.errorMessage,
        provider: options.provider,
        cause: e,
      }),
  }).pipe(
    Effect.flatMap((response) => {
      if (!response.ok) {
        return Effect.fail(
          new OAuthError({
            message: options.errorMessage,
            provider: options.provider,
          }),
        );
      }

      return Effect.tryPromise({
        try: async () => response.json(),
        catch: (e) =>
          new OAuthError({
            message: `Failed to parse ${options.errorMessage.toLowerCase()}`,
            provider: options.provider,
            cause: e,
          }),
      });
    }),
  );
}

function fetchGitHubEmails(
  accessToken: string,
  provider: string,
): Effect.Effect<GitHubEmail[], OAuthError> {
  return fetchJson<GitHubEmail[]>("https://api.github.com/user/emails", {
    headers: {
      Authorization: `Bearer ${accessToken}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "Mirascope/0.1",
    },
    errorMessage: "Failed to fetch GitHub emails",
    provider,
  }).pipe(Effect.catchAll(() => Effect.succeed([] as GitHubEmail[])));
}

function fetchGitHubUserInfo(
  provider: OAuthProviderConfig & { name: "github" },
  accessToken: string,
): Effect.Effect<AuthenticatedUserInfo, OAuthError> {
  return Effect.gen(function* () {
    const userData = yield* fetchJson<GitHubUser>(provider.userUrl, {
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

function fetchGoogleUserInfo(
  provider: OAuthProviderConfig & { name: "google" },
  accessToken: string,
): Effect.Effect<AuthenticatedUserInfo, OAuthError> {
  return Effect.gen(function* () {
    const userData = yield* fetchJson<GoogleUser>(provider.userUrl, {
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

function fetchUserInfo(
  provider: OAuthProviderConfig,
  accessToken: string,
): Effect.Effect<AuthenticatedUserInfo, OAuthError> {
  if (provider.name === "github") {
    return fetchGitHubUserInfo(provider, accessToken);
  }
  return fetchGoogleUserInfo(provider, accessToken);
}

function processAuthenticatedUser(
  userInfo: AuthenticatedUserInfo,
  returnUrl: string | undefined,
  siteUrl: string,
): Effect.Effect<
  Response,
  AuthenticationFailedError | AlreadyExistsError | DatabaseError,
  DatabaseService
> {
  const validateEmail = (email: string | null) => {
    return Effect.filterOrFail(
      Effect.succeed(email),
      (e): e is string => e !== null,
      () =>
        new AuthenticationFailedError({
          message: "Email is required to process an authenticated user",
        }),
    );
  };

  const createUserAndSession = (email: string) => {
    return Effect.gen(function* () {
      const db = yield* DatabaseService;

      const user = yield* db.users.createOrUpdate({
        email: email,
        name: userInfo.name,
      });

      const expiresAt = new Date(Date.now() + DEFAULT_SESSION_DURATION);
      const session = yield* db.sessions.create({
        userId: user.id,
        expiresAt: expiresAt,
      });

      return session.id;
    });
  };

  const buildRedirectResponse = (sessionId: string) => {
    return Effect.sync(() => {
      const redirectUrl = new URL(returnUrl || siteUrl);
      redirectUrl.searchParams.set("success", "true");

      return new Response(null, {
        status: 302,
        headers: {
          Location: redirectUrl.toString(),
          "Set-Cookie": setSessionCookie(sessionId),
        },
      });
    });
  };

  return validateEmail(userInfo.email).pipe(
    Effect.flatMap(createUserAndSession),
    Effect.flatMap(buildRedirectResponse),
  );
}

const validatePreviewUrl = (
  url: string,
): Effect.Effect<string, InvalidStateError> => {
  return Effect.try({
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
};

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
      yield* Effect.fail(
        new OAuthError({
          message: `OAuth Error: ${error} - ${errorDescription || ""}`,
          provider: providerName,
        }),
      );
    }

    const validState = yield* encodedState
      ? Effect.succeed(encodedState)
      : Effect.fail(
          new InvalidStateError({
            message: "No state parameter received",
          }),
        );

    const validCode = yield* code
      ? Effect.succeed(code)
      : Effect.fail(
          new OAuthError({
            message: "No authorization code received",
            provider: providerName,
          }),
        );

    return { code: validCode, encodedState: validState };
  });
};

const validateReturnUrl = (
  returnUrl: string | undefined,
): Effect.Effect<string, InvalidStateError> => {
  return returnUrl
    ? Effect.succeed(returnUrl)
    : Effect.fail(
        new InvalidStateError({
          message: "No return URL found in state",
        }),
      );
};

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

const buildProxyRedirectResponse = (
  returnUrl: string,
  code: string,
  encodedState: string,
  randomState: string,
  providerName: string,
): Effect.Effect<Response> => {
  return Effect.sync(() => {
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
};

export function handleOAuthProxyCallback(
  request: Request,
  providerName: string,
) {
  const url = new URL(request.url);
  const storedState = getOAuthStateFromCookie(request);

  return validateProxyParams(url, providerName).pipe(
    Effect.flatMap(({ code, encodedState }) =>
      decodeState(encodedState).pipe(
        Effect.flatMap((stateData) =>
          validateReturnUrl(stateData.returnUrl).pipe(
            Effect.flatMap((returnUrl) =>
              validatePreviewUrl(returnUrl).pipe(
                Effect.flatMap(() =>
                  validateProxyStateMatch(
                    storedState,
                    stateData.randomState,
                  ).pipe(
                    Effect.map(() => ({
                      code,
                      encodedState,
                      returnUrl,
                      randomState: stateData.randomState,
                    })),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    ),
    Effect.flatMap(({ code, encodedState, returnUrl, randomState }) =>
      buildProxyRedirectResponse(
        returnUrl,
        code,
        encodedState,
        randomState,
        providerName,
      ),
    ),
  );
}
