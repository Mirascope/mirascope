import { useState } from "react";
import { Button } from "@/app/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/app/components/ui/dialog";
import { useUpdateSubscription } from "@/app/api/organizations";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";
import type { PlanTier } from "@/payments/subscriptions";
import { AlertTriangle } from "lucide-react";
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

export function DowngradePlanDialog({
  organizationId,
  currentPlan,
  targetPlan,
  periodEnd,
  open,
  onOpenChange,
}: DowngradePlanDialogProps) {
  const [isConfirming, setIsConfirming] = useState(false);
  const queryClient = useQueryClient();
  const updateMutation = useUpdateSubscription();

  const featuresLost = featureLossWarnings[currentPlan]?.[targetPlan] || [];

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
    } catch (error) {
      toast.error("Failed to schedule plan change");
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
            Your plan change will take effect at the end of your billing period
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="rounded-lg border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-950 p-4">
            <p className="text-sm font-medium text-amber-900 dark:text-amber-200 mb-2">
              Scheduled Change
            </p>
            <p className="text-sm text-amber-800 dark:text-amber-300">
              Your plan will change to <strong>{planLabels[targetPlan]}</strong>{" "}
              on <strong>{periodEnd.toLocaleDateString()}</strong>. You'll
              continue to have access to {planLabels[currentPlan]} features
              until then.
            </p>
          </div>

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

          <div className="rounded-lg border border-border bg-muted/50 p-4">
            <p className="text-sm text-muted-foreground">
              <strong className="text-foreground">No refunds:</strong> You won't
              be refunded for the remainder of your current billing period.
            </p>
          </div>
        </div>

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
            disabled={isConfirming}
          >
            {isConfirming ? "Scheduling..." : "Confirm Change"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
