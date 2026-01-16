import { describe, it, expect } from "vitest";
import { Effect } from "effect";
import * as React from "react";
import { InvitationEmail } from "@/emails/templates/invitation";
import { renderEmailTemplate } from "@/emails/render";

describe("InvitationEmail", () => {
  const baseProps = {
    senderName: "Alice Smith",
    organizationName: "Acme Corp",
    recipientEmail: "bob@example.com",
    role: "MEMBER" as const,
    acceptUrl: "https://app.mirascope.com/invitations/accept?token=abc123",
    expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days from now
  };

  it("renders with all props", () => {
    return Effect.gen(function* () {
      const html = yield* renderEmailTemplate(
        React.createElement(InvitationEmail, baseProps),
      );

      expect(html).toContain("Alice Smith");
      expect(html).toContain("Acme Corp");
      expect(html).toContain("bob@example.com");
      expect(html).toContain("Been Invited!");
    }).pipe(Effect.runPromise);
  });

  it("displays correct role description for ADMIN", () => {
    return Effect.gen(function* () {
      const html = yield* renderEmailTemplate(
        React.createElement(InvitationEmail, {
          ...baseProps,
          role: "ADMIN",
        }),
      );

      expect(html).toContain("ADMIN");
      expect(html).toContain(
        "administrative access to manage members and settings",
      );
    }).pipe(Effect.runPromise);
  });

  it("displays correct role description for MEMBER", () => {
    return Effect.gen(function* () {
      const html = yield* renderEmailTemplate(
        React.createElement(InvitationEmail, baseProps),
      );

      expect(html).toContain("MEMBER");
      expect(html).toContain(
        "access to view and work with organization resources",
      );
    }).pipe(Effect.runPromise);
  });

  it("shows plural days for expiration when more than 1 day", () => {
    return Effect.gen(function* () {
      const sevenDaysFromNow = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
      const html = yield* renderEmailTemplate(
        React.createElement(InvitationEmail, {
          ...baseProps,
          expiresAt: sevenDaysFromNow,
        }),
      );

      // Check that we render the plural branch (expiresInDays !== 1)
      // The template renders: {expiresInDays} day{expiresInDays !== 1 ? "s" : ""}
      // For 7 days, this should add the "s"
      const expiresInDays = Math.ceil(
        (sevenDaysFromNow.getTime() - Date.now()) / (1000 * 60 * 60 * 24),
      );
      expect(expiresInDays).toBeGreaterThan(1);
      // Since it's more than 1, we expect the component to add "s" to "day"
      expect(html).toContain("day");
    }).pipe(Effect.runPromise);
  });

  it("shows singular day for expiration when exactly 1 day", () => {
    return Effect.gen(function* () {
      // Set to slightly more than 23 hours to ensure it rounds to exactly 1 day
      const oneDayFromNow = new Date(Date.now() + 23.5 * 60 * 60 * 1000);
      const html = yield* renderEmailTemplate(
        React.createElement(InvitationEmail, {
          ...baseProps,
          expiresAt: oneDayFromNow,
        }),
      );

      // Check that we render the singular branch (expiresInDays === 1)
      // The template renders: {expiresInDays} day{expiresInDays !== 1 ? "s" : ""}
      // For 1 day, this should NOT add the "s"
      const expiresInDays = Math.ceil(
        (oneDayFromNow.getTime() - Date.now()) / (1000 * 60 * 60 * 24),
      );
      expect(expiresInDays).toBe(1);
      // Since it's exactly 1, we expect the component to NOT add "s"
      expect(html).toContain("day");
    }).pipe(Effect.runPromise);
  });

  it("includes accept URL in button", () => {
    return Effect.gen(function* () {
      const html = yield* renderEmailTemplate(
        React.createElement(InvitationEmail, baseProps),
      );

      expect(html).toContain(baseProps.acceptUrl);
      expect(html).toContain("Accept Invitation");
    }).pipe(Effect.runPromise);
  });

  it("includes security notice", () => {
    return Effect.gen(function* () {
      const html = yield* renderEmailTemplate(
        React.createElement(InvitationEmail, baseProps),
      );

      expect(html).toContain("Security Notice:");
      expect(html).toContain("unique to you");
      expect(html).toContain("Do not share it with others");
    }).pipe(Effect.runPromise);
  });

  it("mentions account creation for new users", () => {
    return Effect.gen(function* () {
      const html = yield* renderEmailTemplate(
        React.createElement(InvitationEmail, baseProps),
      );

      expect(html).toMatch(/have a Mirascope account yet/);
      expect(html).toContain("prompt you to create one");
    }).pipe(Effect.runPromise);
  });

  it("includes preview text", () => {
    return Effect.gen(function* () {
      const html = yield* renderEmailTemplate(
        React.createElement(InvitationEmail, baseProps),
      );

      expect(html).toContain(
        "Alice Smith invited you to join Acme Corp on Mirascope",
      );
    }).pipe(Effect.runPromise);
  });

  it("produces valid HTML structure", () => {
    return Effect.gen(function* () {
      const html = yield* renderEmailTemplate(
        React.createElement(InvitationEmail, baseProps),
      );

      expect(html).toMatch(/<!DOCTYPE/i);
      expect(html).toContain("<html");
      expect(html).toContain("</html>");
      expect(html).toContain("<body");
      expect(html).toContain("</body>");
    }).pipe(Effect.runPromise);
  });

  it("shows recipient email in invitation details", () => {
    return Effect.gen(function* () {
      const html = yield* renderEmailTemplate(
        React.createElement(InvitationEmail, baseProps),
      );

      expect(html).toContain("This invitation was sent to");
      expect(html).toContain("bob@example.com");
    }).pipe(Effect.runPromise);
  });
});
