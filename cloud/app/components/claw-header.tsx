import type { Claw } from "@/api/claws.schemas";
import type { PlanTier } from "@/payments/plans";

import { useSubscription } from "@/app/api/organizations";
import {
  instanceConfig,
  statusBarColor,
  statusConfig,
  UsageMeter,
} from "@/app/components/claw-card";
import { Badge } from "@/app/components/ui/badge";
import { useClaw } from "@/app/contexts/claw";
import { useOrganization } from "@/app/contexts/organization";
import { PLAN_LIMITS } from "@/payments/plans";

function ClawHeaderContent({ claw }: { claw: Claw }) {
  const { selectedOrganization } = useOrganization();
  const { claws } = useClaw();
  const { data: subscription } = useSubscription(selectedOrganization?.id);

  const planTier: PlanTier = subscription?.currentPlan ?? "free";
  const limits = PLAN_LIMITS[planTier];
  const weeklyUsage = claws.reduce(
    (sum, c) => sum + Number(c.weeklyUsageCenticents ?? 0n),
    0,
  );

  return (
    <>
      <div className="flex items-center gap-2 mb-1">
        <h1 className="text-2xl font-semibold">
          {claw.displayName ?? claw.slug}
        </h1>
        <Badge
          pill
          variant="outline"
          className="shrink-0 font-normal bg-white text-primary border-primary/40 dark:bg-primary/10 dark:text-primary-foreground dark:border-primary/40"
        >
          {instanceConfig[claw.instanceType]}
        </Badge>
        <Badge
          pill
          variant="outline"
          className={`shrink-0 ${statusConfig[claw.status].pill}`}
        >
          {statusConfig[claw.status].label}
        </Badge>
      </div>
      <div className="space-y-1 mb-6 max-w-48">
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground w-10 shrink-0">
            Burst
          </span>
          <UsageMeter
            usage={Number(claw.burstUsageCenticents ?? 0n)}
            limit={limits.burstCreditsCenticents}
            barColor={statusBarColor[claw.status]}
            className="flex-1"
          />
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground w-10 shrink-0">
            Weekly
          </span>
          <UsageMeter
            usage={weeklyUsage}
            limit={limits.includedCreditsCenticents}
            barColor={statusBarColor[claw.status]}
            className="flex-1"
          />
        </div>
      </div>
    </>
  );
}

export function ClawHeader() {
  const { selectedClaw } = useClaw();

  if (!selectedClaw) {
    return (
      <p className="text-muted-foreground mb-6">
        Select a claw from the sidebar to get started
      </p>
    );
  }

  return <ClawHeaderContent claw={selectedClaw} />;
}
