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
