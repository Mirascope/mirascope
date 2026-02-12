/**
 * @fileoverview Schema definitions for Claw API responses.
 */

import { Schema } from "effect";

export const ClawStatus = Schema.Literal(
  "pending",
  "provisioning",
  "active",
  "paused",
  "error",
);

export const Claw = Schema.Struct({
  id: Schema.String,
  organizationId: Schema.String,
  organizationSlug: Schema.String,
  slug: Schema.String,
  status: ClawStatus,
  instanceType: Schema.String,
  createdAt: Schema.String,
});

export type Claw = typeof Claw.Type;

export const ClawDetail = Schema.Struct({
  ...Claw.fields,
  containerStatus: Schema.NullOr(Schema.String),
  uptime: Schema.NullOr(Schema.Number),
  lastSync: Schema.NullOr(Schema.String),
  errorMessage: Schema.NullOr(Schema.String),
});

export type ClawDetail = typeof ClawDetail.Type;

export const CreateClawParams = Schema.Struct({
  name: Schema.String,
  instanceType: Schema.optionalWith(Schema.String, {
    default: () => "standard",
  }),
});

export type CreateClawParams = typeof CreateClawParams.Type;
