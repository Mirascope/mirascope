import { Schema } from "effect";

/**
 * Error thrown by deployment operations.
 *
 * Covers provisioning failures, deprovision errors, status check failures,
 * and storage operation errors.
 */
export class ClawDeploymentError extends Schema.TaggedError<ClawDeploymentError>()(
  "DeploymentError",
  {
    message: Schema.String,
    cause: Schema.optional(Schema.Unknown),
  },
) {
  static readonly status = 500 as const;
}
