import { useQueryClient, useQuery } from "@tanstack/react-query";
import { Effect } from "effect";
import { Loader2 } from "lucide-react";
import { useState, useEffect } from "react";
import { toast } from "sonner";

import type { PlanTier } from "@/payments/plans";

import { ApiClient, eq } from "@/app/api/client";
import { useUpdateSubscription } from "@/app/api/organizations";
import { RouterCreditsPaymentForm } from "@/app/components/router-credits-payment-form";
import { Button } from "@/app/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/app/components/ui/dialog";
import { planLabels } from "@/app/components/ui/plan-badge";
import { useAnalytics } from "@/app/contexts/analytics";

interface UpgradePlanDialogProps {
  organizationId: string;
  targetPlan: PlanTier;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

type Step = "preview" | "payment" | "success";

export function UpgradePlanDialog({
  organizationId,
  targetPlan,
  open,
  onOpenChange,
}: UpgradePlanDialogProps) {
  const [step, setStep] = useState<Step>("preview");
  const [clientSecret, setClientSecret] = useState<string | null>(null);

  const queryClient = useQueryClient();
  const updateMutation = useUpdateSubscription();
  const analytics = useAnalytics();

  // Load preview when dialog opens using useQuery
  const {
    data: previewData,
    isLoading: isLoadingPreview,
    error: previewError,
  } = useQuery({
    ...eq.queryOptions({
      queryKey: ["subscription-preview", organizationId, targetPlan],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.organizations.previewSubscriptionChange({
            path: { id: organizationId },
            payload: { targetPlan },
          });
        }),
    }),
    enabled: open && step === "preview",
    staleTime: 0, // Always fetch fresh pricing
  });

  // Show error toast if preview fails
  useEffect(() => {
    if (previewError && open && step === "preview") {
      toast.error("Failed to load pricing preview");
    }
  }, [previewError, open, step]);

  const handleConfirmUpgrade = async () => {
    try {
      const result = await updateMutation.mutateAsync({
        organizationId,
        data: { targetPlan },
      });

      if (result.requiresPayment && result.clientSecret) {
        // Need to collect payment
        setClientSecret(result.clientSecret);
        setStep("payment");
      } else {
        // Upgrade succeeded immediately
        handleUpgradeSuccess();
      }
    } catch (error) {
      toast.error("Failed to upgrade plan");
      console.error("Upgrade error:", error);
    }
  };

  const handleUpgradeSuccess = () => {
    analytics.trackEvent("plan_upgraded", {
      organization_id: organizationId,
      target_plan: targetPlan,
    });
    setStep("success");

    // Refetch subscription data
    void queryClient.refetchQueries({
      queryKey: ["organizations", organizationId, "subscription"],
    });

    // Close dialog after showing success message
    setTimeout(() => {
      onOpenChange(false);

      // Reset state for next time
      setTimeout(() => {
        setStep("preview");
        setClientSecret(null);
      }, 300);
    }, 2000);
  };

  const handlePaymentError = (error: string) => {
    toast.error(`Payment failed: ${error}`);
  };

  const handleOpenChangeInternal = (newOpen: boolean) => {
    onOpenChange(newOpen);
    if (!newOpen) {
      // Reset state when closing
      setTimeout(() => {
        setStep("preview");
        setClientSecret(null);
      }, 300);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChangeInternal}>
      <DialogContent className="sm:max-w-[500px]">
        {step === "preview" && (
          <>
            <DialogHeader>
              <DialogTitle>Upgrade to {planLabels[targetPlan]}</DialogTitle>
              <DialogDescription>
                Confirm your plan upgrade and payment details
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              {isLoadingPreview ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                </div>
              ) : previewData ? (
                <>
                  <div className="rounded-lg border border-border bg-muted/50 p-4">
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">New Plan:</span>
                        <span className="font-semibold">
                          {planLabels[targetPlan]}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">
                          Prorated Charge Today:
                        </span>
                        <span className="font-semibold">
                          ${previewData.proratedAmountInDollars.toFixed(2)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">
                          Next Billing Date:
                        </span>
                        <span className="font-medium">
                          {previewData.nextBillingDate.toLocaleDateString()}
                        </span>
                      </div>
                      <div className="flex justify-between border-t border-border pt-2">
                        <span className="text-muted-foreground">
                          Recurring Amount:
                        </span>
                        <span className="font-semibold">
                          ${previewData.recurringAmountInDollars.toFixed(2)}
                          /month
                        </span>
                      </div>
                    </div>
                  </div>

                  <p className="text-sm text-muted-foreground">
                    You'll be charged $
                    {previewData.proratedAmountInDollars.toFixed(2)} today for
                    the remainder of your billing period, then $
                    {previewData.recurringAmountInDollars.toFixed(2)} per month.
                  </p>
                </>
              ) : (
                <p className="text-sm text-destructive">
                  Failed to load pricing preview. Please try again.
                </p>
              )}
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                disabled={updateMutation.isPending}
              >
                Cancel
              </Button>
              <Button
                type="button"
                onClick={() => void handleConfirmUpgrade()}
                disabled={
                  !previewData || isLoadingPreview || updateMutation.isPending
                }
              >
                {updateMutation.isPending
                  ? "Processing..."
                  : `Confirm & Pay $${previewData?.proratedAmountInDollars.toFixed(2) || "0.00"}`}
              </Button>
            </DialogFooter>
          </>
        )}

        {step === "payment" && clientSecret && previewData && (
          <>
            <DialogHeader>
              <DialogTitle>Enter Payment Details</DialogTitle>
              <DialogDescription>
                Complete your upgrade to {planLabels[targetPlan]}
              </DialogDescription>
            </DialogHeader>
            <div className="py-4">
              <RouterCreditsPaymentForm
                clientSecret={clientSecret}
                amount={previewData.proratedAmountInDollars}
                onSuccess={handleUpgradeSuccess}
                onError={handlePaymentError}
              />
            </div>
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setStep("preview")}
              >
                Back
              </Button>
            </DialogFooter>
          </>
        )}

        {step === "success" && (
          <>
            <DialogHeader>
              <DialogTitle>Upgrade Successful!</DialogTitle>
              <DialogDescription>
                Your plan has been upgraded to {planLabels[targetPlan]}
              </DialogDescription>
            </DialogHeader>
            <div className="py-6 text-center">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100 dark:bg-green-900">
                <svg
                  className="h-6 w-6 text-green-600 dark:text-green-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <p className="text-lg font-semibold mb-1">
                Welcome to {planLabels[targetPlan]}!
              </p>
              <p className="text-sm text-muted-foreground">
                Your new plan is active immediately
              </p>
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
