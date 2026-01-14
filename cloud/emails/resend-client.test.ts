import { describe, it, expect, vi, beforeEach, assert } from "vitest";
import { Effect, Layer } from "effect";
import { Resend, wrapResendClient } from "@/emails/resend-client";
import { ResendError, ConfigError } from "@/errors";
import { Resend as ResendAPI } from "resend";
import {
  TestSendRequestFixture,
  TestEmailResponseFixture,
  TestDomainCreateRequestFixture,
  TestDomainResponseFixture,
  TestApiKeyCreateRequestFixture,
  TestApiKeyResponseFixture,
} from "@/tests/emails";

// Mock the Resend SDK
vi.mock("resend", () => {
  const MockResend = vi.fn();
  return {
    Resend: MockResend,
  };
});

// Type for our mock Resend instance
interface MockResendInstance {
  emails: {
    send: ReturnType<typeof vi.fn>;
    create: ReturnType<typeof vi.fn>;
    get: ReturnType<typeof vi.fn>;
    list: ReturnType<typeof vi.fn>;
    update: ReturnType<typeof vi.fn>;
    cancel: ReturnType<typeof vi.fn>;
  };
  domains: {
    create: ReturnType<typeof vi.fn>;
    get: ReturnType<typeof vi.fn>;
    list: ReturnType<typeof vi.fn>;
    update: ReturnType<typeof vi.fn>;
    remove: ReturnType<typeof vi.fn>;
  };
  apiKeys: {
    create: ReturnType<typeof vi.fn>;
    list: ReturnType<typeof vi.fn>;
    remove: ReturnType<typeof vi.fn>;
  };
  key: string;
  _internal?: string;
  [key: symbol]: unknown;
}

// Type for the wrapped Resend client that includes internal properties we test
type WrappedResendForTest = ReturnType<typeof wrapResendClient> & {
  key: string;
  _internal: string;
  [key: symbol]: unknown;
};

