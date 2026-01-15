import { describe, it, expect } from "vitest";
import { Effect } from "effect";
import * as React from "react";
import { Html, Body } from "@react-email/components";
import { Footer } from "@/emails/templates/components/footer";
import { renderReactElement } from "@/emails/render";

describe("Footer", () => {
  it("renders footer with copyright and links", () => {
    const EmailWithFooter = () => (
      <Html>
        <Body>
          <Footer />
        </Body>
      </Html>
    );

    return Effect.gen(function* () {
      const html = yield* renderReactElement(
        React.createElement(EmailWithFooter),
      );

      expect(html).toContain("Mirascope. All rights reserved");
      expect(html).toContain("https://mirascope.com");
      expect(html).toContain("https://mirascope.com/docs");
      expect(html).toContain("https://mirascope.com/discord-invite");
      expect(html).toContain(new Date().getFullYear().toString());
    }).pipe(Effect.runPromise);
  });
});
