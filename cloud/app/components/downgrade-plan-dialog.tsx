import { useState, useEffect } from "react";
import { Button } from "@/app/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/app/components/ui/dialog";
import {
  useUpdateSubscription,
  usePreviewSubscriptionChange,
} from "@/app/api/organizations";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";
// Import from /types directly to avoid pulling in server-only database dependencies
import type { PlanTier } from "@/payments/subscriptions/types";
import type {
  ValidationError,
  SubscriptionChangePreview,
} from "@/api/organizations.schemas";
import { AlertTriangle, CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { planLabels } from "@/app/components/ui/plan-badge";

interface DowngradePlanDialogProps {
  organizationId: string;
  currentPlan: PlanTier;
  targetPlan: PlanTier;
  periodEnd: Date;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const featureLossWarnings: Record<PlanTier, Record<PlanTier, string[]>> = {
  team: {
    team: [], // Same plan
    pro: [
      "Private Slack Support",
      "Reduced user limit",
      "Reduced API rate limits",
    ],
    free: [
      "Private Slack Support",
      "Email & Chat Support",
      "Significantly reduced user limit",
      "Significantly reduced span quota",
      "Shorter data retention",
      "Reduced API rate limits",
    ],
  },
  pro: {
    team: [], // Can't downgrade from pro to team (upgrade)
    pro: [], // Same plan
    free: [
      "Email & Chat Support",
      "Reduced user limit",
      "Reduced span quota",
      "Shorter data retention",
      "Reduced API rate limits",
    ],
  },
  free: {
    team: [], // Can't downgrade from free (upgrade)
    pro: [], // Can't downgrade from free (upgrade)
    free: [], // Same plan
  },
};

const RESOURCE_LABELS: Record<string, string> = {
  seats: "Team Members",
  projects: "Projects",
};

function DowngradeBlockedContent({
  validationErrors,
  targetPlan,
}: {
  validationErrors: readonly ValidationError[];
  targetPlan: PlanTier;
}) {
  return (
    <div className="space-y-4 py-4">
      <div className="rounded-lg border-2 border-destructive/50 bg-destructive/10 p-4">
        <p className="text-sm font-medium text-destructive mb-3">
          Cannot downgrade to {planLabels[targetPlan]}
        </p>
        <p className="text-sm text-muted-foreground mb-4">
          Your current usage exceeds the {planLabels[targetPlan]} plan limits.
          Please reduce your usage before downgrading:
        </p>

        <div className="space-y-2">
          {validationErrors.map((error) => (
            <div
              key={error.resource}
              className="flex items-center justify-between rounded-md border border-destructive/30 bg-background p-3"
            >
              <div className="flex items-center gap-2">
                <XCircle className="h-5 w-5 text-destructive" />
                <div>
                  <p className="text-sm font-medium capitalize">
                    {RESOURCE_LABELS[error.resource] || error.resource}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {error.currentUsage} / {error.limit} allowed
                  </p>
                </div>
              </div>
              <span className="text-sm font-medium text-destructive">
                Remove {error.currentUsage - error.limit}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-lg border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-950 p-4">
        <p className="text-sm text-amber-800 dark:text-amber-300">
          <strong className="text-amber-900 dark:text-amber-200">
            Next steps:
          </strong>{" "}
          {validationErrors.map((error, i) => {
            const action =
              error.resource === "seats"
                ? `remove ${error.currentUsage - error.limit} member${error.currentUsage - error.limit > 1 ? "s" : ""}`
                : `delete ${error.currentUsage - error.limit} project${error.currentUsage - error.limit > 1 ? "s" : ""}`;
            return (
              <span key={error.resource}>
                {i > 0 && " and "}
                {action}
              </span>
            );
          })}
          .
        </p>
      </div>
    </div>
  );
}

function DowngradeAllowedContent({
  targetPlan,
  currentPlan,
  periodEnd,
  featuresLost,
  validationErrors,
}: {
  targetPlan: PlanTier;
  currentPlan: PlanTier;
  periodEnd: Date;
  featuresLost: string[];
  validationErrors?: readonly ValidationError[];
}) {
  return (
    <div className="space-y-4 py-4">
      {/* Usage Check - Green checkmarks */}
      {validationErrors && validationErrors.length === 0 && (
        <div className="rounded-lg border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-950 p-4">
          <p className="text-sm font-medium text-green-900 dark:text-green-200 mb-3">
            ✓ Usage within {planLabels[targetPlan]} limits
          </p>
          <div className="space-y-1">
            {["seats", "projects"].map((resource) => (
              <div
                key={resource}
                className="flex items-center gap-2 text-sm text-green-800 dark:text-green-300"
              >
                <CheckCircle2 className="h-4 w-4" />
                <span className="capitalize">
                  {RESOURCE_LABELS[resource] || resource}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Scheduled Change Info */}
      <div className="rounded-lg border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-950 p-4">
        <p className="text-sm font-medium text-amber-900 dark:text-amber-200 mb-2">
          Scheduled Change
        </p>
        <p className="text-sm text-amber-800 dark:text-amber-300">
          Your plan will change to <strong>{planLabels[targetPlan]}</strong> on{" "}
          <strong>{periodEnd.toLocaleDateString()}</strong>. You'll continue to
          have access to {planLabels[currentPlan]} features until then.
        </p>
      </div>

      {/* Features Lost */}
      {featuresLost.length > 0 && (
        <div>
          <p className="text-sm font-medium text-foreground mb-2">
            Features you'll lose:
          </p>
          <ul className="space-y-1">
            {featuresLost.map((feature, i) => (
              <li
                key={i}
                className="text-sm text-muted-foreground flex items-start gap-2"
              >
                <span className="text-destructive mt-1">•</span>
                <span>{feature}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* No Refunds Warning */}
      <div className="rounded-lg border border-border bg-muted/50 p-4">
        <p className="text-sm text-muted-foreground">
          <strong className="text-foreground">No refunds:</strong> You won't be
          refunded for the remainder of your current billing period.
        </p>
      </div>
    </div>
  );
}

export function DowngradePlanDialog({
  organizationId,
  currentPlan,
  targetPlan,
  periodEnd,
  open,
  onOpenChange,
}: DowngradePlanDialogProps) {
  const [isConfirming, setIsConfirming] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [preview, setPreview] = useState<SubscriptionChangePreview | null>(
    null,
  );
  const queryClient = useQueryClient();
  const updateMutation = useUpdateSubscription();
  const previewMutation = usePreviewSubscriptionChange();

  const featuresLost = featureLossWarnings[currentPlan]?.[targetPlan] || [];

  // Fetch preview when dialog opens
  useEffect(() => {
    if (open) {
      let cancelled = false;
      setIsLoading(true);
      previewMutation
        .mutateAsync({
          organizationId,
          data: { targetPlan },
        })
        .then((result) => {
          if (!cancelled) setPreview(result);
        })
        .catch((error) => {
          if (!cancelled) {
            toast.error("Failed to load plan change preview");
            console.error("Preview error:", error);
            onOpenChange(false);
          }
        })
        .finally(() => {
          if (!cancelled) setIsLoading(false);
        });
      return () => {
        cancelled = true;
      };
    } else {
      // Reset state when dialog closes
      setPreview(null);
    }
  }, [open, organizationId, targetPlan]);

  const handleConfirmDowngrade = async () => {
    setIsConfirming(true);
    try {
      const result = await updateMutation.mutateAsync({
        organizationId,
        data: { targetPlan },
      });

      if (result.scheduledFor) {
        toast.success(
          `Your plan will change to ${planLabels[targetPlan]} on ${result.scheduledFor.toLocaleDateString()}`,
        );

        // Refetch subscription data
        await queryClient.refetchQueries({
          queryKey: ["organizations", organizationId, "subscription"],
        });

        onOpenChange(false);
      } else {
        toast.error("Unexpected response: missing scheduled date");
        console.error("Downgrade result missing scheduledFor:", result);
      }
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (error: any) {
      // Handle PlanLimitExceededError with detailed message
      // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
      if (error?.status === 402 && error?.limitType) {
        toast.error(
          // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
          `Cannot downgrade: Current ${error.limitType} usage (${error.currentUsage}) exceeds ${targetPlan} plan limit (${error.limit})`,
          { duration: 5000 },
        );
      } else {
        toast.error("Failed to schedule plan change");
      }
      console.error("Downgrade error:", error);
    } finally {
      setIsConfirming(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-amber-600" />
            Switch to {planLabels[targetPlan]}
          </DialogTitle>
          <DialogDescription>
            {isLoading
              ? "Checking your current usage..."
              : preview?.canDowngrade === false
                ? "Your current usage exceeds plan limits"
                : "Your plan change will take effect at the end of your billing period"}
          </DialogDescription>
        </DialogHeader>

        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : preview?.canDowngrade === false ? (
          <DowngradeBlockedContent
            validationErrors={preview.validationErrors || []}
            targetPlan={targetPlan}
          />
        ) : (
          <DowngradeAllowedContent
            targetPlan={targetPlan}
            currentPlan={currentPlan}
            periodEnd={periodEnd}
            featuresLost={featuresLost}
            validationErrors={preview?.validationErrors}
          />
        )}

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isConfirming}
          >
            Cancel
          </Button>
          <Button
            type="button"
            variant="destructive"
            onClick={() => void handleConfirmDowngrade()}
            disabled={
              isConfirming || isLoading || preview?.canDowngrade === false
            }
          >
            {isConfirming ? "Scheduling..." : "Confirm Change"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
