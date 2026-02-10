import { Check, X } from "lucide-react";
import React, { useEffect, useState } from "react";

import ViewModeSwitcher from "@/app/components/blocks/navigation/view-mode-switcher";
import { useViewMode } from "@/app/components/blocks/theme-provider";
import { Badge } from "@/app/components/ui/badge";
import { ButtonLink } from "@/app/components/ui/button-link";
import { highlightCode, fallbackHighlighter } from "@/app/lib/code-highlight";
import { cn } from "@/app/lib/utils";
import { PLAN_LIMITS, type PlanTier } from "@/payments/plans";

/**
 * Markdown content for MACHINE mode view of the pricing page.
 *
 * IMPORTANT: This content must be kept in sync with TWO other places:
 * 1. `cloudHostedDetails` below (the human-readable pricing table)
 * 2. `public/pricing.md` (the static markdown file served at /pricing.md)
 */
const PRICING_MARKDOWN = `# Mirascope Cloud Pricing

Get started with the Free plan today. No credit card required.

## Plans Overview

### Free - $0/month
For individuals getting started with AI bots.

- **Claws:** 1
- **Instance Size:** Small
- **Seats:** 1
- **Projects:** 1
- **Tracing:** 1M spans/month (hard limit, no overages)
- **Data Retention:** 30 days
- **API Rate Limit:** 100 requests/minute
- **Support:** Community only

### Pro - $49/month
For professionals who need more power.

- **Claws:** 1
- **Instance Size:** Medium
- **Seats:** 5
- **Projects:** 5
- **Tracing:** 1M spans/month included, then $5 per additional million
- **Data Retention:** 90 days
- **API Rate Limit:** 1,000 requests/minute
- **Support:** Community + Chat/Email

### Team - $199/month
For teams running multiple AI bots.

- **Claws:** 3
- **Instance Size:** Large
- **Seats:** Unlimited
- **Projects:** Unlimited
- **Tracing:** 1M spans/month included, then $5 per additional million
- **Data Retention:** 180 days
- **API Rate Limit:** 10,000 requests/minute
- **Support:** Community + Chat/Email + Private Slack

## Plan Comparison Table

| Feature | Free | Pro | Team |
|---------|------|-----|------|
| Claws | 1 | 1 | 3 |
| Instance Size | Small | Medium | Large |
| Seats | 1 | 5 | Unlimited |
| Projects | 1 | 5 | Unlimited |
| Tracing | 1M spans/month (no overages) | 1M spans/month + $5/additional M | 1M spans/month + $5/additional M |
| Data Retention | 30 days | 90 days | 180 days |
| API Rate Limits | 100/minute | 1,000/minute | 10,000/minute |
| Community Support | Yes | Yes | Yes |
| Chat/Email Support | No | Yes | Yes |
| Private Slack Support | No | No | Yes |

## Getting Started

Visit https://mirascope.com/login to create your free account.

## Questions?

Join our community at https://mirascope.com/discord-invite to ask the team directly.
`;

/**
 * Machine-readable pricing content with syntax highlighting
 */
function MachinePricingContent() {
  const [highlightedHtml, setHighlightedHtml] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    highlightCode(PRICING_MARKDOWN, "markdown")
      .then((result) => {
        if (!cancelled) {
          setHighlightedHtml(result.themeHtml);
        }
      })
      .catch(() => {
        if (!cancelled) {
          const fallback = fallbackHighlighter(PRICING_MARKDOWN, "markdown");
          setHighlightedHtml(fallback.themeHtml);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  if (!highlightedHtml) {
    const fallback = fallbackHighlighter(PRICING_MARKDOWN, "markdown");
    return (
      <div className="mx-auto max-w-4xl px-4 py-4">
        <div
          className="machine-mode-code highlight-container w-full overflow-auto rounded-md border text-sm [&>pre]:overflow-x-auto [&>pre]:py-3 [&>pre]:pr-5 [&>pre]:pl-4"
          dangerouslySetInnerHTML={{ __html: fallback.themeHtml }}
        />
        <ViewModeSwitcher />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-4">
      <div
        className="machine-mode-code highlight-container w-full overflow-auto rounded-md border text-sm [&>pre]:overflow-x-auto [&>pre]:py-3 [&>pre]:pr-5 [&>pre]:pl-4"
        dangerouslySetInnerHTML={{ __html: highlightedHtml }}
      />
      <ViewModeSwitcher />
    </div>
  );
}

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
  claws: number;
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
        <p className="text-muted-foreground mb-1">{description}</p>
        <p className="text-muted-foreground mb-4 text-sm">
          {limits.claws} {limits.claws === 1 ? "Claw" : "Claws"} ·{" "}
          {INSTANCE_SIZE[tier]}
        </p>
        <div className="mb-5">
          <span className="text-foreground text-3xl font-bold">{price}</span>
          {price !== "TBD" && price !== "N/A" && (
            <span className="text-muted-foreground ml-1 text-sm">/ month</span>
          )}
        </div>
        {usage && (
          <div className="border-border mb-5 space-y-3 border-t pt-4">
            <UsageIndicator
              label="Claws"
              current={usage.claws}
              limit={limits.claws}
            />
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

/**
 * Cloud hosted plan details for the comparison table.
 *
 * IMPORTANT: This content must be kept in sync with TWO other places:
 * 1. `PRICING_MARKDOWN` above (the machine-readable markdown view)
 * 2. `public/pricing.md` (the static markdown file served at /pricing.md)
 */
/** Instance size display names keyed by plan tier */
const INSTANCE_SIZE: Record<PlanTier, string> = {
  free: "Small",
  pro: "Medium",
  team: "Large",
};

export const cloudHostedDetails = [
  {
    detail: "Claws",
    free: String(PLAN_LIMITS.free.claws),
    pro: String(PLAN_LIMITS.pro.claws),
    team: String(PLAN_LIMITS.team.claws),
  },
  {
    detail: "Instance Size",
    free: INSTANCE_SIZE.free,
    pro: INSTANCE_SIZE.pro,
    team: INSTANCE_SIZE.team,
  },
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
  const viewMode = useViewMode();

  // In MACHINE mode, render markdown content for AI agents
  if (viewMode === "machine") {
    return <MachinePricingContent />;
  }

  // In HUMAN mode, render the full interactive pricing page
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
      <ViewModeSwitcher />
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
      description: "For individuals getting started with AI bots",
      button: hostedActions.free.button,
      isCurrentPlan: currentPlan === "free",
      usage,
    },
    {
      name: "Pro",
      tier: "pro",
      price: "$49",
      description: "For professionals who need more power",
      button: hostedActions.pro.button,
      isCurrentPlan: currentPlan === "pro",
      usage,
    },
    {
      name: "Team",
      tier: "team",
      price: "$199",
      description: "For teams running multiple AI bots",
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
