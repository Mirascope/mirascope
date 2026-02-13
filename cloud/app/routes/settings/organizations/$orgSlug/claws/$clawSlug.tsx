import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { ExternalLink, Loader2, Trash2 } from "lucide-react";
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

function ClawSettingsPage() {
  const { orgSlug, clawSlug } = Route.useParams();
  const navigate = useNavigate();
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

  const claw = claws.find((c) => c.slug === clawSlug);

  // Sync URL claw to context
  useEffect(() => {
    if (claw && selectedClaw?.id !== claw.id) {
      setSelectedClaw(claw);
    }
  }, [claw, selectedClaw?.id, setSelectedClaw]);

  useEffect(() => {
    if (claw?.weeklySpendingGuardrailCenticents != null) {
      setUseBeyondPlan(true);
      setWeeklySpendingLimit(
        centicentsToDollars(claw.weeklySpendingGuardrailCenticents).toString(),
      );
    } else {
      setUseBeyondPlan(false);
      setWeeklySpendingLimit("");
    }
    setSpendingError(null);
  }, [claw?.id, claw?.weeklySpendingGuardrailCenticents]);

  const orgRole = selectedOrganization?.role;
  const canManageMembers = orgRole === "OWNER" || orgRole === "ADMIN";

  const planTier = subscription?.currentPlan ?? "free";
  const limits = PLAN_LIMITS[planTier];

  const handleClawChange = (value: string) => {
    if (value === "__create_new__") {
      setShowCreateModal(true);
    } else {
      const target = claws.find((c) => c.id === value);
      if (target) {
        void navigate({
          to: "/settings/organizations/$orgSlug/claws/$clawSlug",
          params: { orgSlug, clawSlug: target.slug },
        });
      }
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
        <Select value={claw?.id || ""} onValueChange={handleClawChange}>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Select claw" />
          </SelectTrigger>
          <SelectContent>
            {claws.map((c) => (
              <SelectItem key={c.id} value={c.id}>
                {c.displayName ?? c.slug}
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
          onCreated={(c) => {
            void navigate({
              to: "/settings/organizations/$orgSlug/claws/$clawSlug",
              params: { orgSlug, clawSlug: c.slug },
            });
          }}
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
          onCreated={(c) => {
            void navigate({
              to: "/settings/organizations/$orgSlug/claws/$clawSlug",
              params: { orgSlug, clawSlug: c.slug },
            });
          }}
        />
      </div>
    );
  }

  if (!claw) {
    return (
      <div className="max-w-2xl">
        {header}
        <div className="flex justify-center pt-12">
          <div className="text-muted-foreground">
            Claw not found: {clawSlug}
          </div>
        </div>
        <CreateClawModal
          open={showCreateModal}
          onOpenChange={setShowCreateModal}
          onCreated={(c) => {
            void navigate({
              to: "/settings/organizations/$orgSlug/claws/$clawSlug",
              params: { orgSlug, clawSlug: c.slug },
            });
          }}
        />
      </div>
    );
  }

  return (
    <div className="max-w-3xl space-y-6">
      {header}

      {/* Plan usage summary + Dashboard link */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Plan: {planTier.charAt(0).toUpperCase() + planTier.slice(1)} (
          {claws.length}/{limits.claws} claws used)
        </p>
        <Button asChild variant="outline" size="sm">
          <a
            href={(() => {
              if (typeof window === "undefined")
                return `https://openclaw.mirascope.com/${orgSlug}/${clawSlug}/overview`;
              const hostname = window.location.hostname;
              const match = hostname.match(/^([\w-]+)\.(mirascope\.com)$/);
              const base =
                match && match[1] !== "www"
                  ? `openclaw.${match[1]}.${match[2]}`
                  : "openclaw.mirascope.com";
              return `https://${base}/${orgSlug}/${clawSlug}/overview`;
            })()}
            target="_blank"
            rel="noopener noreferrer"
          >
            Open Dashboard
            <ExternalLink className="ml-2 h-4 w-4" />
          </a>
        </Button>
      </div>

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
              value={claw.displayName ?? ""}
              readOnly
              className="bg-muted"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="claw-slug">Slug</Label>
            <Input
              id="claw-slug"
              value={claw.slug}
              readOnly
              className="bg-muted"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="claw-status">Status</Label>
            <Input
              id="claw-status"
              value={STATUS_LABELS[claw.status] ?? claw.status}
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
                    if (!selectedOrganization || !claw) return;
                    const dollars = parseFloat(weeklySpendingLimit);
                    if (isNaN(dollars) || dollars <= 0) {
                      setSpendingError("Enter a valid dollar amount");
                      return;
                    }
                    setSpendingError(null);
                    updateClaw.mutate(
                      {
                        organizationId: selectedOrganization.id,
                        clawId: claw.id,
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
          {!useBeyondPlan && claw.weeklySpendingGuardrailCenticents != null && (
            <Button
              type="button"
              variant="outline"
              disabled={updateClaw.isPending}
              onClick={() => {
                if (!selectedOrganization || !claw) return;
                setSpendingError(null);
                updateClaw.mutate(
                  {
                    organizationId: selectedOrganization.id,
                    clawId: claw.id,
                    updates: {
                      weeklySpendingGuardrailCenticents: null,
                    },
                  },
                  {
                    onError: (err) =>
                      setSpendingError(getErrorMessage(err, "Failed to save")),
                  },
                );
              }}
            >
              {updateClaw.isPending
                ? "Saving..."
                : "Disable beyond-plan spending"}
            </Button>
          )}
          {!useBeyondPlan && claw.weeklySpendingGuardrailCenticents == null && (
            <p className="text-xs text-muted-foreground">
              When disabled, this claw will stop when the included plan credits
              are exhausted.
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
        clawId={claw.id}
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
        onCreated={(c) => {
          void navigate({
            to: "/settings/organizations/$orgSlug/claws/$clawSlug",
            params: { orgSlug, clawSlug: c.slug },
          });
        }}
      />
      <DeleteClawModal
        open={showDeleteModal}
        onOpenChange={setShowDeleteModal}
        claw={claw}
        onDeleted={() => {
          void navigate({
            to: "/settings/organizations/$orgSlug/claws",
            params: { orgSlug },
          });
        }}
      />
    </div>
  );
}

export const Route = createFileRoute(
  "/settings/organizations/$orgSlug/claws/$clawSlug",
)({
  component: ClawSettingsPage,
});
