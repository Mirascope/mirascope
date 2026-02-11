import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { toast } from "sonner";

import type { PlanTier } from "@/payments/plans";

import {
  useSubscription,
  useCancelScheduledDowngrade,
} from "@/app/api/organizations";
import { DowngradePlanDialog } from "@/app/components/downgrade-plan-dialog";
import { PlanSettings } from "@/app/components/plan-settings";
import { RouterCreditsSettings } from "@/app/components/router-credits-settings";
import { SavedPaymentMethod } from "@/app/components/saved-payment-method";
import { UpgradePlanDialog } from "@/app/components/upgrade-plan-dialog";
import { useAnalytics } from "@/app/contexts/analytics";
import { useOrganization } from "@/app/contexts/organization";

function BillingSettingsPage() {
  const { selectedOrganization } = useOrganization();
  const analytics = useAnalytics();

  const [upgradeDialogOpen, setUpgradeDialogOpen] = useState(false);
  const [upgradePlan, setUpgradePlan] = useState<PlanTier | null>(null);
  const [downgradeDialogOpen, setDowngradeDialogOpen] = useState(false);
  const [downgradePlan, setDowngradePlan] = useState<PlanTier | null>(null);

  const orgRole = selectedOrganization?.role;
  const canManageBilling = orgRole === "OWNER" || orgRole === "ADMIN";

  const { data: subscription } = useSubscription(selectedOrganization?.id);
  const cancelDowngradeMutation = useCancelScheduledDowngrade();

  const header = (
    <div className="mb-6">
      <h1 className="text-2xl font-semibold">Billing</h1>
      <p className="text-muted-foreground mt-1">
        Manage your subscription plan and router credits
      </p>
    </div>
  );

  if (!selectedOrganization) {
    return (
      <div className="max-w-4xl">
        {header}
        <div className="flex justify-center pt-12">
          <div className="text-muted-foreground">
            Please select an organization first
          </div>
        </div>
      </div>
    );
  }

  if (!canManageBilling) {
    return (
      <div className="max-w-4xl">
        {header}
        <div className="flex justify-center pt-12">
          <div className="text-muted-foreground">
            You don't have permission to manage billing. Contact your
            organization owner or admin.
          </div>
        </div>
      </div>
    );
  }

  const handleUpgrade = (plan: PlanTier) => {
    setUpgradePlan(plan);
    setUpgradeDialogOpen(true);
  };

  const handleDowngrade = (plan: PlanTier) => {
    setDowngradePlan(plan);
    setDowngradeDialogOpen(true);
  };

  const handleCancelDowngrade = () => {
    cancelDowngradeMutation.mutate(selectedOrganization.id, {
      onSuccess: () => {
        analytics.trackEvent("plan_downgrade_cancelled", {
          organization_id: selectedOrganization.id,
        });
        toast.success("Scheduled plan change cancelled");
      },
      onError: () => {
        toast.error("Failed to cancel scheduled change");
      },
    });
  };

  return (
    <div className="max-w-4xl space-y-6">
      {header}

      <PlanSettings
        organizationId={selectedOrganization.id}
        onUpgrade={handleUpgrade}
        onDowngrade={handleDowngrade}
        onCancelDowngrade={handleCancelDowngrade}
      />

      <SavedPaymentMethod organizationId={selectedOrganization.id} />

      <RouterCreditsSettings organizationId={selectedOrganization.id} />

      {/* Upgrade Dialog */}
      {upgradePlan && (
        <UpgradePlanDialog
          organizationId={selectedOrganization.id}
          targetPlan={upgradePlan}
          open={upgradeDialogOpen}
          onOpenChange={(open) => {
            setUpgradeDialogOpen(open);
            if (!open) setUpgradePlan(null);
          }}
        />
      )}

      {/* Downgrade Dialog */}
      {downgradePlan && subscription && (
        <DowngradePlanDialog
          organizationId={selectedOrganization.id}
          currentPlan={subscription.currentPlan}
          targetPlan={downgradePlan}
          periodEnd={subscription.currentPeriodEnd}
          open={downgradeDialogOpen}
          onOpenChange={(open) => {
            setDowngradeDialogOpen(open);
            if (!open) setDowngradePlan(null);
          }}
        />
      )}
    </div>
  );
}

export const Route = createFileRoute("/$orgSlug/settings/billing")({
  component: BillingSettingsPage,
});
