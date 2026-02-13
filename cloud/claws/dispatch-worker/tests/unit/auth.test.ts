/**
 * Unit tests for CORS helpers in auth.ts.
 */
import { describe, expect, it } from "vitest";

import type { DispatchEnv } from "../../src/types";

import { corsHeaders, handlePreflight } from "../../src/auth";

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
    expect(headers["Vary"]).toBe("Origin");
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

  it("normalizes default HTTPS port (443)", () => {
    const headers = corsHeaders(
      "https://mirascope.com:443",
      mockEnv("https://mirascope.com"),
    );
    expect(headers["Access-Control-Allow-Origin"]).toBe(
      "https://mirascope.com:443",
    );
  });

  it("normalizes default HTTP port (80)", () => {
    const headers = corsHeaders(
      "http://mirascope.com:80",
      mockEnv("http://mirascope.com"),
    );
    expect(headers["Access-Control-Allow-Origin"]).toBe(
      "http://mirascope.com:80",
    );
  });

  it("does not match different non-default ports", () => {
    const headers = corsHeaders(
      "https://mirascope.com:8443",
      mockEnv("https://mirascope.com:9443"),
    );
    expect(headers).toEqual({});
  });

  describe("with preflight headers", () => {
    it("includes preflight headers when requested", () => {
      const headers = corsHeaders(
        "https://mirascope.com",
        mockEnv("https://mirascope.com"),
        true,
      );
      expect(headers["Access-Control-Allow-Methods"]).toBe(
        "GET, POST, PUT, PATCH, DELETE, OPTIONS",
      );
      expect(headers["Access-Control-Allow-Headers"]).toBe(
        "Authorization, Content-Type",
      );
      expect(headers["Access-Control-Max-Age"]).toBe("86400");
    });

    it("echoes requested headers from browser", () => {
      const headers = corsHeaders(
        "https://mirascope.com",
        mockEnv("https://mirascope.com"),
        true,
        "Authorization, X-Request-ID, X-Custom-Header",
      );
      expect(headers["Access-Control-Allow-Headers"]).toBe(
        "Authorization, X-Request-ID, X-Custom-Header",
      );
    });

    it("uses default headers when none requested", () => {
      const headers = corsHeaders(
        "https://mirascope.com",
        mockEnv("https://mirascope.com"),
        true,
        null,
      );
      expect(headers["Access-Control-Allow-Headers"]).toBe(
        "Authorization, Content-Type",
      );
    });
  });
});

describe("handlePreflight", () => {
  it("returns null for non-OPTIONS requests", () => {
    const request = new Request("https://example.com", {
      method: "GET",
      headers: { Origin: "https://mirascope.com" },
    });
    expect(
      handlePreflight(request, mockEnv("https://mirascope.com")),
    ).toBeNull();
  });

  it("returns 204 for OPTIONS without Origin header", () => {
    const request = new Request("https://example.com", {
      method: "OPTIONS",
    });
    const response = handlePreflight(request, mockEnv("https://mirascope.com"));
    expect(response?.status).toBe(204);
  });

  it("returns 204 with CORS headers for allowed origin", async () => {
    const request = new Request("https://example.com", {
      method: "OPTIONS",
      headers: { Origin: "https://mirascope.com" },
    });
    const response = handlePreflight(request, mockEnv("https://mirascope.com"));
    expect(response?.status).toBe(204);
    expect(response?.headers.get("Access-Control-Allow-Origin")).toBe(
      "https://mirascope.com",
    );
    expect(response?.headers.get("Access-Control-Max-Age")).toBe("86400");
    expect(response?.headers.get("Vary")).toBe("Origin");
  });

  it("returns 403 without CORS headers for disallowed origin", () => {
    const request = new Request("https://example.com", {
      method: "OPTIONS",
      headers: { Origin: "https://evil.com" },
    });
    const response = handlePreflight(request, mockEnv("https://mirascope.com"));
    expect(response?.status).toBe(403);
    // Should NOT include CORS headers for rejected origins (security)
    expect(response?.headers.get("Access-Control-Allow-Origin")).toBeNull();
    expect(response?.headers.get("Vary")).toBeNull();
  });

  it("echoes requested headers in preflight response", () => {
    const request = new Request("https://example.com", {
      method: "OPTIONS",
      headers: {
        Origin: "https://mirascope.com",
        "Access-Control-Request-Headers": "Authorization, X-Request-ID",
      },
    });
    const response = handlePreflight(request, mockEnv("https://mirascope.com"));
    expect(response?.headers.get("Access-Control-Allow-Headers")).toBe(
      "Authorization, X-Request-ID",
    );
  });
});
