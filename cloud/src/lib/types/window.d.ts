// Type declarations for global window object
interface Window {
  // Google Analytics
  gtag?: (
    command: string,
    action: string,
    params?: {
      [key: string]: any;
    },
  ) => void;

  // Google Analytics data layer
  dataLayer?: any[];

  // PostHog
  posthog?: {
    init: (
      apiKey: string,
      options?: {
        api_host?: string;
        person_profiles?: "identified_only" | "always";
        capture_pageview?: boolean;
        capture_pageleave?: boolean;
        autocapture?: boolean;
        [key: string]: any;
      },
    ) => void;
    capture: (eventName: string, properties?: Record<string, any>) => void;
    identify: (distinctId: string, properties?: Record<string, any>) => void;
    opt_in_capturing: () => void;
    opt_out_capturing: () => void;
    has_opted_in_capturing: () => boolean;
    has_opted_out_capturing: () => boolean;
    reset: () => void;
    [key: string]: any;
  };
}
