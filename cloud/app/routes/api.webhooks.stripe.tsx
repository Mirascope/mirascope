import { createFileRoute } from "@tanstack/react-router";
import { Effect, Layer } from "effect";
import { Payments } from "@/payments";
import { DrizzleORM } from "@/db/client";
import { InternalError, StripeError } from "@/errors";
import Stripe from "stripe";

/**
 * Stripe webhook handler for processing payment events.
 *
 * Handles checkout.session.completed events to automatically grant
 * credits after successful payment.
 */
export const Route = createFileRoute("/api/webhooks/stripe")({
  server: {
    handlers: {
      POST: async ({ request }: { request: Request }) => {
        const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

        const handler = Effect.gen(function* () {
          if (!webhookSecret) {
            return yield* new InternalError({
              message: "Stripe webhook secret not configured",
            });
          }

          const payments = yield* Payments;

          // Get the Stripe signature from headers
          const signature = request.headers.get("stripe-signature");
          if (!signature) {
            return yield* new StripeError({
              message: "Missing stripe-signature header",
            });
          }

          // Get the raw request body
          const body = yield* Effect.tryPromise({
            try: () => request.text(),
            catch: (e) =>
              new InternalError({
                message: "Failed to read request body",
                cause: e,
              }),
          });

          // Verify and construct the webhook event
          const event: Stripe.Event = yield* Effect.tryPromise({
            try: async () => {
              // We need to use the raw Stripe SDK for webhook verification
              const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || "");
              return await stripe.webhooks.constructEventAsync(
                body,
                signature,
                webhookSecret,
              );
            },
            catch: (e) =>
              new StripeError({
                message: "Webhook signature verification failed",
                cause: e,
              }),
          });

          console.log("Received Stripe webhook event:", {
            type: event.type,
            id: event.id,
          });

          // Handle payment_intent.succeeded events
          if (event.type === "payment_intent.succeeded") {
            const paymentIntent = event.data.object;

            console.log("Processing payment_intent.succeeded:", {
              paymentIntentId: paymentIntent.id,
              amount: paymentIntent.amount,
              customer: paymentIntent.customer,
              metadata: paymentIntent.metadata,
            });

            // Extract metadata
            const customerId =
              typeof paymentIntent.customer === "string"
                ? paymentIntent.customer
                : paymentIntent.customer?.id;
            const creditAmountInCents =
              paymentIntent.metadata?.creditAmountInCents;

            if (!customerId || !creditAmountInCents) {
              console.error("Missing metadata in payment intent:", {
                paymentIntentId: paymentIntent.id,
                metadata: paymentIntent.metadata,
              });
              return new Response(
                JSON.stringify({ error: "Missing required metadata" }),
                {
                  status: 400,
                  headers: { "Content-Type": "application/json" },
                },
              );
            }

            // Convert cents to dollars
            const amountInDollars = parseInt(creditAmountInCents) / 100;

            // Set expiration to 1 year from now
            const expiresAt = new Date();
            expiresAt.setFullYear(expiresAt.getFullYear() + 1);

            // Create the credit grant
            console.log("Creating credit grant:", {
              customerId,
              amountInDollars,
              paymentIntentId: paymentIntent.id,
            });

            const creditGrantId =
              yield* payments.products.router.createCreditGrant({
                customerId,
                amountInDollars,
                expiresAt,
                metadata: {
                  paymentIntentId: paymentIntent.id,
                },
              });

            console.log("Credit grant created successfully:", creditGrantId);

            return new Response(
              JSON.stringify({ received: true, creditGrantId }),
              { status: 200, headers: { "Content-Type": "application/json" } },
            );
          }

          return new Response(JSON.stringify({ received: true }), {
            status: 200,
            headers: { "Content-Type": "application/json" },
          });
        }).pipe(
          Effect.provide(
            Payments.Live({
              apiKey: process.env.STRIPE_SECRET_KEY || "",
              routerPriceId: process.env.STRIPE_ROUTER_PRICE_ID || "",
              routerMeterId: process.env.STRIPE_ROUTER_METER_ID || "",
              cloudFreePriceId: process.env.STRIPE_CLOUD_FREE_PRICE_ID || "",
              cloudProPriceId: process.env.STRIPE_CLOUD_PRO_PRICE_ID || "",
              cloudTeamPriceId: process.env.STRIPE_CLOUD_TEAM_PRICE_ID || "",
              cloudSpansPriceId: process.env.STRIPE_CLOUD_SPANS_PRICE_ID || "",
              cloudSpansMeterId: process.env.STRIPE_CLOUD_SPANS_METER_ID || "",
            }).pipe(
              Layer.provide(
                DrizzleORM.layer({
                  connectionString: process.env.DATABASE_URL || "",
                }),
              ),
            ),
          ),
          Effect.catchAll((error) => {
            console.error("Webhook handler error:", error);
            return Effect.succeed(
              new Response(
                JSON.stringify({
                  error:
                    error instanceof Error ? error.message : "Unknown error",
                }),
                {
                  status: 500,
                  headers: { "Content-Type": "application/json" },
                },
              ),
            );
          }),
        );

        return Effect.runPromise(handler);
      },
    },
  },
});
