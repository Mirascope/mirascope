import { relations, sql } from "drizzle-orm";
import {
  pgTable,
  text,
  timestamp,
  uuid,
  pgEnum,
  bigint,
  index,
} from "drizzle-orm/pg-core";
import { organizations } from "./organizations";
import { routerRequests } from "./router-requests";
import type { CostInCenticents } from "@/api/router/cost-utils";

/**
 * Reservation status enum for tracking fund reservation lifecycle.
 *
 * - active: Reservation is active and funds are locked
 * - released: Funds released (check routerRequestId to determine if request succeeded/failed)
 * - expired: Reservation expired due to timeout (handled by future CRON job)
 */
export const reservationStatusEnum = pgEnum("reservation_status", [
  "active",
  "released",
  "expired",
]);

/**
 * Credit reservations table for preventing overdraft in concurrent router requests.
 *
 * ## Purpose
 * This table implements a two-phase commit pattern for fund reservation to prevent
 * overdraft in concurrent scenarios. It stores ONLY the financial reservation data.
 * Request metadata (provider, model, usage) is stored in the router_requests table.
 *
 * ## Financial Data Immutability
 * This table stores financial records that must NEVER be deleted. Records are linked
 * to Stripe customers (not organizations) because:
 * - Stripe customers are permanent and never deleted
 * - Organizations can be deleted, but financial data must be preserved
 * - Regulatory compliance requires immutable audit trails
 * - Organization info can be retrieved via join: stripeCustomerId → organizations.stripe_customer_id
 *
 * ## Cost Storage Format
 * All costs are stored as BIGINT in centi-cents, where 1 = $0.0001 USD.
 * This provides:
 * - Precision for micro-pricing (LLM token costs)
 * - Fast, accurate integer arithmetic
 * - No floating-point errors
 *
 * Examples:
 * - 10000 = $1.00
 * - 1 = $0.0001
 * - 12345 = $1.2345
 *
 * ## Problem
 * Without reservations, concurrent requests could race to check balance, both see
 * sufficient funds, and both proceed - causing overdraft. Example:
 * - Balance: $10
 * - Request A checks balance → $10 available → proceeds
 * - Request B checks balance → $10 available → proceeds (race!)
 * - Both requests charge $8 → Total used: $16 → Overdraft by $6
 *
 * ## Solution: Two-Phase Reservation Pattern
 * When a router request is received:
 * 1. **Create Request**: Insert router_requests record in "pending" state
 * 2. **Reserve**: Atomically lock estimated funds
 *    - Calculate: available = total_balance - SUM(active_reservations)
 *    - If available >= estimated_cost: create active reservation with routerRequestId
 *    - If available < estimated_cost: reject request immediately
 * 3. **Process**: Make the actual request to the AI provider
 * 4. **Complete**:
 *    - Update router_requests with actual usage/cost and status (success/failure)
 *    - Mark reservation as 'released'
 *    - Funds are freed for new reservations
 *
 * ## Lifecycle
 * - **active**: Reservation created, funds locked (initial state)
 * - **released**: Funds released (join with router_requests via routerRequestId to see outcome)
 * - **expired**: Reservation timed out (handled by future CRON job)
 *
 * ## Determining Request Outcome
 * Join with router_requests via routerRequestId to see the complete request status:
 * - pending: Request still being processed (shouldn't happen if released)
 * - success: Request completed successfully
 * - failure: Request failed
 *
 * ## Expiration Safety Net
 * The expires_at field (default 5 minutes) provides a safety net for orphaned
 * reservations from server crashes or bugs. Under normal operation (99.9%+ of cases),
 * reservations are explicitly released. The CRON job is a defensive measure.
 *
 * TODO: Implement CRON job to expire orphaned reservations:
 * - Run every 5 minutes
 * - Find reservations WHERE status='active' AND expires_at < NOW()
 * - Mark them as 'expired' and release the funds
 * - Log these occurrences for monitoring (should be rare - indicates bugs or crashes)
 * - Use the expires_at index for efficient querying
 */
export const creditReservations = pgTable(
  "credit_reservations",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    stripeCustomerId: text("stripe_customer_id").notNull(),

    // Cost tracking (in centi-cents: 1 = $0.0001 USD)
    estimatedCostCenticents: bigint("estimated_cost_centicents", {
      mode: "bigint",
    }).notNull(),

    // Status tracking
    status: reservationStatusEnum("status").default("active").notNull(),

    // Foreign key to router_requests table (required - request always created in pending state first)
    routerRequestId: uuid("router_request_id")
      .notNull()
      .references(() => routerRequests.id),

    // Timestamps
    createdAt: timestamp("created_at").defaultNow().notNull(),
    releasedAt: timestamp("released_at"), // Single field for any release (settled or not)
    expiresAt: timestamp("expires_at")
      .notNull()
      .$defaultFn(() => new Date(Date.now() + 5 * 60 * 1000)), // 5 minutes from now
  },
  (table) => ({
    // Index for fast lookup of active reservations by customer
    customerStatusIndex: index("credit_reservations_customer_status_index").on(
      table.stripeCustomerId,
      table.status,
    ),
    // Index for future CRON job to expire old active reservations
    expiresAtIndex: index("credit_reservations_expires_at_index")
      .on(table.expiresAt)
      .where(sql`${table.status} = 'active'`),
  }),
);

export const creditReservationsRelations = relations(
  creditReservations,
  ({ one }) => ({
    organization: one(organizations, {
      fields: [creditReservations.stripeCustomerId],
      references: [organizations.stripeCustomerId],
    }),
    routerRequest: one(routerRequests, {
      fields: [creditReservations.routerRequestId],
      references: [routerRequests.id],
    }),
  }),
);

// Internal types
export type CreditReservation = typeof creditReservations.$inferSelect;
export type NewCreditReservation = typeof creditReservations.$inferInsert;
export type ReservationStatus =
  (typeof reservationStatusEnum.enumValues)[number];

// Helper to ensure cost fields use the CostInCenticents type
export type CreditReservationWithTypedCosts = Omit<
  CreditReservation,
  "estimatedCostCenticents"
> & {
  estimatedCostCenticents: CostInCenticents;
};
