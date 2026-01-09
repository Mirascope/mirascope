import { Effect } from "effect";
import { NotFoundError, StripeError, SubscriptionPastDueError } from "@/errors";
import { Payments } from "@/payments/service";
import {
  describe,
  it,
  expect,
  assert,
  TestSubscriptionFixture,
  TestErrorScenarioFixture,
  TestSubscriptionWithScheduleFixture,
  TestMultipleSubscriptionItemsFixture,
  TestUpgradeWithPaymentIntentFixture,
  TestPreviewChangeFixture,
  TestDowngradeWithScheduleFixture,
  TestCancelScheduleFixture,
  TestCancelSubscriptionsFixture,
} from "@/tests/payments";

describe("subscriptions", () => {
  describe("getSubscription", () => {
    it.effect("gets subscription for team plan", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers.subscriptions.get("cus_123");

        expect(result.subscriptionId).toBe("sub_123");
        expect(result.currentPlan).toBe("team");
        expect(result.status).toBe("active");
        expect(result.hasPaymentMethod).toBe(true);
      }).pipe(
        Effect.provide(
          TestSubscriptionFixture({
            plan: "team",
            hasPaymentMethod: true,
            stripeCustomerId: "cus_123",
            subscriptionId: "sub_123",
            paymentMethodId: "pm_123",
          }),
        ),
      ),
    );

    it.effect("falls back to free for unknown price ID", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers.subscriptions.get("cus_123");

        expect(result.subscriptionId).toBe("sub_123");
        expect(result.currentPlan).toBe("free"); // Falls back to free
        expect(result.status).toBe("active");
      }).pipe(
        Effect.provide(
          TestMultipleSubscriptionItemsFixture({
            stripeCustomerId: "cus_123",
            subscriptionId: "sub_123",
            items: [
              { id: "si_123", priceId: "price_cloud_legacy_mock" },
              { id: "si_124", priceId: "price_cloud_free_mock" },
            ],
          }),
        ),
      ),
    );

    it.effect("gets subscription details with payment method", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers.subscriptions.get("cus_123");

        expect(result.subscriptionId).toBe("sub_123");
        expect(result.currentPlan).toBe("pro");
        expect(result.status).toBe("active");
        expect(result.hasPaymentMethod).toBe(true);
        expect(result.scheduledChange).toBeUndefined();
      }).pipe(
        Effect.provide(
          TestSubscriptionFixture({
            plan: "pro",
            hasPaymentMethod: true,
            stripeCustomerId: "cus_123",
            subscriptionId: "sub_123",
            paymentMethodId: "pm_123",
          }),
        ),
      ),
    );

    it.effect(
      "gets subscription with payment method from list (not default)",
      () =>
        Effect.gen(function* () {
          const payments = yield* Payments;

          const result = yield* payments.customers.subscriptions.get("cus_123");

          expect(result.hasPaymentMethod).toBe(true);
          expect(result.paymentMethod).toBeDefined();
          expect(result.paymentMethod?.brand).toBe("visa");
          expect(result.paymentMethod?.last4).toBe("4242");
        }).pipe(
          Effect.provide(
            TestSubscriptionFixture({
              plan: "pro",
              hasPaymentMethod: true,
              paymentMethodLocation: "list",
              stripeCustomerId: "cus_123",
              customPaymentMethod: { id: "pm_456" },
            }),
          ),
        ),
    );

    it.effect(
      "gets subscription with payment method from customer invoice settings",
      () =>
        Effect.gen(function* () {
          const payments = yield* Payments;

          const result = yield* payments.customers.subscriptions.get("cus_123");

          expect(result.hasPaymentMethod).toBe(true);
          expect(result.paymentMethod).toBeDefined();
          expect(result.paymentMethod?.brand).toBe("visa");
          expect(result.paymentMethod?.last4).toBe("4242");
        }).pipe(
          Effect.provide(
            TestSubscriptionFixture({
              plan: "pro",
              hasPaymentMethod: true,
              paymentMethodLocation: "customer",
              stripeCustomerId: "cus_123",
            }),
          ),
        ),
    );

    it.effect("handles subscription with expanded payment method object", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers.subscriptions.get("cus_123");

        // Should have payment method detected but no details retrieved
        expect(result.hasPaymentMethod).toBe(true);
        expect(result.paymentMethod).toBeUndefined();
      }).pipe(
        Effect.provide(
          TestSubscriptionFixture({
            plan: "pro",
            hasPaymentMethod: true,
            paymentMethodLocation: "subscription",
            expandedPaymentMethod: true,
            stripeCustomerId: "cus_123",
          }),
        ),
      ),
    );

    it.effect("gets subscription with scheduled downgrade", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers.subscriptions.get("cus_123");

        expect(result.scheduledChange).toBeDefined();
        expect(result.scheduledChange?.targetPlan).toBe("free");
      }).pipe(
        Effect.provide(
          TestSubscriptionWithScheduleFixture({
            plan: "pro",
            targetPlan: "free",
            stripeCustomerId: "cus_123",
            subscriptionId: "sub_123",
            scheduleId: "sched_123",
          }),
        ),
      ),
    );

    it.effect(
      "gets subscription with scheduled downgrade (expanded price object)",
      () =>
        Effect.gen(function* () {
          const payments = yield* Payments;

          const result = yield* payments.customers.subscriptions.get("cus_123");

          expect(result.scheduledChange).toBeDefined();
          expect(result.scheduledChange?.targetPlan).toBe("free");
        }).pipe(
          Effect.provide(
            TestSubscriptionWithScheduleFixture({
              plan: "pro",
              targetPlan: "free",
              stripeCustomerId: "cus_123",
              subscriptionId: "sub_123",
              scheduleId: "sched_123",
              useExpandedPriceObject: true,
            }),
          ),
        ),
    );

    it.effect("gets subscription with past_due status", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers.subscriptions.get("cus_123");

        expect(result.subscriptionId).toBe("sub_123");
        expect(result.status).toBe("past_due");
      }).pipe(
        Effect.provide(
          TestSubscriptionFixture({
            plan: "pro",
            status: "past_due",
            stripeCustomerId: "cus_123",
            subscriptionId: "sub_123",
          }),
        ),
      ),
    );

    it.effect("returns error when no active subscription found", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers.subscriptions
          .get("cus_123")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          "No active subscription found for customer",
        );
      }).pipe(
        Effect.provide(
          TestErrorScenarioFixture({
            errorType: "noActiveSubscription",
            stripeCustomerId: "cus_123",
          }),
        ),
      ),
    );
  });

  describe("previewSubscriptionChange", () => {
    it.effect("previews downgrade (line 523-530)", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers.subscriptions.previewChange({
          stripeCustomerId: "cus_123",
          targetPlan: "free",
        });

        expect(result.isUpgrade).toBe(false);
        expect(result.proratedAmountInDollars).toBe(50);
        expect(result.recurringAmountInDollars).toBe(100);
      }).pipe(
        Effect.provide(
          TestPreviewChangeFixture({
            currentPlan: "pro",
            targetPlan: "free",
            stripeCustomerId: "cus_123",
            proratedAmountInCents: 5000,
            recurringAmountInCents: 10000,
          }),
        ),
      ),
    );

    it.effect("previews upgrade with prorated amount", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers.subscriptions.previewChange({
          stripeCustomerId: "cus_123",
          targetPlan: "team",
        });

        expect(result.isUpgrade).toBe(true);
        expect(result.proratedAmountInDollars).toBe(50);
        expect(result.recurringAmountInDollars).toBe(100);
      }).pipe(
        Effect.provide(
          TestPreviewChangeFixture({
            currentPlan: "pro",
            targetPlan: "team",
            stripeCustomerId: "cus_123",
            proratedAmountInCents: 5000,
            recurringAmountInCents: 10000,
            hasPaymentMethod: true,
          }),
        ),
      ),
    );

    it.effect(
      "returns error when plan item not found in retrieve (line 507)",
      () =>
        Effect.gen(function* () {
          const payments = yield* Payments;

          const result = yield* payments.customers.subscriptions
            .previewChange({
              stripeCustomerId: "cus_123",
              targetPlan: "team",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(StripeError);
          expect(result.message).toBe("Could not find current plan item");
        }).pipe(
          Effect.provide(
            TestPreviewChangeFixture({
              currentPlan: "pro",
              targetPlan: "team",
              stripeCustomerId: "cus_123",
              proratedAmountInCents: 5000,
              recurringAmountInCents: 10000,
              retrieveSubscriptionItems: [
                { id: "si_other", priceId: "price_cloud_spans_mock" },
              ],
            }),
          ),
        ),
    );

    it.effect("returns error when plan item not found", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers.subscriptions
          .previewChange({
            stripeCustomerId: "cus_123",
            targetPlan: "team",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          "Could not determine plan tier from subscription items",
        );
      }).pipe(
        Effect.provide(
          TestPreviewChangeFixture({
            currentPlan: "pro",
            targetPlan: "team",
            stripeCustomerId: "cus_123",
            customCurrentPriceId: "price_unknown",
          }),
        ),
      ),
    );
  });

  describe("updateSubscription", () => {
    it.effect("upgrades subscription without payment method", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers.subscriptions.update({
          stripeCustomerId: "cus_123",
          targetPlan: "pro",
        });

        expect(result.requiresPayment).toBe(true);
        expect(result.clientSecret).toBeDefined();
      }).pipe(
        Effect.provide(
          TestUpgradeWithPaymentIntentFixture({
            currentPlan: "free",
            targetPlan: "pro",
            stripeCustomerId: "cus_123",
            requiresPayment: true,
            hasPaymentMethod: false,
          }),
        ),
      ),
    );

    it.effect("upgrades subscription with payment method on file", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers.subscriptions.update({
          stripeCustomerId: "cus_123",
          targetPlan: "pro",
        });

        expect(result.requiresPayment).toBe(false);
      }).pipe(
        Effect.provide(
          TestUpgradeWithPaymentIntentFixture({
            currentPlan: "free",
            targetPlan: "pro",
            stripeCustomerId: "cus_123",
            requiresPayment: false,
            hasPaymentMethod: true,
          }),
        ),
      ),
    );

    it.effect(
      "returns error when plan item not found in retrieve during upgrade (line 590)",
      () =>
        Effect.gen(function* () {
          const payments = yield* Payments;

          const result = yield* payments.customers.subscriptions
            .update({
              stripeCustomerId: "cus_123",
              targetPlan: "pro",
            })
            .pipe(Effect.flip);

          expect(result).toBeInstanceOf(StripeError);
          expect(result.message).toBe("Could not find current plan item");
        }).pipe(
          Effect.provide(
            TestUpgradeWithPaymentIntentFixture({
              currentPlan: "free",
              targetPlan: "pro",
              stripeCustomerId: "cus_123",
              retrieveSubscriptionItems: [
                { id: "si_other", priceId: "price_router_mock" },
              ],
            }),
          ),
        ),
    );

    it.effect("returns error when plan item not found during upgrade", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers.subscriptions
          .update({
            stripeCustomerId: "cus_123",
            targetPlan: "pro",
          })
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(NotFoundError);
        expect(result.message).toBe(
          "Could not determine plan tier from subscription items",
        );
      }).pipe(
        Effect.provide(
          TestUpgradeWithPaymentIntentFixture({
            currentPlan: "free",
            targetPlan: "pro",
            stripeCustomerId: "cus_123",
            customCurrentPriceId: "price_unknown",
          }),
        ),
      ),
    );

    it.effect("downgrades subscription and schedules change", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers.subscriptions.update({
          stripeCustomerId: "cus_123",
          targetPlan: "free",
        });

        expect(result.requiresPayment).toBe(false);
        expect(result.scheduledFor).toBeDefined();
        expect(result.scheduleId).toBeDefined();
      }).pipe(
        Effect.provide(
          TestDowngradeWithScheduleFixture({
            currentPlan: "pro",
            targetPlan: "free",
            stripeCustomerId: "cus_123",
            subscriptionId: "sub_123",
            newScheduleId: "sched_123",
            updatedScheduleId: "sched_123",
          }),
        ),
      ),
    );

    it.effect(
      "downgrades subscription with multiple items including non-plan items",
      () =>
        Effect.gen(function* () {
          const payments = yield* Payments;

          const result = yield* payments.customers.subscriptions.update({
            stripeCustomerId: "cus_123",
            targetPlan: "free",
          });

          expect(result.requiresPayment).toBe(false);
          expect(result.scheduledFor).toBeDefined();
          expect(result.scheduleId).toBeDefined();
        }).pipe(
          Effect.provide(
            TestDowngradeWithScheduleFixture({
              currentPlan: "pro",
              targetPlan: "free",
              stripeCustomerId: "cus_123",
              subscriptionId: "sub_123",
              newScheduleId: "sched_123",
              updatedScheduleId: "sched_123",
              additionalItems: [
                {
                  id: "si_124",
                  priceId: "price_cloud_spans_mock",
                  quantity: 1,
                },
              ],
            }),
          ),
        ),
    );

    it.effect(
      "downgrades subscription with items without explicit quantity",
      () =>
        Effect.gen(function* () {
          const payments = yield* Payments;

          const result = yield* payments.customers.subscriptions.update({
            stripeCustomerId: "cus_123",
            targetPlan: "free",
          });

          expect(result.requiresPayment).toBe(false);
          expect(result.scheduledFor).toBeDefined();
          expect(result.scheduleId).toBeDefined();
        }).pipe(
          Effect.provide(
            TestDowngradeWithScheduleFixture({
              currentPlan: "pro",
              targetPlan: "free",
              stripeCustomerId: "cus_123",
              subscriptionId: "sub_123",
              newScheduleId: "sched_123",
              updatedScheduleId: "sched_123",
              omitQuantity: true,
            }),
          ),
        ),
    );
  });

  describe("cancelScheduledDowngrade", () => {
    it.effect("cancels scheduled downgrade", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        yield* payments.customers.subscriptions.cancelScheduledDowngrade(
          "cus_123",
        );

        // Test passes if no errors thrown
      }).pipe(
        Effect.provide(
          TestCancelScheduleFixture({
            schedules: [{ id: "sched_123" }],
          }),
        ),
      ),
    );

    it.effect("returns error when no scheduled changes found", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers.subscriptions
          .cancelScheduledDowngrade("cus_123")
          .pipe(Effect.flip);

        expect(result).toBeInstanceOf(StripeError);
        expect(result.message).toBe("No scheduled changes found");
      }).pipe(
        Effect.provide(
          TestCancelScheduleFixture({
            schedules: [],
          }),
        ),
      ),
    );
  });

  describe("getSubscription - scheduled changes edge cases", () => {
    it.effect("handles schedule with non-active status (line 412)", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const subscription =
          yield* payments.customers.subscriptions.get("cus_123");

        // Should not have scheduled change since schedule is not active
        expect(subscription.scheduledChange).toBeUndefined();
      }).pipe(
        Effect.provide(
          TestSubscriptionWithScheduleFixture({
            plan: "pro",
            targetPlan: "free",
            scheduleStatus: "canceled",
            hasPaymentMethod: true,
            stripeCustomerId: "cus_123",
            subscriptionId: "sub_123",
            scheduleId: "sub_sched_123",
          }),
        ),
      ),
    );

    it.effect("handles scheduled change correctly", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const subscription =
          yield* payments.customers.subscriptions.get("cus_123");

        expect(subscription.scheduledChange).not.toBeUndefined();
        expect(subscription.scheduledChange?.targetPlan).toBe("free");
      }).pipe(
        Effect.provide(
          TestSubscriptionWithScheduleFixture({
            plan: "pro",
            targetPlan: "free",
            hasPaymentMethod: true,
            stripeCustomerId: "cus_123",
            subscriptionId: "sub_123",
            scheduleId: "sub_sched_123",
          }),
        ),
      ),
    );

    it.effect("handles scheduled change with no plan items in next phase", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const subscription =
          yield* payments.customers.subscriptions.get("cus_123");

        expect(subscription.scheduledChange).toBeUndefined();
      }).pipe(
        Effect.provide(
          TestSubscriptionWithScheduleFixture({
            plan: "pro",
            targetPlan: "free",
            hasPaymentMethod: true,
            stripeCustomerId: "cus_123",
            subscriptionId: "sub_123",
            scheduleId: "sub_sched_123",
            emptyNextPhase: true,
          }),
        ),
      ),
    );
  });

  describe("previewSubscriptionChange - edge cases", () => {
    it.effect("handles price retrieval for recurring amount", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const preview = yield* payments.customers.subscriptions.previewChange({
          stripeCustomerId: "cus_123",
          targetPlan: "pro",
        });

        expect(preview.recurringAmountInDollars).toBe(50); // $50 from mocked price
      }).pipe(
        Effect.provide(
          TestPreviewChangeFixture({
            currentPlan: "free",
            targetPlan: "pro",
            stripeCustomerId: "cus_123",
            proratedAmountInCents: 1000,
            recurringAmountInCents: 5000, // $50 in cents
            upcomingInvoiceTotalOverride: null, // Null to test price retrieval fallback
          }),
        ),
      ),
    );
  });

  describe("getPlanConfig - missing config", () => {
    it.effect("fails when cloud price IDs are not configured", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers.subscriptions.get("cus_123");

        expect(result).toEqual(
          expect.objectContaining({
            message:
              "Cloud subscription price IDs not configured. Required: cloudFreePriceId, cloudProPriceId, cloudTeamPriceId",
          }),
        );
      }).pipe(
        Effect.flip,
        Effect.provide(
          TestErrorScenarioFixture({
            errorType: "missingConfig",
            stripeCustomerId: "cus_123",
          }),
        ),
      ),
    );
  });

  describe("updateSubscription - downgrade with existing schedule", () => {
    it.effect("releases existing schedule before creating new one", () => {
      let releaseScheduleCalled = false;

      return Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers.subscriptions.update({
          stripeCustomerId: "cus_123",
          targetPlan: "free",
        });

        expect(result.scheduledFor).toBeDefined();
        expect(result.scheduleId).toBe("sub_sched_updated");
        expect(releaseScheduleCalled).toBe(true);
      }).pipe(
        Effect.provide(
          TestDowngradeWithScheduleFixture({
            currentPlan: "pro",
            targetPlan: "free",
            stripeCustomerId: "cus_123",
            subscriptionId: "sub_123",
            existingScheduleId: "sub_sched_existing",
            updatedScheduleId: "sub_sched_updated",
            onScheduleRelease: () => {
              releaseScheduleCalled = true;
            },
          }),
        ),
      );
    });

    it.effect(
      "releases existing schedule (as object) before creating new one",
      () => {
        let releaseScheduleCalled = false;

        return Effect.gen(function* () {
          const payments = yield* Payments;

          const result = yield* payments.customers.subscriptions.update({
            stripeCustomerId: "cus_123",
            targetPlan: "free",
          });

          expect(result.scheduledFor).toBeDefined();
          expect(result.scheduleId).toBe("sub_sched_updated");
          expect(releaseScheduleCalled).toBe(true);
        }).pipe(
          Effect.provide(
            TestDowngradeWithScheduleFixture({
              currentPlan: "pro",
              targetPlan: "free",
              stripeCustomerId: "cus_123",
              subscriptionId: "sub_123",
              existingScheduleId: "sub_sched_existing",
              existingScheduleAsObject: true, // Key: schedule as expanded object
              updatedScheduleId: "sub_sched_updated",
              onScheduleRelease: () => {
                releaseScheduleCalled = true;
              },
            }),
          ),
        );
      },
    );
  });

  describe("updateSubscription - payment intent edge cases", () => {
    it.effect("handles upgrade with no payment_intent in invoice", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers.subscriptions.update({
          stripeCustomerId: "cus_123",
          targetPlan: "pro",
        });

        expect(result.scheduledFor).toBeUndefined();
        expect(result.requiresPayment).toBe(false);
      }).pipe(
        Effect.provide(
          TestUpgradeWithPaymentIntentFixture({
            currentPlan: "free",
            targetPlan: "pro",
            stripeCustomerId: "cus_123",
            requiresPayment: true,
            paymentIntentStatus: null,
            hasPaymentMethod: true,
          }),
        ),
      ),
    );

    it.effect("handles upgrade with payment_intent not requiring payment", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers.subscriptions.update({
          stripeCustomerId: "cus_123",
          targetPlan: "pro",
        });

        expect(result.scheduledFor).toBeUndefined();
        expect(result.requiresPayment).toBe(false);
      }).pipe(
        Effect.provide(
          TestUpgradeWithPaymentIntentFixture({
            currentPlan: "free",
            targetPlan: "pro",
            stripeCustomerId: "cus_123",
            requiresPayment: true,
            paymentIntentStatus: "succeeded",
            hasPaymentMethod: true,
          }),
        ),
      ),
    );

    it.effect("handles upgrade with payment_intent requires_confirmation", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        const result = yield* payments.customers.subscriptions.update({
          stripeCustomerId: "cus_123",
          targetPlan: "pro",
        });

        expect(result.requiresPayment).toBe(true);
        expect(result.clientSecret).toBe("pi_client_secret_mock");
      }).pipe(
        Effect.provide(
          TestUpgradeWithPaymentIntentFixture({
            currentPlan: "free",
            targetPlan: "pro",
            stripeCustomerId: "cus_123",
            requiresPayment: true,
            paymentIntentStatus: "requires_confirmation",
            hasPaymentMethod: true,
          }),
        ),
      ),
    );
  });

  describe("cancel", () => {
    it.effect("cancels all active subscriptions successfully", () => {
      const cancelledSubscriptions: string[] = [];

      return Effect.gen(function* () {
        const payments = yield* Payments;

        yield* payments.customers.subscriptions.cancel("cus_123");

        expect(cancelledSubscriptions).toEqual(["sub_123", "sub_456"]);
      }).pipe(
        Effect.provide(
          TestCancelSubscriptionsFixture({
            subscriptions: [
              { id: "sub_123", status: "active" },
              { id: "sub_456", status: "active" },
            ],
            onSubscriptionCancel: (id) => cancelledSubscriptions.push(id),
          }),
        ),
      );
    });

    it.effect(
      "throws SubscriptionPastDueError when past_due subscriptions exist",
      () =>
        Effect.gen(function* () {
          const payments = yield* Payments;

          const result = yield* payments.customers.subscriptions
            .cancel("cus_123")
            .pipe(Effect.flip);

          assert(result instanceof SubscriptionPastDueError);
          expect(result.message).toContain(
            "Cannot cancel subscriptions - 1 subscription(s) have past_due payments",
          );
          expect(result.stripeCustomerId).toBe("cus_123");
          expect(result.pastDueSubscriptionIds).toEqual(["sub_456"]);
        }).pipe(
          Effect.provide(
            TestCancelSubscriptionsFixture({
              subscriptions: [
                { id: "sub_123", status: "active" },
                { id: "sub_456", status: "past_due" },
              ],
            }),
          ),
        ),
    );

    it.effect(
      "throws SubscriptionPastDueError when only past_due subscriptions exist",
      () =>
        Effect.gen(function* () {
          const payments = yield* Payments;

          const result = yield* payments.customers.subscriptions
            .cancel("cus_123")
            .pipe(Effect.flip);

          assert(result instanceof SubscriptionPastDueError);
          expect(result.message).toContain(
            "Cannot cancel subscriptions - 2 subscription(s) have past_due payments",
          );
          expect(result.pastDueSubscriptionIds).toEqual(["sub_123", "sub_456"]);
        }).pipe(
          Effect.provide(
            TestCancelSubscriptionsFixture({
              subscriptions: [
                { id: "sub_123", status: "past_due" },
                { id: "sub_456", status: "past_due" },
              ],
            }),
          ),
        ),
    );

    it.effect("succeeds when no subscriptions exist", () =>
      Effect.gen(function* () {
        const payments = yield* Payments;

        yield* payments.customers.subscriptions.cancel("cus_123");

        // Test passes if no errors thrown
      }).pipe(
        Effect.provide(
          TestCancelSubscriptionsFixture({
            subscriptions: [],
          }),
        ),
      ),
    );
  });
});
