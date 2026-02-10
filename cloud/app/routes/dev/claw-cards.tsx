import { createFileRoute, useLoaderData } from "@tanstack/react-router";

import type { Claw } from "@/api/claws.schemas";

import DevLayout from "@/app/components/blocks/dev/dev-layout";
import LoadingContent from "@/app/components/blocks/loading-content";
import { ClawCard } from "@/app/components/claw-card";
import { getAllDevMeta } from "@/app/lib/content/virtual-module";

const baseClaw: Claw = {
  id: "00000000-0000-0000-0000-000000000001",
  slug: "my-claw",
  displayName: "My Claw",
  description: null,
  organizationId: "00000000-0000-0000-0000-000000000002",
  createdByUserId: "00000000-0000-0000-0000-000000000003",
  status: "active",
  instanceType: "basic",
  lastDeployedAt: null,
  lastError: null,
  secretsEncrypted: null,
  secretsKeyId: null,
  bucketName: null,
  botUserId: null,
  homeProjectId: null,
  homeEnvironmentId: null,
  weeklySpendingGuardrailCenticents: null,
  weeklyWindowStart: new Date(),
  weeklyUsageCenticents: 3500n,
  burstWindowStart: new Date(),
  burstUsageCenticents: 800n,
  createdAt: new Date(),
  updatedAt: new Date(),
};

const statuses: Claw["status"][] = [
  "active",
  "pending",
  "provisioning",
  "error",
  "paused",
];

const instanceTypes: Claw["instanceType"][] = [
  "lite",
  "basic",
  "standard-1",
  "standard-2",
  "standard-3",
  "standard-4",
];

export const Route = createFileRoute("/dev/claw-cards")({
  component: ClawCardsDevPage,
  loader: () => {
    const devPages = getAllDevMeta();
    return { devPages };
  },
  pendingComponent: () => {
    return (
      <DevLayout devPages={[]}>
        <div className="container">
          <LoadingContent spinnerClassName="h-12 w-12" fullHeight={false} />
        </div>
      </DevLayout>
    );
  },
});

function ClawCardsDevPage() {
  const { devPages } = useLoaderData({ from: "/dev/claw-cards" });

  return (
    <DevLayout devPages={devPages}>
      <div className="p-8 space-y-10 max-w-4xl mx-auto">
        <div>
          <h1 className="text-2xl font-semibold mb-2">Claw Card Variants</h1>
          <p className="text-muted-foreground mb-6">
            All status and instance type combinations
          </p>
        </div>

        {/* By Status */}
        <div className="space-y-6">
          <h2 className="text-lg font-semibold">By Status</h2>
          <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
            {statuses.map((status) => (
              <ClawCard
                key={status}
                claw={{
                  ...baseClaw,
                  status,
                  displayName: `${status.charAt(0).toUpperCase()}${status.slice(1)} Claw`,
                  slug: `${status}-claw`,
                }}
                burstLimitCenticents={2_000}
              />
            ))}
          </div>
        </div>

        {/* By Instance Type */}
        <div className="space-y-6">
          <h2 className="text-lg font-semibold">By Instance Type</h2>
          <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
            {instanceTypes.map((instanceType) => (
              <ClawCard
                key={instanceType}
                claw={{
                  ...baseClaw,
                  instanceType,
                  displayName: `${instanceType} Instance`,
                  slug: `${instanceType}-instance`,
                }}
                burstLimitCenticents={2_000}
              />
            ))}
          </div>
        </div>

        {/* Long Name Truncation */}
        <div className="space-y-6">
          <h2 className="text-lg font-semibold">Edge Cases</h2>
          <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
            <ClawCard
              claw={{
                ...baseClaw,
                displayName:
                  "Very Long Claw Name That Should Truncate Properly",
                slug: "very-long-claw-name-that-should-truncate",
              }}
              burstLimitCenticents={2_000}
            />
            <ClawCard
              claw={{
                ...baseClaw,
                displayName: null,
                slug: "slug-only-no-display-name",
              }}
              burstLimitCenticents={2_000}
            />
            <ClawCard
              claw={{
                ...baseClaw,
                status: "error",
                instanceType: "standard-4",
                displayName: "Error XL",
                slug: "error-xl",
                lastError: "Deployment failed",
              }}
              burstLimitCenticents={2_000}
            />
          </div>
        </div>

        {/* Usage Meter States */}
        <div className="space-y-6">
          <h2 className="text-lg font-semibold">Usage Meter States</h2>
          <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
            <ClawCard
              claw={{
                ...baseClaw,
                displayName: "Low Usage",
                slug: "low-usage",
                weeklyUsageCenticents: 1_000n,
                burstUsageCenticents: 200n,
              }}
              burstLimitCenticents={2_000}
            />
            <ClawCard
              claw={{
                ...baseClaw,
                displayName: "Near Limit (>90%)",
                slug: "near-limit",
                weeklyUsageCenticents: 9_500n,
                burstUsageCenticents: 1_900n,
              }}
              burstLimitCenticents={2_000}
            />
            <ClawCard
              claw={{
                ...baseClaw,
                status: "paused",
                displayName: "Over Limit",
                slug: "over-limit",
                weeklyUsageCenticents: 12_000n,
                burstUsageCenticents: 2_500n,
              }}
              burstLimitCenticents={2_000}
            />
            <ClawCard
              claw={{
                ...baseClaw,
                displayName: "No Usage Data",
                slug: "no-usage-data",
                weeklyUsageCenticents: null,
                burstUsageCenticents: null,
              }}
              burstLimitCenticents={2_000}
            />
            <ClawCard
              claw={{
                ...baseClaw,
                displayName: "No Limits Passed",
                slug: "no-limits",
              }}
            />
          </div>
        </div>

        {/* All Status + Instance Combos (compact) */}
        <div className="space-y-6">
          <h2 className="text-lg font-semibold">Status x Instance Matrix</h2>
          {statuses.map((status) => (
            <div key={status} className="space-y-2">
              <h3 className="text-sm font-medium text-muted-foreground capitalize">
                {status}
              </h3>
              <div className="grid gap-3 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
                {instanceTypes.map((instanceType) => (
                  <ClawCard
                    key={`${status}-${instanceType}`}
                    claw={{
                      ...baseClaw,
                      status,
                      instanceType,
                      displayName: `${status} ${instanceType}`,
                      slug: `${status}-${instanceType}`,
                    }}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </DevLayout>
  );
}
