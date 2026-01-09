import { useSubscription } from "@/app/api/organizations";
import { Button } from "@/app/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/app/components/ui/card";
import { Badge } from "@/app/components/ui/badge";
import { PlanBadge, planLabels } from "@/app/components/ui/plan-badge";
import { Check, Loader2 } from "lucide-react";
import {
  formatPaymentMethod,
  isUpgrade,
  getPlanFeatures,
} from "@/app/lib/billing-utils";
import { type PlanTier, PLAN_TIERS } from "@/payments/subscriptions";

interface BillingSettingsProps {
  organizationId: string;
  onUpgrade: (targetPlan: PlanTier) => void;
  onDowngrade: (targetPlan: PlanTier) => void;
  onCancelDowngrade: () => void;
}

export function BillingSettings({
  organizationId,
  onUpgrade,
  onDowngrade,
  onCancelDowngrade,
}: BillingSettingsProps) {
  const { data: subscription, isLoading } = useSubscription(organizationId);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Billing</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!subscription) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Billing</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Unable to load billing information.
          </p>
        </CardContent>
      </Card>
    );
  }

  const currentPlan = subscription.currentPlan;
  const scheduledChange = subscription.scheduledChange;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Billing</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Current Plan Section */}
        <div className="rounded-lg border border-border p-4">
          <div className="mb-2 flex items-center justify-between">
            <h3 className="text-lg font-semibold">Current Plan</h3>
            <PlanBadge plan={currentPlan} />
          </div>
          <div className="space-y-1 text-sm text-muted-foreground">
            <p>
              Billing Period Ends:{" "}
              <span className="font-medium text-foreground">
                {subscription.currentPeriodEnd.toLocaleDateString()}
              </span>
            </p>
            <p>
              Payment Method:{" "}
              <span className="font-medium text-foreground">
                {formatPaymentMethod(subscription)}
              </span>
            </p>
          </div>

          {scheduledChange && (
            <div className="mt-4 rounded-md bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-800 p-3">
              <p className="text-sm font-medium text-amber-900 dark:text-amber-200">
                Scheduled Change
              </p>
              <p className="text-sm text-amber-800 dark:text-amber-300">
                Your plan will change to{" "}
                <strong>{planLabels[scheduledChange.targetPlan]}</strong> on{" "}
                {scheduledChange.effectiveDate.toLocaleDateString()}
              </p>
              <Button
                variant="outline"
                size="sm"
                className="mt-2"
                onClick={onCancelDowngrade}
              >
                Cancel Change
              </Button>
            </div>
          )}
        </div>

        {/* Plan Comparison */}
        <div>
          <h3 className="mb-4 text-lg font-semibold">Available Plans</h3>
          <div className="grid gap-4 md:grid-cols-3">
            {PLAN_TIERS.map((plan) => (
              <PlanCard
                key={plan}
                plan={plan}
                currentPlan={currentPlan}
                scheduledTargetPlan={scheduledChange?.targetPlan}
                onUpgrade={() => onUpgrade(plan)}
                onDowngrade={() => onDowngrade(plan)}
              />
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

interface PlanCardProps {
  plan: PlanTier;
  currentPlan: PlanTier;
  scheduledTargetPlan?: PlanTier;
  onUpgrade: () => void;
  onDowngrade: () => void;
}

function PlanCard({
  plan,
  currentPlan,
  scheduledTargetPlan,
  onUpgrade,
  onDowngrade,
}: PlanCardProps) {
  const isCurrent = plan === currentPlan;
  const isScheduled = plan === scheduledTargetPlan;
  const isPlanUpgrade = isUpgrade(currentPlan, plan);

  // Get features for this plan
  const planFeatures = getPlanFeatures(plan);
  const features = [
    planFeatures.users,
    planFeatures.tracing,
    planFeatures.support,
  ];

  return (
    <div
      className={`rounded-lg border ${
        isCurrent
          ? "border-primary bg-primary/5"
          : isScheduled
            ? "border-amber-500 bg-amber-50 dark:bg-amber-950"
            : "border-border"
      } p-4`}
    >
      <div className="mb-2 flex items-center justify-between">
        <h4 className="text-lg font-semibold">{planLabels[plan]}</h4>
        {isCurrent && (
          <Badge variant="outline" className="text-xs">
            Current
          </Badge>
        )}
        {isScheduled && !isCurrent && (
          <Badge
            variant="outline"
            className="text-xs border-amber-500 text-amber-700 dark:text-amber-400"
          >
            Scheduled
          </Badge>
        )}
      </div>

      <div className="mb-4 space-y-1">
        {features.map((feature, i) => (
          <div key={i} className="flex items-start gap-2 text-sm">
            <Check className="mt-0.5 h-4 w-4 flex-shrink-0 text-primary" />
            <span>{feature}</span>
          </div>
        ))}
      </div>

      <Button
        variant={isCurrent ? "outline" : isPlanUpgrade ? "default" : "outline"}
        className="w-full"
        disabled={isCurrent || isScheduled}
        onClick={isPlanUpgrade ? onUpgrade : onDowngrade}
      >
        {isCurrent
          ? "Current Plan"
          : isScheduled
            ? "Scheduled"
            : isPlanUpgrade
              ? `Upgrade to ${planLabels[plan]}`
              : `Switch to ${planLabels[plan]}`}
      </Button>
    </div>
  );
}
