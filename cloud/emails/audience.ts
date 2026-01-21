/**
 * @fileoverview Audience service for managing Resend marketing audience.
 *
 * Provides an Effect-native service for adding contacts to the Mirascope Cloud
 * audience segment for marketing emails. This service wraps Resend's contact
 * segment operations and provides a clean interface for audience management.
 */

import { Effect } from "effect";
import { Resend } from "@/emails/resend-client";
import { ResendError } from "@/errors";

/**
 * Response from adding a contact to an audience segment.
 * This type is not exported by the resend package, so we define it here.
 */
export interface AddContactSegmentResponseSuccess {
  id: string;
}

/**
 * Audience service for managing the Mirascope Cloud marketing audience.
 *
 * Provides methods for adding contacts to the audience segment for marketing emails.
 * The segment ID is configured at initialization and all operations use this segment.
 *
 * @example
 * ```ts
 * const program = Effect.gen(function* () {
 *   const emails = yield* Emails;
 *
 *   // Add a user to the marketing audience
 *   const result = yield* emails.audience.add("user@example.com");
 *
 *   return result;
 * });
 * ```
 */
export class Audience {
  /**
   * Adds a contact to the Mirascope Cloud audience segment by email.
   *
   * This adds the email to the configured audience segment, allowing them to
   * receive marketing emails. Duplicate adds are handled gracefully by Resend.
   *
   * @param email - The email address to add to the audience
   * @returns Result containing the contact ID
   * @throws ResendError - If Resend API call fails
   *
   * @example
   * ```ts
   * const program = Effect.gen(function* () {
   *   const emails = yield* Emails;
   *
   *   // Add new user to marketing audience
   *   const result = yield* emails.audience.add("user@example.com");
   *   console.log(`Added contact with ID: ${result.id}`);
   * });
   * ```
   */
  add(
    email: string,
  ): Effect.Effect<AddContactSegmentResponseSuccess, ResendError, Resend> {
    return Effect.gen(function* () {
      const resend = yield* Resend;
      return yield* resend.contacts.segments.add({
        email,
        segmentId: resend.config.audienceSegmentId,
      });
    });
  }
}
