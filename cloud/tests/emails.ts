import { Effect, Layer, Context } from "effect";
import { Resend } from "@/emails/resend-client";

// ============================================================================
// Mock Resend layer for service testing
// ============================================================================

/**
 * Creates a mock Resend layer for testing the Emails service.
 *
 * Provides a consistent way to mock the Resend client without manually
 * constructing the layer structure in each test.
 *
 * @example
 * ```ts
 * // Simple mock that returns success
 * const layer = MockResend.layer(() => Effect.succeed({ id: "email_123" }));
 *
 * // Mock that captures parameters
 * let capturedParams: unknown;
 * const layer = MockResend.layer((params) => {
 *   capturedParams = params;
 *   return Effect.succeed({ id: "email_123" });
 * });
 *
 * // Mock that returns an error
 * const layer = MockResend.layer(() =>
 *   Effect.fail(new ResendError({ message: "Failed to send" }))
 * );
 * ```
 */
export const MockResend = {
  layer: (
    sendFn: (params: unknown) => Effect.Effect<{ id: string }, unknown, never>,
  ) =>
    Layer.succeed(Resend, {
      emails: {
        send: sendFn,
      },
      config: {
        apiKey: "re_test_mock",
        audienceSegmentId: "seg_test_mock",
      },
    } as unknown as Context.Tag.Service<typeof Resend>),
};

/**
 * Creates a mock Resend layer for testing the Emails.Audience service.
 *
 * Provides a consistent way to mock the Resend audience operations without
 * manually constructing the layer structure in each test.
 *
 * @example
 * ```ts
 * // Simple mock that returns success
 * const layer = MockResendAudience.layer(() => Effect.succeed({ id: "contact_123" }));
 *
 * // Mock with custom segment ID
 * const layer = MockResendAudience.layer(
 *   () => Effect.succeed({ id: "contact_123" }),
 *   "seg_custom_123"
 * );
 *
 * // Mock that captures parameters
 * let capturedParams: unknown;
 * const layer = MockResendAudience.layer((params) => {
 *   capturedParams = params;
 *   return Effect.succeed({ id: "contact_123" });
 * });
 *
 * // Mock that returns an error
 * const layer = MockResendAudience.layer(() =>
 *   Effect.fail(new ResendError({ message: "Failed to add contact" }))
 * );
 * ```
 */
export const MockResendAudience = {
  layer: <P = unknown>(
    addFn: (params: P) => Effect.Effect<{ id: string }, unknown, never>,
    audienceSegmentId = "seg_test_mock",
    createFn: (
      params: unknown,
    ) => Effect.Effect<{ id: string; object: string }, unknown, never> = () =>
      Effect.succeed({ id: "contact_created", object: "contact" }),
  ) =>
    Layer.succeed(Resend, {
      contacts: {
        create: createFn,
        segments: {
          add: addFn as (
            params: unknown,
          ) => Effect.Effect<{ id: string }, unknown, never>,
        },
      },
      config: {
        apiKey: "re_test_mock",
        audienceSegmentId,
      },
    } as unknown as Context.Tag.Service<typeof Resend>),
};

// ============================================================================
// Test fixtures for email testing
// ============================================================================

/**
 * Factory for creating test email send request objects.
 *
 * Provides a consistent way to create send requests without manually spreading
 * or overriding properties.
 *
 * @example
 * ```ts
 * const request = TestSendRequestFixture();
 * const customRequest = TestSendRequestFixture({ from: "custom@example.com" });
 * const invalidRequest = TestSendRequestFixture({ from: "invalid" });
 * ```
 */
export function TestSendRequestFixture(
  overrides?: Partial<{
    from: string;
    to: string;
    subject: string;
    html: string;
  }>,
) {
  return {
    from: "test@example.com",
    to: "user@example.com",
    subject: "Test",
    html: "<p>Test</p>",
    ...overrides,
  };
}

/**
 * Factory for creating test email response objects.
 *
 * @example
 * ```ts
 * const email = TestEmailResponseFixture();
 * const customEmail = TestEmailResponseFixture({ id: "email_456" });
 * ```
 */
