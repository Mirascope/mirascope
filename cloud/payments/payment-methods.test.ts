import { Effect, Layer, Context } from "effect";

import { StripeError } from "@/errors";
import { Stripe } from "@/payments/client";
import { Payments } from "@/payments/service";
import { describe, it, expect } from "@/tests/db";

describe("payment methods", () => {
  const mockConfig = {
    apiKey: "sk_test_mock",
    routerPriceId: "price_test",
    routerMeterId: "meter_test",
  };

  describe("createSetupIntent", () => {
    it.effect("creates setup intent and returns client secret", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result =
          yield* payments.paymentMethods.createSetupIntent("cus_test123");

        expect(result.clientSecret).toBe("seti_test_secret");
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(
              Layer.succeed(Stripe, {
                setupIntents: {
                  create: (params: {
                    customer: string;
                    usage: string;
                    payment_method_types: string[];
                  }) => {
                    expect(params.customer).toBe("cus_test123");
                    expect(params.usage).toBe("off_session");
                    expect(params.payment_method_types).toEqual([
                      "card",
                      "link",
                    ]);
                    return Effect.succeed({
                      id: "seti_test",
                      client_secret: "seti_test_secret",
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
      "returns StripeError when setup intent has no client secret",
      () =>
        Effect.gen(function* () {
          const payments = yield* Payments;

          const result = yield* payments.paymentMethods
            .createSetupIntent("cus_test123")
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(StripeError);
          expect(result.message).toBe(
            "SetupIntent created but no client secret returned",
          );
        }).pipe(
          Effect.provide(
            Payments.Default.pipe(
              Layer.provide(
                Layer.succeed(Stripe, {
                  setupIntents: {
                    create: () =>
                      Effect.succeed({
                        id: "seti_test",
                        client_secret: null,
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

  describe("getDefault", () => {
    it.effect(
      "returns payment method from customer invoice_settings default",
      () =>
        Effect.gen(function* () {
          const payments = yield* Payments;

          const result =
            yield* payments.paymentMethods.getDefault("cus_test123");

          expect(result).not.toBeNull();
          expect(result!.id).toBe("pm_test_default");
          expect(result!.brand).toBe("visa");
          expect(result!.last4).toBe("4242");
          expect(result!.expMonth).toBe(12);
          expect(result!.expYear).toBe(2025);
        }).pipe(
          Effect.provide(
            Payments.Default.pipe(
              Layer.provide(
                Layer.succeed(Stripe, {
                  customers: {
                    retrieve: () =>
                      Effect.succeed({
                        id: "cus_test123",
                        deleted: undefined,
                        invoice_settings: {
                          default_payment_method: "pm_test_default",
                        },
                      }),
                  },
                  paymentMethods: {
                    retrieve: () =>
                      Effect.succeed({
                        id: "pm_test_default",
                        card: {
                          brand: "visa",
                          last4: "4242",
                          exp_month: 12,
                          exp_year: 2025,
                        },
                      }),
                  },
                  config: mockConfig,
                } as unknown as Context.Tag.Service<typeof Stripe>),
              ),
            ),
          ),
        ),
    );

    it.effect("falls back to first card in list when no default set", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.paymentMethods.getDefault("cus_test123");

        expect(result).not.toBeNull();
        expect(result!.id).toBe("pm_from_list");
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(
              Layer.succeed(Stripe, {
                customers: {
                  retrieve: () =>
                    Effect.succeed({
                      id: "cus_test123",
                      deleted: undefined,
                      invoice_settings: {
                        default_payment_method: null,
                      },
                    }),
                },
                paymentMethods: {
                  list: () =>
                    Effect.succeed({
                      data: [
                        {
                          id: "pm_from_list",
                        },
                      ],
                    }),
                  retrieve: () =>
                    Effect.succeed({
                      id: "pm_from_list",
                      card: {
                        brand: "mastercard",
                        last4: "5555",
                        exp_month: 6,
                        exp_year: 2026,
                      },
                    }),
                },
                config: mockConfig,
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      ),
    );

    it.effect("returns null when no payment methods exist", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.paymentMethods.getDefault("cus_test123");

        expect(result).toBeNull();
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(
              Layer.succeed(Stripe, {
                customers: {
                  retrieve: () =>
                    Effect.succeed({
                      id: "cus_test123",
                      deleted: undefined,
                      invoice_settings: {
                        default_payment_method: null,
                      },
                    }),
                },
                paymentMethods: {
                  list: () =>
                    Effect.succeed({
                      data: [],
                    }),
                },
                config: mockConfig,
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      ),
    );

    it.effect("returns null when customer is deleted", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.paymentMethods.getDefault("cus_test123");

        expect(result).toBeNull();
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(
              Layer.succeed(Stripe, {
                customers: {
                  retrieve: () =>
                    Effect.succeed({
                      id: "cus_test123",
                      deleted: true,
                    }),
                },
                config: mockConfig,
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      ),
    );

    it.effect("returns null when payment method has no card details", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.paymentMethods.getDefault("cus_test123");

        expect(result).toBeNull();
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(
              Layer.succeed(Stripe, {
                customers: {
                  retrieve: () =>
                    Effect.succeed({
                      id: "cus_test123",
                      deleted: undefined,
                      invoice_settings: {
                        default_payment_method: "pm_nocard",
                      },
                    }),
                },
                paymentMethods: {
                  retrieve: () =>
                    Effect.succeed({
                      id: "pm_nocard",
                      card: null,
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

  describe("remove", () => {
    it.effect("detaches payment method and clears default", () => {
      let detached = false;
      let customerUpdated = false;

      return Effect.gen(function* () {
        const payments = yield* Payments;

        yield* payments.paymentMethods.remove("cus_test123", "pm_test_default");

        expect(detached).toBe(true);
        expect(customerUpdated).toBe(true);
      }).pipe(
        Effect.provide(
          Payments.Default.pipe(
            Layer.provide(
              Layer.succeed(Stripe, {
                paymentMethods: {
                  detach: (id: string) => {
                    expect(id).toBe("pm_test_default");
                    detached = true;
                    return Effect.succeed({ id });
                  },
                },
                customers: {
                  retrieve: () =>
                    Effect.succeed({
                      id: "cus_test123",
                      deleted: undefined,
                      invoice_settings: {
                        default_payment_method: "pm_test_default",
                      },
                    }),
                  update: (
                    id: string,
                    params: {
                      invoice_settings: { default_payment_method: string };
                    },
                  ) => {
                    expect(id).toBe("cus_test123");
                    expect(params.invoice_settings.default_payment_method).toBe(
                      "",
                    );
                    customerUpdated = true;
                    return Effect.succeed({ id });
                  },
                },
                config: mockConfig,
              } as unknown as Context.Tag.Service<typeof Stripe>),
            ),
          ),
        ),
      );
    });

    it.effect(
      "detaches payment method without clearing when not default",
      () => {
        let detached = false;

        return Effect.gen(function* () {
          const payments = yield* Payments;

          yield* payments.paymentMethods.remove("cus_test123", "pm_other");

          expect(detached).toBe(true);
        }).pipe(
          Effect.provide(
            Payments.Default.pipe(
              Layer.provide(
                Layer.succeed(Stripe, {
                  paymentMethods: {
                    detach: (id: string) => {
                      detached = true;
                      return Effect.succeed({ id });
                    },
                  },
                  customers: {
                    retrieve: () =>
                      Effect.succeed({
                        id: "cus_test123",
                        deleted: undefined,
                        invoice_settings: {
                          default_payment_method: "pm_different",
                        },
                      }),
                  },
                  config: mockConfig,
                } as unknown as Context.Tag.Service<typeof Stripe>),
              ),
            ),
          ),
        );
      },
    );
  });
});