describe("Resend", () => {
  let mockResend: MockResendInstance;

  beforeEach(() => {
    // Reset mocks before each test
    vi.clearAllMocks();

    // Create a mock Resend instance with nested structure
    mockResend = {
      emails: {
        send: vi.fn(),
        create: vi.fn(),
        get: vi.fn(),
        list: vi.fn(),
        update: vi.fn(),
        cancel: vi.fn(),
      },
      domains: {
        create: vi.fn(),
        get: vi.fn(),
        list: vi.fn(),
        update: vi.fn(),
        remove: vi.fn(),
      },
      apiKeys: {
        create: vi.fn(),
        list: vi.fn(),
        remove: vi.fn(),
      },
      key: "re_test_mock",
    };

    // Mock Resend constructor to return our mock instance.
    // Note: Must use regular function in vitest v4 (not arrow) because it's called with `new`
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-member-access
    (ResendAPI as any).mockImplementation(function () {
      return mockResend;
    });
  });

  // ===========================================================================
  // Layer Creation
  // ===========================================================================

  describe("layer", () => {
    it("creates a layer with provided configuration", () => {
      const layer = Resend.layer({
        apiKey: "re_test_mock",
      });

      expect(layer).toBeDefined();
      expect(Layer.isLayer(layer)).toBe(true);
    });

    it("validates configuration and creates client", () => {
      const layer = Resend.layer({
        apiKey: "re_test_mock",
      });

      expect(layer).toBeDefined();

      // Return an effect that accesses Resend, which will trigger layer initialization
      return Effect.gen(function* () {
        const resend = yield* Resend;

        // Accessing the resend service should have triggered constructor call
        expect(ResendAPI).toHaveBeenCalledWith("re_test_mock");

        // Verify the service is properly configured
        expect(resend.config.apiKey).toBe("re_test_mock");
      }).pipe(Effect.provide(layer), Effect.runPromise);
    });

    it("validates configuration and fails with missing apiKey", () => {
      const result = Effect.runSync(
        Layer.launch(Resend.layer({})).pipe(Effect.flip),
      );

      assert(result instanceof ConfigError);
      expect(result.message).toContain("Missing or empty fields");
      expect(result.message).toContain("apiKey");
    });

    it("validates configuration and fails with empty apiKey", () => {
      const result = Effect.runSync(
        Layer.launch(Resend.layer({ apiKey: "" })).pipe(Effect.flip),
      );

      assert(result instanceof ConfigError);
      expect(result.message).toContain("Missing or empty fields");
      expect(result.message).toContain("apiKey");
    });

    it("validates configuration and fails with whitespace-only apiKey", () => {
      const result = Effect.runSync(
        Layer.launch(Resend.layer({ apiKey: "   " })).pipe(Effect.flip),
      );

      assert(result instanceof ConfigError);
      expect(result.message).toContain("Missing or empty fields");
      expect(result.message).toContain("apiKey");
    });
  });

  // ===========================================================================
  // Proxy Wrapper Behavior
  // ===========================================================================

  describe("wrapResendClient", () => {
    beforeEach(() => {
      mockResend.emails.send.mockResolvedValue({
        data: { id: "email_123" },
        error: null,
      });
    });

    it("wraps successful method calls to return Effects with unwrapped data", async () => {
      const wrapped = wrapResendClient(mockResend as unknown as ResendAPI);
      const request = TestSendRequestFixture({ html: "<p>Test email</p>" });

      await Effect.gen(function* () {
        const result = yield* wrapped.emails.send(request);

        // Should unwrap Response<T> and return just the data
        expect(result).toEqual({ id: "email_123" });
        expect(mockResend.emails.send).toHaveBeenCalledWith(request);
      }).pipe(Effect.runPromise);
    });

    it("converts Resend errors to ResendError", async () => {
      // Mock an error response from Resend API
      mockResend.emails.send.mockResolvedValue({
        data: null,
        error: {
          message: "Invalid email address",
          name: "validation_error",
        },
      });

      const wrapped = wrapResendClient(mockResend as unknown as ResendAPI);

      await Effect.gen(function* () {
        const result = yield* wrapped.emails
          .send(TestSendRequestFixture({ from: "invalid" }))
          .pipe(Effect.flip);

        assert(result instanceof ResendError);
        expect(result.message).toContain("Invalid email address");
      }).pipe(Effect.runPromise);
    });

    it("converts thrown exceptions to ResendError", async () => {
      // Mock a network error or other exception
      mockResend.emails.send.mockRejectedValue(
        new Error("Network error: connection timeout"),
      );

      const wrapped = wrapResendClient(mockResend as unknown as ResendAPI);

      await Effect.gen(function* () {
        const result = yield* wrapped.emails
          .send(TestSendRequestFixture())
          .pipe(Effect.flip);

        assert(result instanceof ResendError);
        expect(result.message).toContain("Network error");
      }).pipe(Effect.runPromise);
    });

    it("preserves nested resource structure", () => {
      const wrapped = wrapResendClient(mockResend as unknown as ResendAPI);

      // Verify nested resources are accessible
      expect(wrapped.emails).toBeDefined();
      expect(wrapped.domains).toBeDefined();
      expect(wrapped.apiKeys).toBeDefined();

      // Verify nested methods return Effects
      const effect = wrapped.emails.send(TestSendRequestFixture());

      expect(Effect.isEffect(effect)).toBe(true);
    });

    it("caches wrapped objects to preserve identity", () => {
      const wrapped = wrapResendClient(mockResend as unknown as ResendAPI);

      // Access the same nested object multiple times
      const emails1 = wrapped.emails;
      const emails2 = wrapped.emails;

      // Should return the same wrapped object (cached)
      expect(emails1).toBe(emails2);
    });

    it("passes through non-function, non-object properties", () => {
      const wrapped = wrapResendClient(
        mockResend as unknown as ResendAPI,
      ) as WrappedResendForTest;

      // Primitive properties should pass through unchanged
      expect(wrapped.key).toBe("re_test_mock");
    });

    it("skips wrapping internal properties starting with underscore", () => {
      mockResend._internal = "internal_value";
      const wrapped = wrapResendClient(
        mockResend as unknown as ResendAPI,
      ) as WrappedResendForTest;

      // Internal properties should pass through unchanged
      expect(wrapped._internal).toBe("internal_value");
    });

    it("skips wrapping symbol properties", () => {
      const testSymbol = Symbol("test");
      mockResend[testSymbol] = "symbol_value";

      const wrapped = wrapResendClient(
        mockResend as unknown as ResendAPI,
      ) as WrappedResendForTest;

      // Symbol properties should pass through unchanged
      expect(wrapped[testSymbol]).toBe("symbol_value");
    });

    it("includes full method path in error messages", async () => {
      // Mock an error that doesn't return Response<T> format (thrown exception)
      mockResend.emails.send.mockRejectedValue(
        new Error("API rate limit exceeded"),
      );

      const wrapped = wrapResendClient(mockResend as unknown as ResendAPI);

      await Effect.gen(function* () {
        const result = yield* wrapped.emails
          .send(TestSendRequestFixture())
          .pipe(Effect.flip);

        assert(result instanceof ResendError);
        // Error message should include the method that was called
        expect(result.message).toContain("API rate limit exceeded");
      }).pipe(Effect.runPromise);
    });
  });

  // ===========================================================================
  // Multiple Resource Types
  // ===========================================================================

  describe("multiple resource types", () => {
    it("wraps emails resource correctly", async () => {
      const emailResponse = TestEmailResponseFixture();
      mockResend.emails.get.mockResolvedValue({
        data: emailResponse,
        error: null,
      });

      const wrapped = wrapResendClient(mockResend as unknown as ResendAPI);

      await Effect.gen(function* () {
        const email = yield* wrapped.emails.get("email_123");

        expect(email).toEqual(emailResponse);
        expect(mockResend.emails.get).toHaveBeenCalledWith("email_123");
      }).pipe(Effect.runPromise);
    });

    it("wraps domains resource correctly", async () => {
      const domainRequest = TestDomainCreateRequestFixture();
      const domainResponse = TestDomainResponseFixture();
      mockResend.domains.create.mockResolvedValue({
        data: domainResponse,
        error: null,
      });

      const wrapped = wrapResendClient(mockResend as unknown as ResendAPI);

      await Effect.gen(function* () {
        const domain = yield* wrapped.domains.create(domainRequest);

        expect(domain).toEqual(domainResponse);
        expect(mockResend.domains.create).toHaveBeenCalledWith(domainRequest);
      }).pipe(Effect.runPromise);
    });

    it("wraps apiKeys resource correctly", async () => {
      const apiKeyRequest = TestApiKeyCreateRequestFixture();
      const apiKeyResponse = TestApiKeyResponseFixture();
      mockResend.apiKeys.create.mockResolvedValue({
        data: apiKeyResponse,
        error: null,
      });

      const wrapped = wrapResendClient(mockResend as unknown as ResendAPI);

      await Effect.gen(function* () {
        const apiKey = yield* wrapped.apiKeys.create(apiKeyRequest);

        expect(apiKey).toEqual(apiKeyResponse);
        expect(mockResend.apiKeys.create).toHaveBeenCalledWith(apiKeyRequest);
      }).pipe(Effect.runPromise);
    });
  });

  // ===========================================================================
  // Error Handling Edge Cases
  // ===========================================================================

  describe("error handling edge cases", () => {
    it("handles errors with no message property", async () => {
      // Mock an error that's not a standard Error object
      mockResend.emails.send.mockRejectedValue({ code: "UNKNOWN" });

      const wrapped = wrapResendClient(mockResend as unknown as ResendAPI);

      await Effect.gen(function* () {
        const result = yield* wrapped.emails
          .send(TestSendRequestFixture())
          .pipe(Effect.flip);

        assert(result instanceof ResendError);
        // Should still create an error with a generic message
        expect(result.message).toContain("Resend API call failed");
        expect(result.message).toContain("resend.emails.send");
      }).pipe(Effect.runPromise);
    });

    it("handles non-Response format returns gracefully", async () => {
      // Some methods might not return Response<T> format (like verify)
      mockResend.emails.send.mockResolvedValue({ id: "direct_value" });

      const wrapped = wrapResendClient(mockResend as unknown as ResendAPI);

      await Effect.gen(function* () {
        const result = yield* wrapped.emails.send(TestSendRequestFixture());

        // Should return the value as-is if it doesn't match Response<T> format
        expect(result).toEqual({ id: "direct_value" });
      }).pipe(Effect.runPromise);
    });
  });
});
