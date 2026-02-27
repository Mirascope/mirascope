import { Effect, Layer, Context } from "effect";
import StripeSDK from "stripe";

import { StripeError } from "@/errors";
import { Stripe } from "@/payments/client";
import { Payments } from "@/payments/service";
import { describe, it, expect } from "@/tests/db";

describe("payment intents", () => {
  const mockConfig = {
    apiKey: "sk_test_mock",
    routerPriceId: "price_test",
    routerMeterId: "meter_test",
  };

  describe("createRouterCreditsPurchaseIntent", () => {
    it.effect(
      "creates payment intent without saved card (requires_payment)",
      () =>
        Effect.gen(function* () {
          const payments = yield* Payments;

          const result =
            yield* payments.paymentIntents.createRouterCreditsPurchaseIntent({
              stripeCustomerId: "cus_test123",
              amountInDollars: 50,
              metadata: {
                organizationId: "org_123",
              },
            });

          expect(result.clientSecret).toBeDefined();
          expect(result.clientSecret).toMatch(/^pi_test_/);
          expect(result.amountInDollars).toBe(50);
          expect(result.status).toBe("requires_payment");
        }).pipe(
          Effect.provide(
            Payments.Default.pipe(
              Layer.provide(
                Layer.succeed(Stripe, {
                  paymentIntents: {
                    create: (params: StripeSDK.PaymentIntentCreateParams) => {
                      expect(params.setup_future_usage).toBe("off_session");
                      expect(params.payment_method_types).toEqual([
                        "card",
                        "link",
                      ]);
                      return Effect.succeed({
                        id: `pi_test_${crypto.randomUUID()}`,
                        client_secret: `pi_test_${crypto.randomUUID()}_secret_${crypto.randomUUID()}`,
                        status: "requires_payment_method",
                      });
                    },
                  },
                  config: mockConfig,
                } as unknown as Context.Tag.Service<typeof Stripe>),
              ),
            ),
          ),
        ),
    );

    it.effect("includes correct metadata in payment intent", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        yield* payments.paymentIntents.createRouterCreditsPurchaseIntent({
          stripeCustomerId: "cus_test123",
          amountInDollars: 50,
          metadata: {
            organizationId: "org_123",
            customKey: "customValue",
          },
        });

        // Just ensure it completes without error
        expect(true).toBe(true);
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(
              Layer.succeed(Stripe, {
                paymentIntents: {
                  create: (params: StripeSDK.PaymentIntentCreateParams) => {
                    // Verify metadata
                    expect(params.metadata).toBeDefined();
                    expect(params.metadata?.stripeCustomerId).toBe(
                      "cus_test123",
                    );
                    expect(params.metadata?.creditAmountInCents).toBe("5000");
                    expect(params.metadata?.organizationId).toBe("org_123");
                    expect(params.metadata?.customKey).toBe("customValue");

                    // Verify amount and currency
                    expect(params.amount).toBe(5000);
                    expect(params.currency).toBe("usd");
                    expect(params.customer).toBe("cus_test123");
                    expect(params.description).toContain("$50.00");

                    return Effect.succeed({
                      id: `pi_test_${crypto.randomUUID()}`,
                      client_secret: `pi_test_${crypto.randomUUID()}_secret_${crypto.randomUUID()}`,
                    });
                  },
                },
                config: mockConfig,
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      ),
    );

    it.effect("converts dollars to cents correctly", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        yield* payments.paymentIntents.createRouterCreditsPurchaseIntent({
          stripeCustomerId: "cus_test123",
          amountInDollars: 123.45,
        });
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(
              Layer.succeed(Stripe, {
                paymentIntents: {
                  create: (params: StripeSDK.PaymentIntentCreateParams) => {
                    expect(params.amount).toBe(12345);
                    expect(params.metadata?.creditAmountInCents).toBe("12345");
                    return Effect.succeed({
                      id: "pi_test_123",
                      client_secret: "pi_test_123_secret_456",
                    });
                  },
                },
                config: mockConfig,
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      ),
    );

    it.effect("returns StripeError when payment intent creation fails", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.paymentIntents
          .createRouterCreditsPurchaseIntent({
            stripeCustomerId: "cus_test123",
            amountInDollars: 50,
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(StripeError);
        expect(result.message).toBe("Failed to create payment intent");
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(
              Layer.succeed(Stripe, {
                paymentIntents: {
                  create: () =>
                    Effect.fail(
                      new StripeError({
                        message: "Failed to create payment intent",
                      }),
                    ),
                },
                config: mockConfig,
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      ),
    );

    it.effect(
      "returns StripeError when payment intent has no client secret",
      () =>
        Effect.gen(function* () {
          const payments = yield* Payments;

          const result = yield* payments.paymentIntents
            .createRouterCreditsPurchaseIntent({
              stripeCustomerId: "cus_test123",
              amountInDollars: 50,
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(StripeError);
          expect(result.message).toBe(
            "PaymentIntent created but no client secret returned",
          );
        }).pipe(
          Effect.provide(
            Payments.Default.pipe(
              Layer.provide(
                Layer.succeed(Stripe, {
                  paymentIntents: {
                    create: () =>
                      Effect.succeed({
                        id: "pi_test_123",
                        client_secret: null, // No client secret
                      }),
                  },
                  config: mockConfig,
                } as unknown as Context.Tag.Service<typeof Stripe>),
              ),
            ),
          ),
        ),
    );

    it.effect(
      "with saved card: returns succeeded when server-side confirmation succeeds",
      () =>
        Effect.gen(function* () {
          const payments = yield* Payments;

          const result =
            yield* payments.paymentIntents.createRouterCreditsPurchaseIntent({
              stripeCustomerId: "cus_test123",
              amountInDollars: 50,
              paymentMethodId: "pm_saved_123",
            });

          expect(result.clientSecret).toBeNull();
          expect(result.status).toBe("succeeded");
          expect(result.amountInDollars).toBe(50);
        }).pipe(
          Effect.provide(
            Payments.Default.pipe(
              Layer.provide(
                Layer.succeed(Stripe, {
                  paymentIntents: {
                    create: (params: StripeSDK.PaymentIntentCreateParams) => {
                      expect(params.payment_method).toBe("pm_saved_123");
                      expect(params.confirm).toBe(true);
                      expect(params.off_session).toBe(true);
                      return Effect.succeed({
                        id: "pi_test_123",
                        client_secret: "pi_test_123_secret",
                        status: "succeeded",
                      });
                    },
                  },
                  config: mockConfig,
                } as unknown as Context.Tag.Service<typeof Stripe>),
              ),
            ),
          ),
        ),
    );

    it.effect(
      "with saved card: returns requires_action when 3DS is needed",
      () =>
        Effect.gen(function* () {
          const payments = yield* Payments;

          const result =
            yield* payments.paymentIntents.createRouterCreditsPurchaseIntent({
              stripeCustomerId: "cus_test123",
              amountInDollars: 50,
              paymentMethodId: "pm_saved_123",
            });

          expect(result.clientSecret).toBe("pi_test_3ds_secret");
          expect(result.status).toBe("requires_action");
          expect(result.amountInDollars).toBe(50);
        }).pipe(
          Effect.provide(
            Payments.Default.pipe(
              Layer.provide(
                Layer.succeed(Stripe, {
                  paymentIntents: {
                    create: () =>
                      Effect.succeed({
                        id: "pi_test_3ds",
                        client_secret: "pi_test_3ds_secret",
                        status: "requires_action",
                      }),
                  },
                  config: mockConfig,
                } as unknown as Context.Tag.Service<typeof Stripe>),
              ),
            ),
          ),
        ),
    );

    it.effect(
      "with saved card: returns StripeError when requires_action but no client secret",
      () =>
        Effect.gen(function* () {
          const payments = yield* Payments;

          const result = yield* payments.paymentIntents
            .createRouterCreditsPurchaseIntent({
              stripeCustomerId: "cus_test123",
              amountInDollars: 50,
              paymentMethodId: "pm_saved_123",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(StripeError);
          expect(result.message).toBe(
            "PaymentIntent requires action but no client secret returned",
          );
        }).pipe(
          Effect.provide(
            Payments.Default.pipe(
              Layer.provide(
                Layer.succeed(Stripe, {
                  paymentIntents: {
                    create: () =>
                      Effect.succeed({
                        id: "pi_test_3ds",
                        client_secret: null,
                        status: "requires_action",
                      }),
                  },
                  config: mockConfig,
                } as unknown as Context.Tag.Service<typeof Stripe>),
              ),
            ),
          ),
        ),
    );
  });
});
