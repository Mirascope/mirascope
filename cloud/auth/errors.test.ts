import { describe, it, expect } from "vitest";

import {
  OAuthError,
  InvalidStateError,
  MissingCredentialsError,
  AuthenticationFailedError,
} from "@/auth/errors";

describe("auth errors", () => {
  it("OAuthError has correct tag and fields", () => {
    const error = new OAuthError({
      message: "OAuth failed",
      provider: "github",
      cause: new Error("network"),
    });

    expect(error._tag).toBe("OAuthError");
    expect(error.message).toBe("OAuth failed");
    expect(error.provider).toBe("github");
    expect(error.cause).toBeInstanceOf(Error);
  });

  it("OAuthError works without optional fields", () => {
    const error = new OAuthError({ message: "fail" });

    expect(error._tag).toBe("OAuthError");
    expect(error.message).toBe("fail");
    expect(error.provider).toBeUndefined();
    expect(error.cause).toBeUndefined();
  });

  it("InvalidStateError has correct tag and fields", () => {
    const error = new InvalidStateError({ message: "bad state" });

    expect(error._tag).toBe("InvalidStateError");
    expect(error.message).toBe("bad state");
  });

  it("MissingCredentialsError has correct tag and fields", () => {
    const error = new MissingCredentialsError({
      message: "no creds",
      provider: "google",
    });

    expect(error._tag).toBe("MissingCredentialsError");
    expect(error.message).toBe("no creds");
    expect(error.provider).toBe("google");
  });

  it("AuthenticationFailedError has correct tag and fields", () => {
    const error = new AuthenticationFailedError({
      message: "auth failed",
      cause: "reason",
    });

    expect(error._tag).toBe("AuthenticationFailedError");
    expect(error.message).toBe("auth failed");
    expect(error.cause).toBe("reason");
  });

  it("AuthenticationFailedError works without optional cause", () => {
    const error = new AuthenticationFailedError({ message: "auth failed" });

    expect(error._tag).toBe("AuthenticationFailedError");
    expect(error.cause).toBeUndefined();
  });
});
