import { createFileRoute } from "@tanstack/react-router";
import { Effect, Layer } from "effect";
import { Payments } from "@/payments";
import { DrizzleORM } from "@/db/client";
import { StripeError } from "@/errors";
import { Settings, validateSettings } from "@/settings";
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
        const handler = Effect.gen(function* () {
          // Get validated settings
          const settings = yield* Settings;

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
              new StripeError({
                message: "Failed to read request body",
                cause: e,
              }),
          });

          // Verify and construct the webhook event
          const event: Stripe.Event = yield* Effect.tryPromise({
            try: async () => {
              // We need to use the raw Stripe SDK for webhook verification
              const stripe = new Stripe(settings.stripe.secretKey);
              return await stripe.webhooks.constructEventAsync(
                body,
                signature,
                settings.stripe.webhookSecret,
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

          // Handle customer.subscription.updated events
          if (event.type === "customer.subscription.updated") {
            const subscription = event.data.object;

            console.log("Processing customer.subscription.updated:", {
              subscriptionId: subscription.id,
              stripeCustomerId: subscription.customer,
              status: subscription.status,
            });

            // Log subscription changes (no action needed, just informational)
            return new Response(JSON.stringify({ received: true }), {
              status: 200,
              headers: { "Content-Type": "application/json" },
            });
          }

          // Handle invoice.payment_succeeded events
          if (event.type === "invoice.payment_succeeded") {
            const invoice = event.data.object;

            console.log("Processing invoice.payment_succeeded:", {
              invoiceId: invoice.id,
              stripeCustomerId: invoice.customer,
              amount: invoice.amount_paid,
              subscriptionId: invoice.subscription,
            });

            // Subscription upgrade payment succeeded
            return new Response(JSON.stringify({ received: true }), {
              status: 200,
              headers: { "Content-Type": "application/json" },
            });
          }

          // Handle invoice.payment_failed events
          if (event.type === "invoice.payment_failed") {
            const invoice = event.data.object;

            console.error("Invoice payment failed:", {
              invoiceId: invoice.id,
              stripeCustomerId: invoice.customer,
              amount: invoice.amount_due,
              subscriptionId: invoice.subscription,
            });

            // Payment failed - subscription upgrade failed
            // In a future PR, we could send an email notification here
            return new Response(JSON.stringify({ received: true }), {
              status: 200,
              headers: { "Content-Type": "application/json" },
            });
          }

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
            const stripeCustomerId =
              typeof paymentIntent.customer === "string"
                ? paymentIntent.customer
                : paymentIntent.customer?.id;
            const creditAmountInCents =
              paymentIntent.metadata?.creditAmountInCents;

            if (!stripeCustomerId || !creditAmountInCents) {
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
              stripeCustomerId,
              amountInDollars,
              paymentIntentId: paymentIntent.id,
            });

            const creditGrantId =
              yield* payments.products.router.createCreditGrant({
                stripeCustomerId,
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
            Layer.unwrapEffect(
              validateSettings().pipe(
                Effect.orDie, // Settings validation failure is fatal
                Effect.map((settings) =>
                  Layer.mergeAll(
                    Layer.succeed(Settings, settings),
                    Payments.Live(settings.stripe).pipe(
                      Layer.provide(
                        DrizzleORM.layer({
                          connectionString: settings.databaseUrl,
                        }),
                      ),
                    ),
                  ),
                ),
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
