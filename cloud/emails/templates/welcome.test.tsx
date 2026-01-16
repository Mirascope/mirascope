import { describe, it, expect } from "vitest";
import { Effect } from "effect";
import * as React from "react";
import { WelcomeEmail } from "@/emails/templates/welcome";
import { renderReactElement } from "@/emails/render";

describe("WelcomeEmail", () => {
  it("renders with user name", () => {
    return Effect.gen(function* () {
      const html = yield* renderReactElement(
        React.createElement(WelcomeEmail, { name: "Alice" }),
      );

      expect(html).toContain("Hi Alice");
      expect(html).toContain("Welcome to Mirascope Cloud!");
      expect(html).toContain("founder of Mirascope");
    }).pipe(Effect.runPromise);
  });

  it("renders without user name", () => {
    return Effect.gen(function* () {
      const html = yield* renderReactElement(
        React.createElement(WelcomeEmail, { name: null }),
      );

      expect(html).toContain("Hello");
      expect(html).not.toContain("Hi null");
      expect(html).toContain("Welcome to Mirascope Cloud!");
    }).pipe(Effect.runPromise);
  });

  it("includes documentation link", () => {
    return Effect.gen(function* () {
      const html = yield* renderReactElement(
        React.createElement(WelcomeEmail, { name: "Bob" }),
      );

      expect(html).toContain("https://mirascope.com/docs");
      expect(html).toContain("View Documentation");
    }).pipe(Effect.runPromise);
  });

  it("includes Discord invite link", () => {
    return Effect.gen(function* () {
      const html = yield* renderReactElement(
        React.createElement(WelcomeEmail, { name: "Charlie" }),
      );

      expect(html).toContain("https://mirascope.com/discord-invite");
      expect(html).toContain("Join Our Discord");
    }).pipe(Effect.runPromise);
  });

  it("includes credit incentive information", () => {
    return Effect.gen(function* () {
      const html = yield* renderReactElement(
        React.createElement(WelcomeEmail, { name: "Dana" }),
      );

      expect(html).toContain("$5");
      expect(html).toContain("$20");
      expect(html).toContain("Earn Up to $30 in Credits");
      expect(html).toContain("introduce yourself");
      expect(html).toContain("show-and-tell");
      expect(html).toContain("user interview");
    }).pipe(Effect.runPromise);
  });

  it("includes founder signature", () => {
    return Effect.gen(function* () {
      const html = yield* renderReactElement(
        React.createElement(WelcomeEmail, { name: "Eve" }),
      );

      expect(html).toContain("William Bakst");
      expect(html).toContain("Founder &amp; CEO");
      expect(html).toContain("Mirascope, Inc.");
    }).pipe(Effect.runPromise);
  });

  it("includes preview text", () => {
    return Effect.gen(function* () {
      const html = yield* renderReactElement(
        React.createElement(WelcomeEmail, { name: "Frank" }),
      );

      // Preview text is used by email clients for inbox preview
      expect(html).toContain(
        "Welcome to Mirascope Cloud - Get Started with $30 in Credits",
      );
    }).pipe(Effect.runPromise);
  });

  it("produces valid HTML structure", () => {
    return Effect.gen(function* () {
      const html = yield* renderReactElement(
        React.createElement(WelcomeEmail, { name: "Grace" }),
      );

      expect(html).toMatch(/<!DOCTYPE/i);
      expect(html).toContain("<html");
      expect(html).toContain("</html>");
      expect(html).toContain("<body");
      expect(html).toContain("</body>");
    }).pipe(Effect.runPromise);
  });

  it("includes personal touch message", () => {
    return Effect.gen(function* () {
      const html = yield* renderReactElement(
        React.createElement(WelcomeEmail, { name: "Hannah" }),
      );

      expect(html).toContain("Just reply to this email");
      expect(html).toContain("I read and respond to every message personally");
    }).pipe(Effect.runPromise);
  });
});
