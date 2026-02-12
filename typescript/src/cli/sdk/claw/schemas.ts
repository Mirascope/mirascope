/**
 * @fileoverview Schema definitions for Claw API responses.
 *
 * These match the cloud's ClawSchema from api/claws.schemas.ts.
 * We use Schema.Struct with only the fields the CLI cares about,
 * using { onExcessProperty: "ignore" } to tolerate extra fields.
 */

import { Schema } from "effect";

export const ClawStatus = Schema.Literal(
  "pending",
  "provisioning",
  "active",
  "paused",
  "error",
);

/**
 * Core claw schema — subset of fields the CLI needs.
 * The cloud response includes more fields (secrets, bucket, etc.)
 * which we ignore.
 */
export const Claw = Schema.Struct({
  id: Schema.String,
  slug: Schema.String,
  displayName: Schema.NullOr(Schema.String),
  organizationId: Schema.String,
  status: ClawStatus,
  instanceType: Schema.String,
  createdAt: Schema.NullOr(Schema.Unknown),
});

export type Claw = typeof Claw.Type;

/**
 * Extended claw detail — same as Claw for now.
 * Will add container status fields when the status endpoint differs.
 */
export const ClawDetail = Schema.Struct({
  ...Claw.fields,
  lastError: Schema.NullOr(Schema.String),
  lastDeployedAt: Schema.NullOr(Schema.Unknown),
});

export type ClawDetail = typeof ClawDetail.Type;
