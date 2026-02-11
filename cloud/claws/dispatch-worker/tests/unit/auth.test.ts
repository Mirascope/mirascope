/**
 * Unit tests for CORS helpers in auth.ts.
 */
import { describe, expect, it } from "vitest";

import type { DispatchEnv } from "../../src/types";

import { corsHeaders } from "../../src/auth";

function mockEnv(siteUrl: string): DispatchEnv {
  return { SITE_URL: siteUrl } as unknown as DispatchEnv;
}

describe("corsHeaders", () => {
  it("returns CORS headers for exact-match origin", () => {
    const headers = corsHeaders(
      "https://mirascope.com",
      mockEnv("https://mirascope.com"),
    );
    expect(headers["Access-Control-Allow-Origin"]).toBe(
      "https://mirascope.com",
    );
    expect(headers["Access-Control-Allow-Credentials"]).toBe("true");
  });

  it("returns empty object for mismatched origin", () => {
    const headers = corsHeaders(
      "https://staging.mirascope.com",
      mockEnv("https://mirascope.com"),
    );
    expect(headers).toEqual({});
  });

  it("returns empty object when SITE_URL is missing", () => {
    const headers = corsHeaders("https://mirascope.com", {
      SITE_URL: "",
    } as unknown as DispatchEnv);
    expect(headers).toEqual({});
  });

  it("returns empty object when SITE_URL is invalid", () => {
    const headers = corsHeaders("https://mirascope.com", {
      SITE_URL: "not-a-url",
    } as unknown as DispatchEnv);
    expect(headers).toEqual({});
  });

  it("matches origin with path against SITE_URL without path", () => {
    const headers = corsHeaders(
      "https://mirascope.com/foo",
      mockEnv("https://mirascope.com"),
    );
    expect(headers["Access-Control-Allow-Origin"]).toBe(
      "https://mirascope.com/foo",
    );
  });

  it("returns empty object for null origin", () => {
    const headers = corsHeaders(null, mockEnv("https://mirascope.com"));
    expect(headers).toEqual({});
  });
});
