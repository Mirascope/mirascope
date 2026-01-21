import type React from "react";
import { createFileRoute } from "@tanstack/react-router";
import { PricingPage, type UsageData } from "@/app/components/pricing-page";
import { ButtonLink } from "@/app/components/ui/button-link";
import { Button } from "@/app/components/ui/button";
import { createPageHead } from "@/app/lib/seo/head";
import { useAuth } from "@/app/contexts/auth";
import {
  OrganizationProvider,
  useOrganization,
} from "@/app/contexts/organization";
import { useSubscription } from "@/app/api/organizations";
import { useProjects } from "@/app/api/projects";
import { useOrganizationMembers } from "@/app/api/organization-memberships";
import type { PlanTier } from "@/payments/plans";
import { isUpgrade } from "@/app/lib/billing-utils";
import { Loader2 } from "lucide-react";

function getTierButton(tier: PlanTier, currentPlan: PlanTier): React.ReactNode {
  if (tier === currentPlan) {
    return (
      <Button disabled variant="outline" className="w-full">
        Current Plan
      </Button>
    );
  }

  const isPlanUpgrade = isUpgrade(currentPlan, tier);

  if (isPlanUpgrade) {
    return (
      <ButtonLink
        href="/cloud/settings/billing"
        variant="default"
        className="w-full"
      >
        Upgrade
      </ButtonLink>
    );
  }

  return (
    <ButtonLink
      href="/cloud/settings/billing"
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
}: {
  user: unknown;
  currentPlan?: PlanTier;
  isLoading: boolean;
}) {
  // Unauthenticated: "Get Started" -> login
  if (!user) {
    return {
      hosted: {
        free: {
          button: (
            <ButtonLink href="/cloud/login" variant="default">
              Get Started
            </ButtonLink>
          ),
        },
        pro: {
          button: (
            <ButtonLink href="/cloud/login" variant="outline">
              Get Started
            </ButtonLink>
          ),
        },
        team: {
          button: (
            <ButtonLink href="/cloud/login" variant="outline">
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
      free: { button: getTierButton("free", currentPlan) },
      pro: { button: getTierButton("pro", currentPlan) },
      team: { button: getTierButton("team", currentPlan) },
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

  const currentPlan = subscription?.currentPlan;

  const pricingActions = buildPricingActions({
    user,
    currentPlan,
    isLoading: authLoading || orgLoading || subLoading,
  });

  // Build usage data for authenticated users
  const usage: UsageData | undefined = user
    ? {
        projects: projects?.length ?? 0,
        seats: members?.length ?? 0,
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
  head: () =>
    createPageHead({
      route: "/pricing",
      title: "Pricing",
      description: "Mirascope cloud's pricing plans and features",
    }),
  component: PricingRoute,
});
