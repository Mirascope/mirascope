import { describe, it, expect } from "vitest";
import { Effect } from "effect";
import * as React from "react";
import { Html, Body } from "@react-email/components";
import { Logo } from "@/emails/templates/components/logo";
import { renderEmailTemplate } from "@/emails/render";

describe("Logo", () => {
  it("renders logo image with correct attributes", () => {
    const EmailWithLogo = () => (
      <Html>
        <Body>
          <Logo />
        </Body>
      </Html>
    );

    return Effect.gen(function* () {
      const html = yield* renderEmailTemplate(
        React.createElement(EmailWithLogo),
      );

      expect(html).toContain("Mirascope");
      expect(html).toContain("logo.svg");
      expect(html).toContain('width="64"');
      expect(html).toContain('height="64"');
      expect(html).toContain('alt="Mirascope"');
    }).pipe(Effect.runPromise);
  });
});
