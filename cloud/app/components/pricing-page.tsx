import { Check, X } from "lucide-react";
import React from "react";

import { Badge } from "@/app/components/ui/badge";
import { ButtonLink } from "@/app/components/ui/button-link";
import { cn } from "@/app/lib/utils";
import { PLAN_LIMITS, type PlanTier } from "@/payments/plans";

interface PlanDetailsRowProps {
  detail: string;
  free: string | boolean | React.ReactElement;
  pro: string | boolean | React.ReactElement;
  team: string | boolean | React.ReactElement;
}
// Plan details component for displaying plan details with the same value across tiers
const PlanDetailsRow = ({ detail, free, pro, team }: PlanDetailsRowProps) => {
  // If all tiers have the exact same value (and it's not a boolean)
  const allSameNonBoolean =
    free === pro && pro === team && typeof free === "string" && free !== "";

  return (
    <div className="border-border grid min-h-[48px] grid-cols-4 items-center gap-4 border-b py-3">
      <div className="text-foreground text-lg font-medium">{detail}</div>

      {allSameNonBoolean ? (
        <div className="col-span-3 text-center text-lg whitespace-pre-line">
          {free}
        </div>
      ) : (
        <>
          <div className="text-center">
            {typeof free === "boolean" ? (
              <div className="flex justify-center">
                {free ? (
                  <div className="bg-primary/30 rounded-full p-1">
                    <Check size={16} className="text-primary" />
                  </div>
                ) : (
                  <div className="bg-muted rounded-full p-1">
                    <X size={16} className="text-muted-foreground" />
                  </div>
                )}
              </div>
            ) : (
              <span className="text-foreground text-lg whitespace-pre-line">
                {free}
              </span>
            )}
          </div>

          <div className="text-center">
            {typeof pro === "boolean" ? (
              <div className="flex justify-center">
                {pro ? (
                  <div className="bg-primary/30 rounded-full p-1">
                    <Check size={16} className="text-primary" />
                  </div>
                ) : (
                  <div className="bg-muted rounded-full p-1">
                    <X size={16} className="text-muted-foreground" />
                  </div>
                )}
              </div>
            ) : (
              <span className="text-foreground text-lg whitespace-pre-line">
                {pro}
              </span>
            )}
          </div>

          <div className="text-center">
            {typeof team === "boolean" ? (
              <div className="flex justify-center">
                {team ? (
                  <div className="bg-primary/30 rounded-full p-1">
                    <Check size={16} className="text-primary" />
                  </div>
                ) : (
                  <div className="bg-muted rounded-full p-1">
                    <X size={16} className="text-muted-foreground" />
                  </div>
                )}
              </div>
            ) : (
              <span className="text-foreground text-lg whitespace-pre-line">
                {team}
              </span>
            )}
          </div>
        </>
      )}
    </div>
  );
};

// Current usage data for authenticated users (without limits - limits come from the plan)
export interface UsageData {
  projects: number;
  seats: number;
}

interface UsageIndicatorProps {
  label: string;
  current: number;
  limit: number;
}