export function TestEmailResponseFixture(
  overrides?: Partial<{
    id: string;
    from: string;
    to: string;
    subject: string;
  }>,
) {
  return {
    id: "email_123",
    from: "test@example.com",
    to: "user@example.com",
    subject: "Test",
    ...overrides,
  };
}

/**
 * Factory for creating test domain create request objects.
 *
 * @example
 * ```ts
 * const request = TestDomainCreateRequestFixture();
 * const customRequest = TestDomainCreateRequestFixture({ name: "custom.com" });
 * ```
 */
export function TestDomainCreateRequestFixture(
  overrides?: Partial<{
    name: string;
  }>,
) {
  return {
    name: "example.com",
    ...overrides,
  };
}

/**
 * Factory for creating test domain response objects.
 *
 * @example
 * ```ts
 * const domain = TestDomainResponseFixture();
 * const customDomain = TestDomainResponseFixture({ status: "verified" });
 * ```
 */
export function TestDomainResponseFixture(
  overrides?: Partial<{
    id: string;
    name: string;
    status: string;
  }>,
) {
  return {
    id: "domain_123",
    name: "example.com",
    status: "pending",
    ...overrides,
  };
}

/**
 * Factory for creating test API key create request objects.
 *
 * @example
 * ```ts
 * const request = TestApiKeyCreateRequestFixture();
 * const customRequest = TestApiKeyCreateRequestFixture({ name: "Production Key" });
 * ```
 */
export function TestApiKeyCreateRequestFixture(
  overrides?: Partial<{
    name: string;
  }>,
) {
  return {
    name: "Test API Key",
    ...overrides,
  };
}

/**
 * Factory for creating test API key response objects.
 *
 * @example
 * ```ts
 * const apiKey = TestApiKeyResponseFixture();
 * const customApiKey = TestApiKeyResponseFixture({ token: "re_custom_token" });
 * ```
 */
export function TestApiKeyResponseFixture(
  overrides?: Partial<{
    id: string;
    token: string;
  }>,
) {
  return {
    id: "key_123",
    token: "re_new_token",
    ...overrides,
  };
}

/**
 * Factory for creating test email service send parameters.
 *
 * @example
 * ```ts
 * const params = TestEmailSendParamsFixture();
 * const multiRecipient = TestEmailSendParamsFixture({ to: ["user1@example.com", "user2@example.com"] });
 * const withCc = TestEmailSendParamsFixture({ cc: "cc@example.com" });
 * ```
 */
export function TestEmailSendParamsFixture(
  overrides?: Partial<{
    from: string;
    to: string | string[];
    cc?: string | string[];
    bcc?: string | string[];
    replyTo?: string | string[];
    subject: string;
    html?: string;
    text?: string;
    attachments?: Array<{ filename: string; content: string }>;
  }>,
) {
  return {
    from: "noreply@example.com",
    to: "user@example.com",
    subject: "Test Email",
    html: "<p>Test content</p>",
    ...overrides,
  };
}

/**
 * Factory for creating test email service send response.
 *
 * @example
 * ```ts
 * const response = TestEmailSendResponseFixture();
 * const customResponse = TestEmailSendResponseFixture({ id: "email_custom_456" });
 * ```
 */
export function TestEmailSendResponseFixture(
  overrides?: Partial<{
    id: string;
  }>,
) {
  return {
    id: "email_test_123",
    ...overrides,
  };
}

/**
 * Factory for creating test audience add parameters.
 *
 * @example
 * ```ts
 * const params = TestAudienceAddParamsFixture();
 * const customParams = TestAudienceAddParamsFixture({ email: "custom@example.com" });
 * ```
 */
export function TestAudienceAddParamsFixture(
  overrides?: Partial<{
    email: string;
    segmentId: string;
  }>,
) {
  return {
    email: "user@example.com",
    segmentId: "seg_test_mock",
    ...overrides,
  };
}

/**
 * Factory for creating test audience add response.
 *
 * @example
 * ```ts
 * const response = TestAudienceAddResponseFixture();
 * const customResponse = TestAudienceAddResponseFixture({ id: "contact_456" });
 * ```
 */
export function TestAudienceAddResponseFixture(
  overrides?: Partial<{
    id: string;
  }>,
) {
  return {
    id: "contact_test_123",
    ...overrides,
  };
}
