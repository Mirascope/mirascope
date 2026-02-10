import type React from "react";

import { createFileRoute } from "@tanstack/react-router";
import { Loader2 } from "lucide-react";

import type { PlanTier } from "@/payments/plans";

import { useClaws } from "@/app/api/claws";
import { useOrganizationMembers } from "@/app/api/organization-memberships";
import { useSubscription } from "@/app/api/organizations";
import { useProjects } from "@/app/api/projects";
import { PricingPage, type UsageData } from "@/app/components/pricing-page";
import { Button } from "@/app/components/ui/button";
import { ButtonLink } from "@/app/components/ui/button-link";
import { useAuth } from "@/app/contexts/auth";
import {
  OrganizationProvider,
  useOrganization,
} from "@/app/contexts/organization";
import { isUpgrade } from "@/app/lib/billing-utils";
import { createStaticRouteHead } from "@/app/lib/seo/static-route-head";

function getTierButton(
  tier: PlanTier,
  currentPlan: PlanTier,
  orgSlug: string,
): React.ReactNode {
  if (tier === currentPlan) {
    return (
      <Button disabled variant="outline" className="w-full">
        Current Plan
      </Button>
    );
  }

  // Guard against empty orgSlug — fall back to login
  const billingHref = orgSlug
    ? `/${orgSlug}/settings/billing`
    : "/login";

  const isPlanUpgrade = isUpgrade(currentPlan, tier);

  if (isPlanUpgrade) {
    return (
      <ButtonLink
        href={billingHref}
        variant="default"
        className="w-full"
      >
        Upgrade
      </ButtonLink>
    );
  }

  return (
    <ButtonLink
      href={billingHref}
      variant="outline"
      className="w-full"
    >
      Downgrade
    </ButtonLink>
  );
}

function buildPricingActions({
  user,
  currentPlan,
  isLoading,
  orgSlug,
}: {
  user: unknown;
  currentPlan?: PlanTier;
  isLoading: boolean;
  orgSlug: string;
}) {
  // Unauthenticated: "Get Started" -> login
  if (!user) {
    return {
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
  }

  // Authenticated but loading subscription data
  if (isLoading || !currentPlan) {
    return {
      hosted: {
        free: {
          button: (
            <Button disabled className="w-full">
              <Loader2 className="h-4 w-4 animate-spin" />
            </Button>
          ),
        },
        pro: {
          button: (
            <Button disabled variant="outline" className="w-full">
              <Loader2 className="h-4 w-4 animate-spin" />
            </Button>
          ),
        },
        team: {
          button: (
            <Button disabled variant="outline" className="w-full">
              <Loader2 className="h-4 w-4 animate-spin" />
            </Button>
          ),
        },
      },
    };
  }

  // Authenticated with known plan
  return {
    hosted: {
      free: { button: getTierButton("free", currentPlan, orgSlug) },
      pro: { button: getTierButton("pro", currentPlan, orgSlug) },
      team: { button: getTierButton("team", currentPlan, orgSlug) },
    },
  };
}

function PricingContent() {
  const { user, isLoading: authLoading } = useAuth();
  const { selectedOrganization, isLoading: orgLoading } = useOrganization();

  const organizationId = user ? selectedOrganization?.id : undefined;

  const { data: subscription, isLoading: subLoading } =
    useSubscription(organizationId);
  const { data: projects } = useProjects(organizationId ?? null);
  const { data: members } = useOrganizationMembers(organizationId ?? null);
  const { data: claws } = useClaws(organizationId ?? null);

  const currentPlan = subscription?.currentPlan;

  const pricingActions = buildPricingActions({
    user,
    currentPlan,
    isLoading: authLoading || orgLoading || subLoading,
    orgSlug: selectedOrganization?.slug ?? "",
  });

  // Build usage data for authenticated users
  const usage: UsageData | undefined = user
    ? {
        projects: projects?.length ?? 0,
        seats: members?.length ?? 0,
        claws: claws?.length ?? 0,
      }
    : undefined;

  return (
    <PricingPage
      actions={pricingActions}
      currentPlan={currentPlan}
      usage={usage}
    />
  );
}

function PricingRoute() {
  return (
    <OrganizationProvider>
      <PricingContent />
    </OrganizationProvider>
  );
}

export const Route = createFileRoute("/pricing")({
  head: createStaticRouteHead("/pricing"),
  component: PricingRoute,
});
