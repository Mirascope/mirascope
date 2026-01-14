import { Effect } from "effect";
import { render } from "@react-email/render";
import * as React from "react";
import { EmailRenderError } from "@/errors";

/**
 * Renders a React Email component to HTML string.
 *
 * This is an Effect-native wrapper around @react-email/render's render()
 * function, enabling seamless integration with the existing Effect-based
 * email service architecture.
 *
 * @param component - React Email component to render
 * @returns Effect that yields HTML string or EmailRenderError
 *
 * @example
 * ```ts
 * const htmlEffect = renderEmailTemplate(
 *   React.createElement(WelcomeEmail, { name: "Alice" })
 * );
 * const html = yield* htmlEffect;
 * ```
 */
export function renderEmailTemplate(
  component: React.ReactElement,
): Effect.Effect<string, EmailRenderError> {
  return Effect.tryPromise({
    try: async () => {
      const html = await render(component);

      // React Email embeds errors in HTML rather than throwing
      // Detect error markers and throw an error instead
      if (
        html.includes(
          "Switched to client rendering because the server rendering errored",
        ) ||
        html.includes("data-msg=")
      ) {
        // Extract error message from HTML if possible
        const msgMatch = html.match(/data-msg="([^"]+)"/);
        const errorMessage = msgMatch
          ? msgMatch[1]
          : "Email template rendering failed";
        throw new Error(errorMessage);
      }

      return html;
    },
    catch: (error) => {
      const message =
        error instanceof Error
          ? error.message
          : "Failed to render email template";
      return new EmailRenderError({ message, cause: error });
    },
  });
}
