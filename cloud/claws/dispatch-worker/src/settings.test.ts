import { describe, expect, it } from "vitest";

import type { DispatchEnv } from "./types";

import { validateEnv, validateSiteUrl } from "./settings";

function makeEnv(
  overrides: Partial<Record<keyof DispatchEnv, unknown>> = {},
): DispatchEnv {
  return {
    Sandbox: {} as DispatchEnv["Sandbox"],
    MIRASCOPE_CLOUD: {} as DispatchEnv["MIRASCOPE_CLOUD"],
    SITE_URL: "https://mirascope.com",
    ...overrides,
  } as DispatchEnv;
}

describe("validateEnv", () => {
  it("does not throw when all required bindings are present", () => {
    expect(() => validateEnv(makeEnv())).not.toThrow();
  });

  it("throws when Sandbox is missing", () => {
    expect(() => validateEnv(makeEnv({ Sandbox: undefined }))).toThrow(
      "Sandbox",
    );
  });

  it("throws when MIRASCOPE_CLOUD is missing", () => {
    expect(() => validateEnv(makeEnv({ MIRASCOPE_CLOUD: undefined }))).toThrow(
      "MIRASCOPE_CLOUD",
    );
  });

  it("throws when SITE_URL is missing", () => {
    expect(() => validateEnv(makeEnv({ SITE_URL: "" }))).toThrow("SITE_URL");
  });

  it("lists all missing bindings when multiple are absent", () => {
    expect(() =>
      validateEnv(
        makeEnv({
          Sandbox: undefined,
          MIRASCOPE_CLOUD: undefined,
          SITE_URL: "",
        }),
      ),
    ).toThrow(/Sandbox.*MIRASCOPE_CLOUD.*SITE_URL/s);
  });

  it("does not throw when optional CLOUDFLARE_ACCOUNT_ID is missing", () => {
    expect(() =>
      validateEnv(makeEnv({ CLOUDFLARE_ACCOUNT_ID: undefined })),
    ).not.toThrow();
  });
});

describe("validateSiteUrl", () => {
  it.each([
    "https://mirascope.com",
    "https://openclaw.mirascope.com",
    "http://localhost",
    "http://localhost:8787",
  ])("accepts valid URL: %s", (url) => {
    expect(() => validateSiteUrl(url)).not.toThrow();
  });

  it("rejects http:// for non-localhost", () => {
    expect(() => validateSiteUrl("http://example.com")).toThrow("https://");
  });

  it("rejects trailing slash on https URL", () => {
    expect(() => validateSiteUrl("https://example.com/")).toThrow(
      "trailing slash",
    );
  });

  it("rejects trailing slash on localhost URL", () => {
    expect(() => validateSiteUrl("http://localhost:8787/")).toThrow(
      "trailing slash",
    );
  });

  it("rejects empty string", () => {
    expect(() => validateSiteUrl("")).toThrow();
  });

  it("rejects missing protocol", () => {
    expect(() => validateSiteUrl("mirascope.com")).toThrow("https://");
  });
});