// Usage indicator component with progress bar
function UsageIndicator({ label, current, limit }: UsageIndicatorProps) {
  const isUnlimited = limit === Infinity;
  const isOverLimit = !isUnlimited && current > limit;
  // For unlimited: show a small blip (5%); otherwise calculate actual percentage
  const percentage = isUnlimited ? 5 : Math.min((current / limit) * 100, 100);

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-muted-foreground">{label}</span>
        <span className={cn("font-medium", isOverLimit && "text-destructive")}>
          {current}/
          {isUnlimited ? <span className="text-l font-sans">∞</span> : limit}
        </span>
      </div>
      <div className="bg-muted h-2 overflow-hidden rounded-full">
        <div
          className={cn(
            "h-full rounded-full transition-all",
            isOverLimit ? "bg-destructive" : "bg-primary",
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

interface PricingTierProps {
  name: string;
  tier: PlanTier;
  price: string;
  description: string;
  button: React.ReactNode;
  isCurrentPlan?: boolean;
  usage?: UsageData;
}
// Pricing tier component
const PricingTier = ({
  name,
  tier,
  price,
  description,
  button,
  isCurrentPlan,
  usage,
}: PricingTierProps) => {
  const limits = PLAN_LIMITS[tier];

  return (
    <div
      className={cn(
        "border-border bg-background relative overflow-hidden rounded-lg border shadow-sm",
        isCurrentPlan && "border-primary border-2",
      )}
    >
      {isCurrentPlan && (
        <Badge className="bg-primary text-primary-foreground absolute -top-0 right-3 rounded-t-none">
          Current Plan
        </Badge>
      )}
      <div className={cn("bg-background px-6 py-6")}>
        <div className="mb-2">
          <h3 className={cn("text-foreground text-xl font-semibold")}>
            {name}
          </h3>
        </div>
        <p className="text-muted-foreground mb-4">{description}</p>
        <div className="mb-5">
          <span className="text-foreground text-3xl font-bold">{price}</span>
          {price !== "TBD" && price !== "N/A" && (
            <span className="text-muted-foreground ml-1 text-sm">/ month</span>
          )}
        </div>
        {usage && (
          <div className="border-border mb-5 space-y-3 border-t pt-4">
            <UsageIndicator
              label="Seats"
              current={usage.seats}
              limit={limits.seats}
            />
            <UsageIndicator
              label="Projects"
              current={usage.projects}
              limit={limits.projects}
            />
          </div>
        )}
        {button}
      </div>
    </div>
  );
};

// Plan comparison table component
export const PlanComparisonTable = ({
  details,
}: {
  details: PlanDetailsRowProps[];
}) => (
  <div className="border-border bg-background overflow-hidden rounded-lg border shadow-sm">
    <div className="border-border bg-accent border-b px-4 py-5 sm:px-6">
      <h3 className="text-accent-foreground text-lg font-medium">
        Plan Comparison
      </h3>
    </div>
    <div className="bg-background overflow-x-auto px-4 py-5 sm:p-6">
      {/* Table header */}
      <div className="border-border grid grid-cols-4 gap-4 border-b pb-4">
        <div className="text-muted-foreground text-lg font-medium">Detail</div>
        <div className="text-muted-foreground text-center text-lg font-medium">
          Free
        </div>
        <div className="text-muted-foreground text-center text-lg font-medium">
          Pro
        </div>
        <div className="text-muted-foreground text-center text-lg font-medium">
          Team
        </div>
      </div>

      {/* Table rows */}
      <div className="[&>*:last-child]:border-b-0">
        {details.map((feat, i) => (
          <PlanDetailsRow key={i} {...feat} />
        ))}
      </div>
    </div>
  </div>
);

interface TierAction {
  button: React.ReactNode;
}

interface PricingActions {
  hosted: {
    free: TierAction;
    pro: TierAction;
    team: TierAction;
  };
}

// Cloud hosted details
export const cloudHostedDetails = [
  { detail: "Seats", free: "1", pro: "5", team: "Unlimited" },
  { detail: "Projects", free: "1", pro: "5", team: "Unlimited" },
  {
    detail: "Tracing",
    free: (
      <span>
        1M spans / month
        <br />
        No overages
      </span>
    ),
    pro: (
      <span>
        1M spans / month
        <br />
        $5 / additional million
      </span>
    ),
    team: (
      <span>
        1M spans / month
        <br />
        $5 / additional million
      </span>
    ),
  },
  {
    detail: "Data Retention",
    free: "30 days",
    pro: "90 days",
    team: "180 days",
  },
  { detail: "Support (Community)", free: true, pro: true, team: true },
  { detail: "Support (Chat / Email)", free: false, pro: true, team: true },
  { detail: "Support (Private Slack)", free: false, pro: false, team: true },
  {
    detail: "API Rate Limits",
    free: "100 / minute",
    pro: "1,000 / minute",
    team: "10,000 / minute",
  },
];

interface PricingProps {
  actions: PricingActions;
  currentPlan?: PlanTier;
  usage?: UsageData;
}

export function PricingPage({ actions, currentPlan, usage }: PricingProps) {
  return (
    <div className="px-4 py-4">
      <div className="mx-auto max-w-4xl">
        <div className="mb-4 text-center">
          <h1 className="text-foreground mb-4 text-center text-4xl font-bold">
            Pricing
          </h1>
          <p className="text-foreground mx-auto mb-2 max-w-2xl text-xl">
            Get started with the Free plan today.
          </p>
          <p className="text-muted-foreground mx-auto max-w-2xl text-sm italic">
            No credit card required.
          </p>
        </div>

        <CloudPricing
          hostedActions={actions.hosted}
          currentPlan={currentPlan}
          usage={usage}
        />

        {/* Plan comparison table */}
        <PlanComparisonTable details={cloudHostedDetails} />

        <div className="mt-16 text-center">
          <h2 className="text-foreground mb-4 text-2xl font-semibold">
            Have questions about our pricing?
          </h2>
          <p className="text-muted-foreground">
            Join our{" "}
            <ButtonLink
              href="https://mirascope.com/discord-invite?"
              variant="link"
              className="h-auto p-0"
            >
              community
            </ButtonLink>{" "}
            and ask the team directly!
          </p>
        </div>
      </div>
    </div>
  );
}

export const CloudPricing = ({
  hostedActions,
  currentPlan,
  usage,
}: {
  hostedActions: {
    free: TierAction;
    pro: TierAction;
    team: TierAction;
  };
  currentPlan?: PlanTier;
  usage?: UsageData;
}) => {
  const pricingTiers: PricingTierProps[] = [
    {
      name: "Free",
      tier: "free",
      price: "$0",
      description: "For individuals just getting started",
      button: hostedActions.free.button,
      isCurrentPlan: currentPlan === "free",
      usage,
    },
    {
      name: "Pro",
      tier: "pro",
      price: "$49",
      description: "For professionals with growing projects",
      button: hostedActions.pro.button,
      isCurrentPlan: currentPlan === "pro",
      usage,
    },
    {
      name: "Team",
      tier: "team",
      price: "$199",
      description: "For organizations requiring dedicated support",
      button: hostedActions.team.button,
      isCurrentPlan: currentPlan === "team",
      usage,
    },
  ];
  return (
    <div className="mb-10 grid gap-8 md:grid-cols-3">
      {pricingTiers.map((tier) => (
        <PricingTier key={tier.name} {...tier} />
      ))}
    </div>
  );
};
