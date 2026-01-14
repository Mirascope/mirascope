import { createFileRoute } from "@tanstack/react-router";
import { PricingPage } from "@/app/components/pricing-page";
import { ButtonLink } from "@/app/components/ui/button-link";
import { createPageHead } from "@/app/lib/seo/head";

const marketingActions = {
  hosted: {
    free: {
      button: (
        <ButtonLink href="/docs" variant="default">
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
        <ButtonLink href="/docs/getting-started/self-hosting" variant="default">
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

export const Route = createFileRoute("/pricing")({
  head: () =>
    createPageHead({
      route: "/pricing",
      title: "Pricing",
      description: "Mirascope cloud's pricing plans and features",
    }),
  component: () => <PricingPage actions={marketingActions} />,
});
