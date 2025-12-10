import { createFileRoute } from "@tanstack/react-router";
import { LilypadPricing } from "@/mirascope-ui/blocks/lilypad-pricing";
import { PageMeta } from "@/src/components";
import { environment } from "@/src/lib/content/environment";
import { ButtonLink } from "@/mirascope-ui/ui/button-link";

function PricingPageWithMeta() {
  const marketingActions = {
    hosted: {
      free: {
        button: (
          <ButtonLink href="/docs/lilypad/" variant="default">
            Get Started
          </ButtonLink>
        ),
      },
      pro: {
        button: (
          <ButtonLink href="mailto:sales@mirascope.com" variant="outline">
            Contact Us
          </ButtonLink>
        ),
      },
      team: {
        button: (
          <ButtonLink href="mailto:sales@mirascope.com" variant="outline">
            Contact Us
          </ButtonLink>
        ),
      },
    },
    selfHosted: {
      free: {
        button: (
          <ButtonLink href="/docs/lilypad/getting-started/self-hosting" variant="default">
            Get Started
          </ButtonLink>
        ),
      },
      pro: {
        button: (
          <ButtonLink href="mailto:sales@mirascope.com" variant="outline">
            Request License
          </ButtonLink>
        ),
      },
      team: {
        button: (
          <ButtonLink href="mailto:sales@mirascope.com" variant="outline">
            Request License
          </ButtonLink>
        ),
      },
    },
  };

  return (
    <>
      <PageMeta
        title="Lilypad Pricing"
        description="Lilypad's pricing plans and features"
        product="lilypad"
      />
      <LilypadPricing actions={marketingActions} />
    </>
  );
}

export const Route = createFileRoute("/pricing")({
  ssr: false, // Client-side rendered
  component: PricingPageWithMeta,
  onError: (error: Error) => environment.onError(error),
});

