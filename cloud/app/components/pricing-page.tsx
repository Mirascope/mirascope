import React from "react";
import { cn } from "@/app/lib/utils";
import { ButtonLink } from "@/app/components/ui/button-link";
import { Check, X } from "lucide-react";

interface FeatureRowProps {
  feature: string;
  free: string | boolean;
  pro: string | boolean;
  team: string | boolean;
}
// Feature row component for displaying features with the same value across tiers
const FeatureRow = ({ feature, free, pro, team }: FeatureRowProps) => {
  // If all tiers have the exact same value (and it's not a boolean)
  const allSameNonBoolean =
    free === pro && pro === team && typeof free === "string" && free !== "";

  return (
    <div className="border-border grid min-h-[48px] grid-cols-4 items-center gap-4 border-b py-3">
      <div className="text-foreground text-lg font-medium">{feature}</div>

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

interface PricingTierProps {
  name: string;
  price: string;
  description: string;
  button: React.ReactNode;
}
// Pricing tier component
const PricingTier = ({
  name,
  price,
  description,
  button,
}: PricingTierProps) => (
  <div className="border-border bg-background overflow-hidden rounded-lg border shadow-sm">
    <div className={cn("bg-background px-6 py-6")}>
      <div className="mb-2">
        <h3 className={cn("text-foreground text-xl font-semibold")}>{name}</h3>
      </div>
      <p className="text-muted-foreground mb-4">{description}</p>
      <div className="mb-5">
        <span className="text-foreground text-3xl font-bold">{price}</span>
        {price !== "TBD" && price !== "N/A" && (
          <span className="text-muted-foreground ml-1 text-sm">/ month</span>
        )}
      </div>
      {button}
    </div>
  </div>
);

// Feature comparison table component
export const FeatureComparisonTable = ({
  features,
}: {
  features: FeatureRowProps[];
}) => (
  <div className="border-border bg-background overflow-hidden rounded-lg border shadow-sm">
    <div className="border-border bg-accent border-b px-4 py-5 sm:px-6">
      <h3 className="text-accent-foreground text-lg font-medium">
        Feature Comparison
      </h3>
    </div>
    <div className="bg-background overflow-x-auto px-4 py-5 sm:p-6">
      {/* Table header */}
      <div className="border-border grid grid-cols-4 gap-4 border-b pb-4">
        <div className="text-muted-foreground text-lg font-medium">Feature</div>
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
        {features.map((feat, i) => (
          <FeatureRow key={i} {...feat} />
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

// Cloud hosted features
export const cloudHostedFeatures = [
  { feature: "Seats", free: "1", pro: "5", team: "Unlimited" },
  { feature: "Projects", free: "1", pro: "5", team: "Unlimited" },
  {
    feature: "Tracing",
    free: "1M spans / month\nNo overages",
    pro: "1M spans / month\n$5 / additional million",
    team: "1M spans / month\n$5 / additional million",
  },
  {
    feature: "Data Retention",
    free: "30 days",
    pro: "90 days",
    team: "180 days",
  },
  { feature: "Support (Community)", free: true, pro: true, team: true },
  { feature: "Support (Chat / Email)", free: false, pro: true, team: true },
  { feature: "Support (Private Slack)", free: false, pro: false, team: true },
  {
    feature: "API Rate Limits",
    free: "100 / minute",
    pro: "1000 / minute",
    team: "10000 / minute",
  },
];

interface PricingProps {
  actions: PricingActions;
}

export function PricingPage({ actions }: PricingProps) {
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

        <CloudPricing hostedActions={actions.hosted} />

        {/* Feature comparison table */}
        <FeatureComparisonTable features={cloudHostedFeatures} />

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
}: {
  hostedActions: {
    free: TierAction;
    pro: TierAction;
    team: TierAction;
  };
}) => {
  const pricingTiers: PricingTierProps[] = [
    {
      name: "Free",
      price: "$0",
      description: "For individuals just getting started",
      button: hostedActions.free.button,
    },
    {
      name: "Pro",
      price: "$49",
      description: "For professionals with growing projects",
      button: hostedActions.pro.button,
    },
    {
      name: "Team",
      price: "$199",
      description: "For organizations requiring dedicated support",
      button: hostedActions.team.button,
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
