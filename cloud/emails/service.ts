/**
 * @fileoverview Emails service layer.
 *
 * This module provides the `Emails` service which wraps Resend for sending
 * transactional emails through Effect's dependency injection system.
 *
 * ## Usage
 *
 * ```ts
 * import { Emails } from "@/emails";
 *
 * const sendWelcomeEmail = Effect.gen(function* () {
 *   const emails = yield* Emails;
 *
 *   const result = yield* emails.send({
 *     from: "noreply@example.com",
 *     to: "user@example.com",
 *     subject: "Welcome!",
 *     html: "<p>Welcome to our platform!</p>",
 *   });
 *
 *   return result;
 * });
 *
 * // Provide the Emails layer
 * sendWelcomeEmail.pipe(
 *   Effect.provide(Emails.Live({ apiKey: "re_..." }))
 * );
 * ```
 *
 * ## Architecture
 *
 * ```
 * Email (service layer)
 *   └── send: (params) => Effect<SendEmailResult, ResendError>
 *
 * The service uses `yield* Resend` internally. The `makeReady` wrapper
 * provides the Resend client, so consumers see methods returning
 * Effect<T, E> with no additional dependencies.
 * ```
 */

import { Context, Layer, Effect } from "effect";
import { Resend, type ResendConfig } from "@/emails/resend-client";
import { ResendError } from "@/errors";
import { dependencyProvider, type Ready } from "@/utils";
import type { CreateEmailOptions, CreateEmailResponseSuccess } from "resend";

/**
 * Email service for sending transactional emails.
 *
 * Provides methods for sending emails through Resend. This service wraps
 * the Resend client and provides a clean interface for email operations.
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
 *   return result;
 * });
 *
 * // Provide the Emails layer
 * program.pipe(Effect.provide(Emails.Live({ apiKey: "re_..." })));
 * ```
 */
export class Emails extends Context.Tag("Email")<
  Emails,
  Ready<EmailService>
>() {
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

      return provideDependencies(new EmailService());
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
