import { useState, type FormEvent } from "react";

import type { Organization } from "@/api/organizations.schemas";
import type { PlanTier } from "@/payments/plans";

import { useCreateOrganization } from "@/app/api/organizations";
import { Button } from "@/app/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/app/components/ui/dialog";
import { Input } from "@/app/components/ui/input";
import { Label } from "@/app/components/ui/label";
import { useAnalytics } from "@/app/contexts/analytics";
import { useOrganization } from "@/app/contexts/organization";
import { getErrorMessage } from "@/app/lib/errors";
import { generateSlug } from "@/db/slug";

const PLAN_OPTIONS: { value: PlanTier; label: string; description: string }[] =
  [
    {
      value: "free",
      label: "Free",
      description: "For personal projects",
    },
    {
      value: "pro",
      label: "Pro",
      description: "For professional use",
    },
    {
      value: "team",
      label: "Team",
      description: "For teams and collaboration",
    },
  ];

export function CreateOrganizationModal({
  open,
  onOpenChange,
  onCreated,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreated?: (org: Organization, planTier: PlanTier) => void;
}) {
  const [name, setName] = useState("");
  const slug = generateSlug(name.trim());
  const slugTooShort = slug.length > 0 && slug.length < 3;
  const [error, setError] = useState<string | null>(null);
  const [selectedPlan, setSelectedPlan] = useState<PlanTier>("free");
  const createOrganization = useCreateOrganization();
  const { setSelectedOrganization } = useOrganization();
  const analytics = useAnalytics();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError("Organization name is required");
      return;
    }

    if (slug.length < 3) {
      setError("Name must generate a slug of at least 3 characters");
      return;
    }

    try {
      const newOrg = await createOrganization.mutateAsync({
        name: name.trim(),
        slug,
        planTier: selectedPlan,
      });
      analytics.trackEvent("organization_created", {
        organization_id: newOrg.id,
      });
      setSelectedOrganization(newOrg);
      onCreated?.(newOrg, selectedPlan);
      setName("");
      onOpenChange(false);
    } catch (err: unknown) {
      setError(getErrorMessage(err, "Failed to create organization"));
    }
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      setName("");
      setError(null);
      setSelectedPlan("free");
    }
    onOpenChange(newOpen);
  };

  const availablePlans = PLAN_OPTIONS;

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent>
        <form onSubmit={(e) => void handleSubmit(e)}>
          <DialogHeader>
            <DialogTitle>Create Organization</DialogTitle>
            <DialogDescription>
              Create a new organization to manage your projects and team.
            </DialogDescription>
          </DialogHeader>
          <div className="px-6 py-4">
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="org-name">Organization Name</Label>
                <Input
                  id="org-name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="My Organization"
                  autoFocus
                />
                {name.trim() && slug && (
                  <p className="text-xs text-muted-foreground">
                    Slug: <span className="font-mono">{slug}</span>
                  </p>
                )}
                {slugTooShort && (
                  <p className="text-sm text-destructive">
                    Slug must be at least 3 characters
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <Label>Plan</Label>
                <div className="grid gap-2">
                  {availablePlans.map((plan) => (
                    <button
                      key={plan.value}
                      type="button"
                      onClick={() => setSelectedPlan(plan.value)}
                      className={`flex items-center gap-3 rounded-md border p-3 text-left transition-colors ${
                        selectedPlan === plan.value
                          ? "border-primary bg-primary/5"
                          : "border-border hover:border-primary/50"
                      }`}
                    >
                      <div
                        className={`h-4 w-4 rounded-full border-2 ${
                          selectedPlan === plan.value
                            ? "border-primary bg-primary"
                            : "border-muted-foreground"
                        }`}
                      />
                      <div>
                        <div className="font-medium">{plan.label}</div>
                        <div className="text-xs text-muted-foreground">
                          {plan.description}
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
                {selectedPlan !== "free" && (
                  <p className="text-xs text-muted-foreground">
                    You&apos;ll be redirected to set up billing after creation.
                  </p>
                )}
              </div>
              {error && <p className="text-sm text-destructive">{error}</p>}
            </div>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => handleOpenChange(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={createOrganization.isPending || slugTooShort}
            >
              {createOrganization.isPending ? "Creating..." : "Create"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
