import { Effect } from "effect";
import { render } from "@react-email/render";
import * as React from "react";
import { EmailRenderError } from "@/errors";

/**
 * Renders a React Email element to HTML string.
 *
 * Low-level function that takes a React element and renders it to HTML.
 * This is an Effect-native wrapper around @react-email/render's render()
 * function.
 *
 * @internal - Use `renderEmailTemplate` instead for most cases. This is
 * exported primarily for testing purposes.
 * @param element - React Email element to render
 * @returns Effect that yields HTML string or EmailRenderError
 */
export function renderReactElement(
  element: React.ReactElement,
): Effect.Effect<string, EmailRenderError> {
  return Effect.tryPromise({
    try: async () => {
      const html = await render(element);

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

/**
 * Renders an email template with automatic error handling.
 *
 * Takes a React Email component and its props, renders it to HTML with
 * built-in error handling:
 * - Creates the React element from the component and props
 * - Handles rendering errors gracefully by logging and returning null
 * - Extracts the component name for better error messages
 *
 * @param Component - React Email component type
 * @param props - Props for the component
 * @param additionalContext - Optional additional context for error logging
 * @returns Effect that yields HTML string or null on error
 *
 * @example
 * ```ts
 * const html = yield* renderEmailTemplate(
 *   InvitationEmail,
 *   { senderName: "Alice", organizationName: "Acme", ... },
 *   { recipientEmail: "bob@example.com" }
 * );
 *
 * if (html !== null) {
 *   // Send email
 * }
 * ```
 */
export function renderEmailTemplate<P extends object>(
  Component: React.ComponentType<P>,
  props: P,
  additionalContext?: Record<string, unknown>,
): Effect.Effect<string | null, never> {
  const componentName =
    Component.displayName || Component.name || "UnknownEmailComponent";

  return renderReactElement(React.createElement(Component, props)).pipe(
    Effect.catchAll((error) =>
      Effect.gen(function* () {
        yield* Effect.logError(
          `Failed to render ${componentName} template`,
        ).pipe(
          Effect.annotateLogs({
            error: String(error),
            component: componentName,
            ...additionalContext,
          }),
        );
        return null;
      }),
    ),
  );
}
