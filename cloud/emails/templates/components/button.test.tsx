import { describe, it, expect } from "vitest";
import { Effect } from "effect";
import * as React from "react";
import { Html, Body } from "@react-email/components";
import { Button } from "@/emails/templates/components/button";
import { renderReactElement } from "@/emails/render";

describe("Button", () => {
  it("renders button with href and text", () => {
    const EmailWithButton = () => (
      <Html>
        <Body>
          <Button href="https://example.com">Click Me</Button>
        </Body>
      </Html>
    );

    return Effect.gen(function* () {
      const html = yield* renderReactElement(
        React.createElement(EmailWithButton),
      );

      expect(html).toContain("Click Me");
      expect(html).toContain("https://example.com");
      expect(html).toContain("#6366f1"); // Brand color
    }).pipe(Effect.runPromise);
  });

  it("applies custom styles", () => {
    const EmailWithCustomButton = () => (
      <Html>
        <Body>
          <Button
            href="https://example.com"
            style={{ backgroundColor: "#ff0000" }}
          >
            Custom Button
          </Button>
        </Body>
      </Html>
    );

    return Effect.gen(function* () {
      const html = yield* renderReactElement(
        React.createElement(EmailWithCustomButton),
      );

      expect(html).toContain("#ff0000");
    }).pipe(Effect.runPromise);
  });
});
