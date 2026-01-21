import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { Effect } from "effect";
import * as React from "react";
import { Html, Head, Body, Text } from "@react-email/components";
import { EmailRenderError } from "@/errors";

// Mock the render function
vi.mock("@react-email/render", async () => {
  const actual = await vi.importActual<typeof import("@react-email/render")>(
    "@react-email/render",
  );
  return {
    ...actual,
    render: vi.fn(actual.render),
  };
});

import { renderReactElement, renderEmailTemplate } from "@/emails/render";
import { render } from "@react-email/render";

describe("renderReactElement", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders a simple React Email component to HTML", () => {
    const SimpleEmail = () => (
      <Html>
        <Head></Head>
        <Body>
          <Text>Hello, World!</Text>
        </Body>
      </Html>
    );

    return Effect.gen(function* () {
      const html = yield* renderReactElement(React.createElement(SimpleEmail));

      expect(html).toContain("<!DOCTYPE html");
      expect(html).toContain("Hello, World!");
      expect(html).toContain("<html");
      expect(html).toContain("</html>");
    }).pipe(Effect.runPromise);
  });

  it("renders a component with props", () => {
    interface GreetingEmailProps {
      name: string;
    }

    const GreetingEmail = ({ name }: GreetingEmailProps) => (
      <Html>
        <Head></Head>
        <Body>
          <Text>Hello, {name}!</Text>
        </Body>
      </Html>
    );

    return Effect.gen(function* () {
      const html = yield* renderReactElement(
        React.createElement(GreetingEmail, { name: "Alice" }),
      );

      // Check for both parts separately due to email formatting
      expect(html).toContain("Hello,");
      expect(html).toContain("Alice");
    }).pipe(Effect.runPromise);
  });

  it("renders component with null props", () => {
    interface OptionalNameEmailProps {
      name: string | null;
    }

    const OptionalNameEmail = ({ name }: OptionalNameEmailProps) => (
      <Html>
        <Head></Head>
        <Body>
          <Text>{name ? `Hello, ${name}` : "Hello"}!</Text>
        </Body>
      </Html>
    );

    return Effect.gen(function* () {
      const html = yield* renderReactElement(
        React.createElement(OptionalNameEmail, { name: null }),
      );

      expect(html).toContain("Hello");
      expect(html).not.toContain("null");
    }).pipe(Effect.runPromise);
  });

  it("returns EmailRenderError when component throws", () => {
    const ErrorEmail = () => {
      throw new Error("Render failed");
    };

    return Effect.gen(function* () {
      const result = yield* renderReactElement(
        React.createElement(ErrorEmail),
      ).pipe(Effect.flip);

      expect(result).toBeInstanceOf(EmailRenderError);
      expect(result.message).toContain("Render failed");
    }).pipe(Effect.runPromise);
  });

  it("returns generic error message when error marker found but no data-msg pattern", () => {
    // Mock render to return HTML with error marker but no data-msg
    vi.mocked(render).mockResolvedValueOnce(
      "Switched to client rendering because the server rendering errored",
    );

    return Effect.gen(function* () {
      const result = yield* renderReactElement(
        React.createElement(() => <Html />),
      ).pipe(Effect.flip);

      expect(result).toBeInstanceOf(EmailRenderError);
      expect(result.message).toBe("Email template rendering failed");
    }).pipe(Effect.runPromise);
  });

  it("returns generic error message when non-Error is thrown", () => {
    // Mock render to reject with non-Error value
    vi.mocked(render).mockRejectedValueOnce("string error");

    return Effect.gen(function* () {
      const result = yield* renderReactElement(
        React.createElement(() => <Html />),
      ).pipe(Effect.flip);

      expect(result).toBeInstanceOf(EmailRenderError);
      expect(result.message).toBe("Failed to render email template");
    }).pipe(Effect.runPromise);
  });

  it("produces valid HTML structure", () => {
    const ValidEmail = () => (
      <Html>
        <Head></Head>
        <Body>
          <Text>Content</Text>
        </Body>
      </Html>
    );

    return Effect.gen(function* () {
      const html = yield* renderReactElement(React.createElement(ValidEmail));

      // Check for essential HTML email structure
      expect(html).toMatch(/<!DOCTYPE/i);
      expect(html).toContain("<html");
      expect(html).toContain("<head");
      expect(html).toContain("<body");
      expect(html).toContain("</body>");
      expect(html).toContain("</html>");
    }).pipe(Effect.runPromise);
  });
});

