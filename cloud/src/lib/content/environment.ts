/**
 * Environment utilities for content loading system
 */
export const environment = {
  isDev: () => import.meta.env?.DEV ?? false,
  isProd: () => import.meta.env?.PROD ?? false,
  getMode: () => (import.meta.env?.DEV ? "development" : "production"),
  fetch: (...args: Parameters<typeof fetch>) => fetch(...args),
  // Flag to indicate if we're in prerendering mode (SSG)
  isPrerendering: false,
  // Override onError so we can track when prerendering fails (TanStack catches them automatically)
  onError: (error: Error) => {
    console.error(error);
  },
};
