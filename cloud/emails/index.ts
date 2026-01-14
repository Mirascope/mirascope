/**
 * @fileoverview Email service exports.
 *
 * Provides Effect-native Resend client for sending transactional emails
 * and React Email template rendering.
 */

// Export the main service and its configuration type
export { Emails } from "@/emails/service";
export type { ResendConfig } from "@/emails/resend-client";

// Export template rendering utilities
export { renderEmailTemplate } from "@/emails/render";

// Export email templates
export * from "@/emails/templates";
