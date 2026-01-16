import type { SubscriptionDetails } from "@/api/organizations.schemas";
import { cloudHostedFeatures } from "@/app/components/pricing-page";
import { PLAN_TIER_ORDER, type PlanTier } from "@/payments/plans";

/**
 * Formats a payment method for display.
 * Shows brand and last 4 digits if available, otherwise a generic message.
 */
export function formatPaymentMethod(subscription: SubscriptionDetails): string {
  if (!subscription.paymentMethod && !subscription.hasPaymentMethod) {
    return "No payment method";
  }

  if (subscription.paymentMethod) {
    const { brand, last4 } = subscription.paymentMethod;
    const capitalizedBrand =
      brand.charAt(0).toUpperCase() + brand.slice(1).toLowerCase();
    return `${capitalizedBrand} ••••${last4}`;
  }

  return "Card on file";
}

/**
 * Determines if a plan change is an upgrade.
 */
export function isUpgrade(
  currentPlan: PlanTier,
  targetPlan: PlanTier,
): boolean {
  return PLAN_TIER_ORDER[targetPlan] > PLAN_TIER_ORDER[currentPlan];
}

/**
 * Plan features to display for each tier.
 */
export interface PlanFeatures {
  users: string;
  tracing: string;
  support: string;
}

/**
 * Gets the features for a specific plan tier.
 */
export function getPlanFeatures(plan: PlanTier): PlanFeatures {
  const userLimit = cloudHostedFeatures.find((f) => f.feature === "Users");
  const tracingLimit = cloudHostedFeatures.find((f) => f.feature === "Tracing");
  const supportChat = cloudHostedFeatures.find(
    (f) => f.feature === "Support (Chat / Email)",
  );

  return {
    users: (userLimit?.[plan] as string) || "Unknown",
    tracing: (tracingLimit?.[plan] as string) || "Unknown",
    support: supportChat?.[plan] ? "Email & Chat Support" : "Community Support",
  };
}
