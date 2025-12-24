/**
 * @fileoverview Centralized configuration for router environment variables.
 *
 * Provides type-safe access to environment variables used across the router
 * implementation, including database, Stripe, and provider API keys.
 */

/**
 * Router configuration interface.
 */
export interface RouterConfig {
  /** Database connection string */
  databaseUrl: string;
  /** Stripe configuration */
  stripe: {
    /** Stripe API secret key */
    apiKey: string;
    /** Stripe router price ID */
    routerPriceId: string;
    /** Stripe router meter ID */
    routerMeterId: string;
  };
}

/**
 * Gets the router configuration from environment variables.
 *
 * @throws Error if required environment variables are not set
 * @returns Router configuration
 */
export function getRouterConfig(): RouterConfig {
  const databaseUrl = process.env.DATABASE_URL;
  const stripeApiKey = process.env.STRIPE_SECRET_KEY;
  const routerPriceId = process.env.STRIPE_ROUTER_PRICE_ID;
  const routerMeterId = process.env.STRIPE_ROUTER_METER_ID;

  if (!databaseUrl) {
    throw new Error("DATABASE_URL environment variable is required");
  }

  if (!stripeApiKey || !routerPriceId || !routerMeterId) {
    throw new Error(
      "Stripe environment variables (STRIPE_SECRET_KEY, STRIPE_ROUTER_PRICE_ID, STRIPE_ROUTER_METER_ID) are required",
    );
  }

  return {
    databaseUrl,
    stripe: {
      apiKey: stripeApiKey,
      routerPriceId,
      routerMeterId,
    },
  };
}

/**
 * Validates that router configuration is available.
 *
 * Returns null if configuration is valid, or an error message if invalid.
 * Useful for early validation without throwing exceptions.
 *
 * @returns Error message if invalid, null if valid
 */
export function validateRouterConfig(): string | null {
  if (!process.env.DATABASE_URL) {
    return "Database not configured";
  }

  if (
    !process.env.STRIPE_SECRET_KEY ||
    !process.env.STRIPE_ROUTER_PRICE_ID ||
    !process.env.STRIPE_ROUTER_METER_ID
  ) {
    return "Stripe configuration incomplete";
  }

  return null;
}
