/**
 * Stripe client configuration for frontend.
 *
 * Provides loadStripe instance and appearance customization matching
 * the application's design system.
 */

import { loadStripe, type Stripe, type Appearance } from "@stripe/stripe-js";

/**
 * Stripe publishable key from environment.
 * This is safe to expose in the frontend.
 */
const stripePublishableKey =
  import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY ||
  process.env.STRIPE_PUBLISHABLE_KEY;

if (!stripePublishableKey) {
  throw new Error(
    "Missing Stripe publishable key. Set VITE_STRIPE_PUBLISHABLE_KEY or STRIPE_PUBLISHABLE_KEY environment variable.",
  );
}

/**
 * Stripe instance promise.
 * Cached to avoid multiple initializations.
 */
let stripePromise: Promise<Stripe | null> | null = null;

/**
 * Get or create Stripe instance.
 *
 * @returns Promise resolving to Stripe instance
 */
export const getStripe = (): Promise<Stripe | null> => {
  if (!stripePromise) {
    stripePromise = loadStripe(stripePublishableKey);
  }
  return stripePromise;
};

/**
 * Stripe Elements appearance configuration.
 *
 * Customizes the Payment Element to match the application's shadcn/ui
 * design system based on Tailwind CSS.
 */
export const stripeAppearance: Appearance = {
  theme: "stripe",
  variables: {
    colorPrimary: "hsl(262.1 83.3% 57.8%)", // primary color from Tailwind
    colorBackground: "hsl(0 0% 100%)", // background
    colorText: "hsl(224 71.4% 4.1%)", // foreground
    colorDanger: "hsl(0 84.2% 60.2%)", // destructive
    fontFamily:
      'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    spacingUnit: "4px",
    borderRadius: "6px", // rounded-md
  },
  rules: {
    ".Input": {
      border: "1px solid hsl(214.3 31.8% 91.4%)", // border
      boxShadow: "none",
    },
    ".Input:focus": {
      border: "1px solid hsl(262.1 83.3% 57.8%)", // ring color
      boxShadow: "0 0 0 3px hsla(262.1, 83.3%, 57.8%, 0.1)", // ring
    },
    ".Input--invalid": {
      border: "1px solid hsl(0 84.2% 60.2%)", // destructive
    },
    ".Label": {
      fontWeight: "500",
      color: "hsl(224 71.4% 4.1%)", // foreground
    },
    ".Error": {
      color: "hsl(0 84.2% 60.2%)", // destructive
    },
  },
};
