/**
 * @fileoverview Emails service layer.
 *
 * This module provides the `Emails` service which wraps Resend for sending
 * transactional emails and managing marketing audience through Effect's dependency injection system.
 *
 * ## Usage
 *
 * ```ts
 * import { Emails } from "@/emails";
 *
 * const sendWelcomeEmail = Effect.gen(function* () {
 *   const emails = yield* Emails;
 *
 *   // Send a transactional email
 *   const result = yield* emails.send({
 *     from: "noreply@example.com",
 *     to: "user@example.com",
 *     subject: "Welcome!",
 *     html: "<p>Welcome to our platform!</p>",
 *   });
 *
 *   // Add user to marketing audience
 *   yield* emails.audience.add("user@example.com");
 *
 *   return result;
 * });
 *
 * // Provide the Emails layer
 * sendWelcomeEmail.pipe(
 *   Effect.provide(Emails.Live({
 *     apiKey: "re_...",
 *     audienceSegmentId: "seg_..."
 *   }))
 * );
 * ```
 *
 * ## Architecture
 *
 * ```
 * Emails (service layer)
 *   ├── send: (params) => Effect<SendEmailResult, ResendError>
 *   └── audience: Ready<Audience>
 *       └── add: (email) => Effect<AddContactResult, ResendError>
 *
 * Each service (EmailService, Audience) uses `yield* Resend` internally.
 * The `dependencyProvider` wrapper provides the Resend client, so consumers
 * see methods returning Effect<T, E> with no additional dependencies.
 * ```
 */

import { Context, Layer, Effect, Schedule } from "effect";
import { Resend, type ResendConfig } from "@/emails/resend-client";
import { ResendError } from "@/errors";
import { dependencyProvider, type Ready } from "@/utils";
import { Audience } from "@/emails/audience";
import type { CreateEmailOptions, CreateEmailResponseSuccess } from "resend";

/**
 * Email service for sending transactional emails.
 *
 * Provides methods for sending emails through Resend. This service wraps
 * the Resend client and provides a clean interface for email operations.
 *
 * Note: This class only contains the `send` method. The `audience` service
 * is provided separately through the Emails.Audience service layer.
 *
 * @example
 * ```ts
 * const program = Effect.gen(function* () {
 *   const emails = yield* Emails;
 *
 *   // Send an email
 *   const result = yield* emails.send({
 *     from: "noreply@example.com",
 *     to: "user@example.com",
 *     subject: "Welcome!",
 *     html: "<p>Welcome to our platform!</p>",
 *   });
 *
 *   // Add to marketing audience
 *   yield* emails.audience.add("user@example.com");
 *
 *   return result;
 * });
 * ```
 */
export class EmailService {
  /**
   * Sends an email through Resend.
   *
   * @param params - Email parameters (from, to, subject, html/text, etc.)
   * @returns Email send result containing the email ID
   * @throws ResendError - If Resend API call fails
   */
  send(
    params: CreateEmailOptions,
  ): Effect.Effect<CreateEmailResponseSuccess, ResendError, Resend> {
    return Effect.gen(function* () {
      const resend = yield* Resend;
      return yield* resend.emails.send(params);
    });
  }
}

/**
 * Emails service layer.
 *
 * Provides access to the email service through Effect's dependency injection
 * system. The Resend dependency is provided internally, so consumers don't
 * need to manage it.
 *
 * @example
 * ```ts
 * const program = Effect.gen(function* () {
 *   const emails = yield* Emails;
 *
 *   // Send an email - no Resend requirement leaked!
 *   const result = yield* emails.send({
 *     from: "noreply@example.com",
 *     to: "user@example.com",
 *     subject: "Welcome!",
 *     html: "<p>Welcome to our platform!</p>",
 *   });
 *
 *   // Add to marketing audience
 *   yield* emails.audience.add("user@example.com");
 *
 *   return result;
 * });
 *
 * // Provide the Emails layer
 * program.pipe(Effect.provide(Emails.Live({
 *   apiKey: "re_...",
 *   audienceSegmentId: "seg_..."
 * })));
 * ```
 */
export class Emails extends Context.Tag("Email")<
  Emails,
  {
    readonly send: Ready<EmailService>["send"];
    readonly audience: Ready<Audience>;
  }
>() {
  /**
   * Default retry logic for email operations with error handling.
   *
   * Uses exponential backoff with 5 attempts (100ms, 200ms, 400ms, 800ms, 1600ms).
   * Catches all errors, logs them as warnings, and continues without failing.
   *
   * @param errorMessage - The message to log if the operation fails after all retries
   * @returns A pipe operator that adds retry and error handling to an Effect
   *
   * @example
   * ```ts
   * const program = Effect.gen(function* () {
   *   const emails = yield* Emails;
   *   yield* emails.send({...}).pipe(
   *     Emails.DefaultRetries("Failed to send invitation email")
   *   );
   *   yield* emails.audience.add(email).pipe(
   *     Emails.DefaultRetries("Failed to add user to audience")
   *   );
   * });
   * ```
   */
  static DefaultRetries = <A, E, R>(
    errorMessage: string,
  ): ((effect: Effect.Effect<A, E, R>) => Effect.Effect<void, never, R>) => {
    return (effect) =>
      effect.pipe(
        // Retry with exponential backoff: 100ms, 200ms, 400ms, 800ms, 1600ms (max 5 attempts)
        Effect.retry(
          Schedule.exponential("100 millis").pipe(
            Schedule.compose(Schedule.recurs(4)),
          ),
        ),
        // Catch all errors and log them, but don't fail the Effect
        Effect.catchAllCause((cause) =>
          Effect.logWarning(errorMessage).pipe(
            Effect.annotateLogs({ cause: String(cause) }),
            Effect.as(undefined),
          ),
        ),
      );
  };
  /**
   * Default layer that creates the Emails service.
   *
   * Requires Resend to be provided. The dependency provider automatically
   * provides the Resend dependency to service methods, removing it from method signatures.
   */
  static Default = Layer.effect(
    Emails,
    Effect.gen(function* () {
      const resend = yield* Resend;
      const provideDependencies = dependencyProvider([
        { tag: Resend, instance: resend },
      ]);

      const emailService = provideDependencies(new EmailService());
      const audienceService = provideDependencies(new Audience());

      return {
        send: emailService.send,
        audience: audienceService,
      };
    }),
  );

  /**
   * Creates a fully configured layer with Resend.
   *
   * @param config - Partial Resend configuration (validated by Resend layer)
   * @returns A Layer providing Emails
   *
   * @example
   * ```ts
   * const EmailsLive = Emails.Live({
   *   apiKey: process.env.RESEND_API_KEY,
   *   audienceSegmentId: process.env.RESEND_AUDIENCE_SEGMENT_ID,
   * });
   *
   * program.pipe(Effect.provide(EmailsLive));
   * ```
   */
  static Live = (config: Partial<ResendConfig>) => {
    const resendLayer = Resend.layer(config);

    return Emails.Default.pipe(Layer.provide(resendLayer));
  };
}
