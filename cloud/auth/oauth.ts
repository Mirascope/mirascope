import { Effect } from "effect";
import { DatabaseService, DEFAULT_SESSION_DURATION, type Database } from "@/db";
import { EnvironmentService } from "@/environment";
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
  const env = yield* EnvironmentService;

  if (
    !env.GITHUB_CLIENT_ID ||
    !env.GITHUB_CLIENT_SECRET ||
    !env.GITHUB_CALLBACK_URL
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
    clientId: env.GITHUB_CLIENT_ID,
    clientSecret: env.GITHUB_CLIENT_SECRET,
    callbackUrl: env.GITHUB_CALLBACK_URL,
  };
});

export const createGoogleProvider = Effect.gen(function* () {
  const env = yield* EnvironmentService;

  if (
    !env.GOOGLE_CLIENT_ID ||
    !env.GOOGLE_CLIENT_SECRET ||
    !env.GOOGLE_CALLBACK_URL
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
    clientId: env.GOOGLE_CLIENT_ID,
    clientSecret: env.GOOGLE_CLIENT_SECRET,
    callbackUrl: env.GOOGLE_CALLBACK_URL,
  };
});

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
  return Effect.gen(function* () {
    const env = yield* EnvironmentService;
    const db = yield* DatabaseService;

    const url = new URL(request.url);
    const code = url.searchParams.get("code");
    const encodedState = url.searchParams.get("state");
    const error = url.searchParams.get("error");

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

    const stateData = yield* Effect.try({
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

    const { randomState, returnUrl } = stateData;
    const storedState = getOAuthStateFromCookie(request);

    if (storedState !== randomState) {
      return yield* Effect.fail(
        new InvalidStateError({
          message: "Invalid state parameter",
        }),
      );
    }

    const tokenData = yield* Effect.tryPromise({
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
    });

    if (tokenData.error) {
      return yield* Effect.fail(
        new OAuthError({
          message: `Token exchange failed: ${tokenData.error}`,
          provider: provider.name,
        }),
      );
    }

    if (!tokenData.access_token) {
      return yield* Effect.fail(
        new OAuthError({
          message: "No access token received",
          provider: provider.name,
        }),
      );
    }

    const userInfo = yield* fetchUserInfo(provider, tokenData.access_token);

    const response = yield* processAuthenticatedUser(
      db,
      userInfo,
      returnUrl,
      env.SITE_URL || "http://localhost:3000",
    );

    response.headers.append("Set-Cookie", clearOAuthStateCookie());
    return response;
  });
}

function fetchUserInfo(provider: OAuthProviderConfig, accessToken: string) {
  return Effect.gen(function* () {
    const userData = yield* Effect.tryPromise({
      try: async () => {
        const response = await fetch(provider.userUrl, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
            Accept: "application/json",
            "User-Agent": "Mirascope/0.1",
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch user data");
        }

        return response.json();
      },
      catch: (e) =>
        new OAuthError({
          message: "Failed to fetch user data",
          provider: provider.name,
          cause: e,
        }),
    });

    if (provider.name === "github") {
      const emails = yield* Effect.tryPromise({
        try: async () => {
          const response = await fetch("https://api.github.com/user/emails", {
            headers: {
              Authorization: `Bearer ${accessToken}`,
              Accept: "application/vnd.github+json",
              "X-GitHub-Api-Version": "2022-11-28",
              "User-Agent": "Mirascope/0.1",
            },
          });

          if (response.ok) {
            const json = await response.json();
            return json as GitHubEmail[];
          }
          return [] as GitHubEmail[];
        },
        catch: () =>
          new OAuthError({
            message: "Failed to fetch GitHub emails",
            provider: provider.name,
          }),
      });

      return mapGitHubUserData(userData as GitHubUser, emails);
    } else {
      return mapGoogleUserData(userData as GoogleUser);
    }
  });
}

function processAuthenticatedUser(
  db: Database,
  userInfo: AuthenticatedUserInfo,
  returnUrl: string | undefined,
  siteUrl: string,
) {
  return Effect.gen(function* () {
    if (!userInfo.email) {
      return yield* Effect.fail(
        new AuthenticationFailedError({
          message: "Email is required to process an authenticated user",
        }),
      );
    }

    const user = yield* db.users.createOrUpdate({
      email: userInfo.email,
      name: userInfo.name,
    });

    const expiresAt = new Date(Date.now() + DEFAULT_SESSION_DURATION);
    const session = yield* db.sessions.create({
      userId: user.id,
      expiresAt: expiresAt,
    });

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

function isValidPreviewUrl(url: string): boolean {
  try {
    const parsedUrl = new URL(url);
    return (
      !!parsedUrl.hostname.match(/^.*-pr-\d+\.mirascope\.workers\.dev$/) ||
      parsedUrl.hostname === "staging.mirascope.com"
    );
  } catch {
    return false;
  }
}

export function handleOAuthProxyCallback(
  request: Request,
  providerName: string,
) {
  return Effect.gen(function* () {
    const url = new URL(request.url);
    const code = url.searchParams.get("code");
    const encodedState = url.searchParams.get("state");
    const error = url.searchParams.get("error");
    const errorDescription = url.searchParams.get("error_description");

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

    const stateData = yield* Effect.try({
      try: () =>
        JSON.parse(atob(encodedState)) as {
          randomState: string;
          returnUrl?: string;
        },
      catch: () =>
        new InvalidStateError({
          message: "Invalid state parameter - unable to decode",
        }),
    });

    const returnUrl = stateData.returnUrl;
    if (!returnUrl) {
      return yield* Effect.fail(
        new InvalidStateError({
          message: "No return URL found in state",
        }),
      );
    }

    if (!isValidPreviewUrl(returnUrl)) {
      return yield* Effect.fail(
        new InvalidStateError({
          message: "Invalid return URL",
        }),
      );
    }

    const storedState = getOAuthStateFromCookie(request);
    if (!storedState || storedState !== stateData.randomState) {
      return yield* Effect.fail(
        new InvalidStateError({
          message: "Invalid state parameter - does not match stored state",
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
        "Set-Cookie": setOAuthStateCookie(stateData.randomState),
      },
    });
  });
}
