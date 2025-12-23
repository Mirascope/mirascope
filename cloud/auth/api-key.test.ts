import { getApiKeyFromRequest, API_KEY_HEADER } from "@/auth/api-key";
import { describe, it, expect } from "@/tests/auth";


describe("getApiKeyFromRequest", () => {
  it("should extract API key from X-API-Key header", () => {
    const request = new Request("http://localhost/api", {
      headers: { [API_KEY_HEADER]: "mk_test_key" },
    });

    expect(getApiKeyFromRequest(request)).toBe("mk_test_key");
  });

  it("should extract API key from Authorization Bearer header", () => {
    const request = new Request("http://localhost/api", {
      headers: { Authorization: "Bearer mk_test_key" },
    });

    expect(getApiKeyFromRequest(request)).toBe("mk_test_key");
  });

  it("should prefer X-API-Key over Authorization header", () => {
    const request = new Request("http://localhost/api", {
      headers: {
        [API_KEY_HEADER]: "mk_from_header",
        Authorization: "Bearer mk_from_auth",
      },
    });

    expect(getApiKeyFromRequest(request)).toBe("mk_from_header");
  });

  it("should return null if no API key provided", () => {
    const request = new Request("http://localhost/api");

    expect(getApiKeyFromRequest(request)).toBeNull();
  });

  it("should return null for non-Bearer Authorization header", () => {
    const request = new Request("http://localhost/api", {
      headers: { Authorization: "Basic dXNlcjpwYXNz" },
    });

    expect(getApiKeyFromRequest(request)).toBeNull();
  });
});