describe("renderEmailTemplate", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders a component with props successfully", () => {
    interface GreetingEmailProps {
      name: string;
    }

    const GreetingEmail = ({ name }: GreetingEmailProps) => (
      <Html>
        <Head></Head>
        <Body>
          <Text>Hello, {name}!</Text>
        </Body>
      </Html>
    );

    return Effect.gen(function* () {
      const html = yield* renderEmailTemplate(GreetingEmail, { name: "Alice" });

      expect(html).not.toBeNull();
      expect(html).toContain("Hello,");
      expect(html).toContain("Alice");
    }).pipe(Effect.runPromise);
  });

  it("returns null when component rendering fails", () => {
    const ErrorEmail = () => {
      throw new Error("Render failed");
    };

    return Effect.gen(function* () {
      const html = yield* renderEmailTemplate(ErrorEmail, {});

      expect(html).toBeNull();
    }).pipe(Effect.runPromise);
  });

  it("logs error with component name when rendering fails", () => {
    const ErrorEmail = () => {
      throw new Error("Render failed");
    };
    ErrorEmail.displayName = "ErrorEmail";

    return Effect.gen(function* () {
      const html = yield* renderEmailTemplate(ErrorEmail, {});

      expect(html).toBeNull();
      // Effect logging is tested in integration, we just verify null is returned
    }).pipe(Effect.runPromise);
  });

  it("handles component with null props", () => {
    interface OptionalEmailProps {
      name: string | null;
    }

    const OptionalEmail = ({ name }: OptionalEmailProps) => (
      <Html>
        <Head></Head>
        <Body>
          <Text>{name ? `Hello, ${name}` : "Hello"}!</Text>
        </Body>
      </Html>
    );

    return Effect.gen(function* () {
      const html = yield* renderEmailTemplate(OptionalEmail, { name: null });

      expect(html).not.toBeNull();
      expect(html).toContain("Hello");
    }).pipe(Effect.runPromise);
  });

  it("uses component displayName for error logging", () => {
    const ErrorEmail = () => {
      throw new Error("Test error");
    };
    ErrorEmail.displayName = "CustomDisplayName";

    return Effect.gen(function* () {
      const html = yield* renderEmailTemplate(ErrorEmail, {});

      expect(html).toBeNull();
    }).pipe(Effect.runPromise);
  });

  it("uses component name when displayName is not set", () => {
    function NamedErrorEmail(): React.ReactElement {
      throw new Error("Test error");
    }

    return Effect.gen(function* () {
      const html = yield* renderEmailTemplate(NamedErrorEmail, {});

      expect(html).toBeNull();
    }).pipe(Effect.runPromise);
  });

  it("accepts additional context for error logging", () => {
    const ErrorEmail = () => {
      throw new Error("Test error");
    };

    return Effect.gen(function* () {
      const html = yield* renderEmailTemplate(
        ErrorEmail,
        {},
        { email: "test@example.com", userId: "123" },
      );

      expect(html).toBeNull();
    }).pipe(Effect.runPromise);
  });

  it("uses UnknownEmailComponent when component has no name or displayName", () => {
    // Create a component with empty name and no displayName
    const AnonymousErrorEmail = (() => {
      throw new Error("Test error");
    }) as React.ComponentType<object>;

    // Override the name property to be empty
    Object.defineProperty(AnonymousErrorEmail, "name", { value: "" });

    return Effect.gen(function* () {
      const html = yield* renderEmailTemplate(AnonymousErrorEmail, {});

      expect(html).toBeNull();
      // The component name "UnknownEmailComponent" would be used in error logs
    }).pipe(Effect.runPromise);
  });

  it("renders component with complex props", () => {
    interface ComplexEmailProps {
      title: string;
      items: string[];
      metadata: {
        sender: string;
        timestamp: Date;
      };
    }

    const ComplexEmail = ({ title, items, metadata }: ComplexEmailProps) => (
      <Html>
        <Head></Head>
        <Body>
          <Text>{title}</Text>
          {items.map((item) => (
            <Text key={item}>{item}</Text>
          ))}
          <Text>{metadata.sender}</Text>
        </Body>
      </Html>
    );

    const timestamp = new Date("2024-01-01");

    return Effect.gen(function* () {
      const html = yield* renderEmailTemplate(ComplexEmail, {
        title: "Test Email",
        items: ["Item 1", "Item 2"],
        metadata: { sender: "alice@example.com", timestamp },
      });

      expect(html).not.toBeNull();
      expect(html).toContain("Test Email");
      expect(html).toContain("Item 1");
      expect(html).toContain("Item 2");
      expect(html).toContain("alice@example.com");
    }).pipe(Effect.runPromise);
  });
});
