import { createFileRoute } from "@tanstack/react-router";
import { PricingPage } from "@/app/components/pricing-page";
import { ButtonLink } from "@/app/components/ui/button-link";
import { createPageHead } from "@/app/lib/seo/head";

const pricingActions = {
  hosted: {
    free: {
      button: (
        <ButtonLink href="/login" variant="default">
          Get Started
        </ButtonLink>
      ),
    },
    pro: {
      button: (
        <ButtonLink href="/login" variant="outline">
          Get Started
        </ButtonLink>
      ),
    },
    team: {
      button: (
        <ButtonLink href="/login" variant="outline">
          Get Started
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
  component: () => <PricingPage actions={pricingActions} />,
});
