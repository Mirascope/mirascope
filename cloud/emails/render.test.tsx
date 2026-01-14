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

import { renderEmailTemplate } from "@/emails/render";
import { render } from "@react-email/render";

describe("renderEmailTemplate", () => {
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
      const html = yield* renderEmailTemplate(React.createElement(SimpleEmail));

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
      const html = yield* renderEmailTemplate(
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
      const html = yield* renderEmailTemplate(
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
      const result = yield* renderEmailTemplate(
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
      const result = yield* renderEmailTemplate(
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
      const result = yield* renderEmailTemplate(
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
      const html = yield* renderEmailTemplate(React.createElement(ValidEmail));

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
