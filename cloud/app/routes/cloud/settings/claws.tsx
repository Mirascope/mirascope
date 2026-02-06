import { createFileRoute } from "@tanstack/react-router";
import { Loader2, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";

import {
  centicentsToDollars,
  dollarsToCenticents,
} from "@/api/router/cost-utils";
import { useUpdateClaw } from "@/app/api/claws";
import { useSubscription } from "@/app/api/organizations";
import { ClawMembersSection } from "@/app/components/claw-members-section";
import { CreateClawModal } from "@/app/components/create-claw-modal";
import { DeleteClawModal } from "@/app/components/delete-claw-modal";
import { Button } from "@/app/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";
import { Input } from "@/app/components/ui/input";
import { Label } from "@/app/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/app/components/ui/select";
import { Switch } from "@/app/components/ui/switch";
import { useAuth } from "@/app/contexts/auth";
import { useClaw } from "@/app/contexts/claw";
import { useOrganization } from "@/app/contexts/organization";
import { getErrorMessage } from "@/app/lib/errors";
import { PLAN_LIMITS } from "@/payments/plans";

const STATUS_LABELS: Record<string, string> = {
  active: "Active",
  pending: "Pending",
  provisioning: "Provisioning",
  error: "Error",
  paused: "Paused",
};

function ClawsSettingsPage() {
  const { selectedOrganization } = useOrganization();
  const { claws, selectedClaw, setSelectedClaw, isLoading } = useClaw();
  const { user } = useAuth();
  const { data: subscription } = useSubscription(selectedOrganization?.id);
  const updateClaw = useUpdateClaw();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const [useBeyondPlan, setUseBeyondPlan] = useState(false);
  const [weeklySpendingLimit, setWeeklySpendingLimit] = useState("");
  const [spendingError, setSpendingError] = useState<string | null>(null);

  useEffect(() => {
    if (selectedClaw?.weeklySpendingGuardrailCenticents != null) {
      setUseBeyondPlan(true);
      setWeeklySpendingLimit(
        centicentsToDollars(
          selectedClaw.weeklySpendingGuardrailCenticents,
        ).toString(),
      );
    } else {
      setUseBeyondPlan(false);
      setWeeklySpendingLimit("");
    }
    setSpendingError(null);
  }, [selectedClaw?.id, selectedClaw?.weeklySpendingGuardrailCenticents]);

  const orgRole = selectedOrganization?.role;
  const canManageMembers = orgRole === "OWNER" || orgRole === "ADMIN";

  const planTier = subscription?.currentPlan ?? "free";
  const limits = PLAN_LIMITS[planTier];

  const handleClawChange = (value: string) => {
    if (value === "__create_new__") {
      setShowCreateModal(true);
    } else {
      const claw = claws.find((c) => c.id === value);
      setSelectedClaw(claw ?? null);
    }
  };

  const header = (
    <div className="mb-6 flex items-start justify-between">
      <div>
        <h1 className="text-2xl font-semibold">Claws</h1>
        <p className="text-muted-foreground mt-1">
          Manage your claw settings and members
        </p>
      </div>
      {selectedOrganization && !isLoading && (
        <Select value={selectedClaw?.id || ""} onValueChange={handleClawChange}>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Select claw" />
          </SelectTrigger>
          <SelectContent>
            {claws.map((claw) => (
              <SelectItem key={claw.id} value={claw.id}>
                {claw.displayName ?? claw.slug}
              </SelectItem>
            ))}
            <SelectItem
              value="__create_new__"
              className="text-primary font-medium"
            >
              + Create New Claw
            </SelectItem>
          </SelectContent>
        </Select>
      )}
    </div>
  );

  if (!selectedOrganization) {
    return (
      <div className="max-w-2xl">
        {header}
        <div className="flex justify-center pt-12">
          <div className="text-muted-foreground">
            Please select an organization first
          </div>
        </div>
        <CreateClawModal
          open={showCreateModal}
          onOpenChange={setShowCreateModal}
        />
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="max-w-2xl">
        {header}
        <div className="flex justify-center pt-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
        <CreateClawModal
          open={showCreateModal}
          onOpenChange={setShowCreateModal}
        />
      </div>
    );
  }

  if (!selectedClaw) {
    return (
      <div className="max-w-2xl">
        {header}
        <div className="flex justify-center pt-12">
          <div className="text-muted-foreground">
            {claws.length === 0
              ? "No claws yet. Create one to get started!"
              : "Please select a claw"}
          </div>
        </div>
        <CreateClawModal
          open={showCreateModal}
          onOpenChange={setShowCreateModal}
        />
      </div>
    );
  }

  return (
    <div className="max-w-3xl space-y-6">
      {header}

      {/* Plan usage summary */}
      <p className="text-sm text-muted-foreground">
        Plan: {planTier.charAt(0).toUpperCase() + planTier.slice(1)} (
        {claws.length}/{limits.claws} claws used)
      </p>

      {/* Claw details */}
      <Card>
        <CardHeader>
          <CardTitle>Claw Details</CardTitle>
          <CardDescription>Basic information about this claw</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="claw-name">Name</Label>
            <Input
              id="claw-name"
              value={selectedClaw.displayName ?? ""}
              readOnly
              className="bg-muted"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="claw-slug">Slug</Label>
            <Input
              id="claw-slug"
              value={selectedClaw.slug}
              readOnly
              className="bg-muted"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="claw-status">Status</Label>
            <Input
              id="claw-status"
              value={STATUS_LABELS[selectedClaw.status] ?? selectedClaw.status}
              readOnly
              className="bg-muted"
            />
          </div>
        </CardContent>
      </Card>

      {/* Spending Controls */}
      <Card>
        <CardHeader>
          <CardTitle>Spending Controls</CardTitle>
          <CardDescription>
            Control beyond-plan router credit usage for this claw
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <Label htmlFor="settings-beyond-plan">
              Use router credits beyond included plan
            </Label>
            <Switch
              id="settings-beyond-plan"
              checked={useBeyondPlan}
              onCheckedChange={setUseBeyondPlan}
            />
          </div>
          {useBeyondPlan && (
            <div className="space-y-2">
              <Label htmlFor="settings-spending-limit">
                Weekly spending limit (dollars)
              </Label>
              <div className="flex items-center gap-2">
                <div className="relative flex-1">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                    $
                  </span>
                  <Input
                    id="settings-spending-limit"
                    type="number"
                    min={0}
                    step="0.01"
                    placeholder="5.00"
                    value={weeklySpendingLimit}
                    onChange={(e) => setWeeklySpendingLimit(e.target.value)}
                    className="pl-7"
                  />
                </div>
                <Button
                  type="button"
                  disabled={updateClaw.isPending}
                  onClick={() => {
                    if (!selectedOrganization || !selectedClaw) return;
                    const dollars = parseFloat(weeklySpendingLimit);
                    if (isNaN(dollars) || dollars <= 0) {
                      setSpendingError("Enter a valid dollar amount");
                      return;
                    }
                    setSpendingError(null);
                    updateClaw.mutate(
                      {
                        organizationId: selectedOrganization.id,
                        clawId: selectedClaw.id,
                        updates: {
                          weeklySpendingGuardrailCenticents:
                            dollarsToCenticents(dollars),
                        },
                      },
                      {
                        onError: (err) =>
                          setSpendingError(
                            getErrorMessage(err, "Failed to save"),
                          ),
                      },
                    );
                  }}
                >
                  {updateClaw.isPending ? "Saving..." : "Save"}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                Allow up to this dollar amount per week from purchased router
                credits when the included plan is exhausted.
              </p>
            </div>
          )}
          {!useBeyondPlan &&
            selectedClaw.weeklySpendingGuardrailCenticents != null && (
              <Button
                type="button"
                variant="outline"
                disabled={updateClaw.isPending}
                onClick={() => {
                  if (!selectedOrganization || !selectedClaw) return;
                  setSpendingError(null);
                  updateClaw.mutate(
                    {
                      organizationId: selectedOrganization.id,
                      clawId: selectedClaw.id,
                      updates: {
                        weeklySpendingGuardrailCenticents: null,
                      },
                    },
                    {
                      onError: (err) =>
                        setSpendingError(
                          getErrorMessage(err, "Failed to save"),
                        ),
                    },
                  );
                }}
              >
                {updateClaw.isPending
                  ? "Saving..."
                  : "Disable beyond-plan spending"}
              </Button>
            )}
          {!useBeyondPlan &&
            selectedClaw.weeklySpendingGuardrailCenticents == null && (
              <p className="text-xs text-muted-foreground">
                When disabled, this claw will stop when the included plan
                credits are exhausted.
              </p>
            )}
          {spendingError && (
            <p className="text-sm text-destructive">{spendingError}</p>
          )}
        </CardContent>
      </Card>

      {/* Members */}
      <ClawMembersSection
        organizationId={selectedOrganization.id}
        clawId={selectedClaw.id}
        currentUserId={user?.id ?? ""}
        canManageMembers={canManageMembers}
      />

      {/* Danger zone */}
      <Card className="border-destructive">
        <CardHeader>
          <CardTitle className="text-destructive">Danger Zone</CardTitle>
          <CardDescription>
            Irreversible and destructive actions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Delete this claw</p>
              <p className="text-sm text-muted-foreground">
                Once you delete a claw, there is no going back. Please be
                certain.
              </p>
            </div>
            <Button
              variant="destructive"
              onClick={() => setShowDeleteModal(true)}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete
            </Button>
          </div>
        </CardContent>
      </Card>

      <CreateClawModal
        open={showCreateModal}
        onOpenChange={setShowCreateModal}
      />
      <DeleteClawModal
        open={showDeleteModal}
        onOpenChange={setShowDeleteModal}
        claw={selectedClaw}
      />
    </div>
  );
}

export const Route = createFileRoute("/cloud/settings/claws")({
  component: ClawsSettingsPage,
});
