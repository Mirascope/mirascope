import { useState, type FormEvent } from "react";

import type { CreateClawRequest } from "@/api/claws.schemas";
import type { PlanTier } from "@/payments/plans";

import { dollarsToCenticents } from "@/api/router/cost-utils";
import { useCreateClaw } from "@/app/api/claws";
import { useSubscription } from "@/app/api/organizations";
import { useProjects } from "@/app/api/projects";
import { ClawAdvancedOptions } from "@/app/components/claw-advanced-options";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/app/components/ui/select";
import { Textarea } from "@/app/components/ui/textarea";
import { useAnalytics } from "@/app/contexts/analytics";
import { useClaw } from "@/app/contexts/claw";
import { useOrganization } from "@/app/contexts/organization";
import { getErrorMessage } from "@/app/lib/errors";
import { generateSlug } from "@/db/slug";
import { PLAN_LIMITS } from "@/payments/plans";

const DEFAULT_MODEL: Record<PlanTier, CreateClawRequest["model"]> = {
  free: "claude-haiku-4-5",
  pro: "claude-sonnet-4-5",
  team: "claude-sonnet-4-5",
};

export function CreateClawModal({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const { selectedOrganization } = useOrganization();
  const { claws, setSelectedClaw } = useClaw();
  const { data: subscription } = useSubscription(selectedOrganization?.id);
  const { data: projects } = useProjects(selectedOrganization?.id ?? null);
  const createClaw = useCreateClaw();
  const analytics = useAnalytics();

  const planTier: PlanTier = subscription?.currentPlan ?? "free";
  const limits = PLAN_LIMITS[planTier];
  const atLimit = claws.length >= limits.claws;

  const projectCount = projects?.length ?? 0;
  const atProjectLimit = projectCount >= limits.projects;

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [model, setModel] = useState<CreateClawRequest["model"]>(
    DEFAULT_MODEL[planTier],
  );
  const [useBeyondPlan, setUseBeyondPlan] = useState(false);
  const [weeklySpendingLimit, setWeeklySpendingLimit] = useState("");
  const [useExistingProject, setUseExistingProject] = useState(false);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  const slug = generateSlug(name);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError("Name is required");
      return;
    }

    if (!selectedOrganization) {
      setError("No organization selected");
      return;
    }

    if (useExistingProject && !selectedProjectId) {
      setError("Please select a project");
      return;
    }

    try {
      if (useBeyondPlan) {
        const dollars = parseFloat(weeklySpendingLimit);
        if (isNaN(dollars) || dollars <= 0) {
          setError("Please enter a valid weekly spending limit");
          return;
        }
      }

      const dollars = parseFloat(weeklySpendingLimit);
      const weeklySpendingGuardrailCenticents =
        useBeyondPlan && !isNaN(dollars) && dollars > 0
          ? dollarsToCenticents(dollars)
          : null;

      const newClaw = await createClaw.mutateAsync({
        organizationId: selectedOrganization.id,
        name: name.trim(),
        description: description.trim() || undefined,
        model,
        weeklySpendingGuardrailCenticents,
        homeProjectId: useExistingProject ? selectedProjectId : undefined,
      });
      analytics.trackEvent("claw_created", {
        claw_id: newClaw.id,
        organization_id: selectedOrganization.id,
        model,
      });
      setSelectedClaw(newClaw);
      resetForm();
      onOpenChange(false);
    } catch (err: unknown) {
      setError(getErrorMessage(err, "Failed to create claw"));
    }
  };

  const resetForm = () => {
    setName("");
    setDescription("");
    setModel(DEFAULT_MODEL[planTier]);
    setUseBeyondPlan(false);
    setWeeklySpendingLimit("");
    setUseExistingProject(false);
    setSelectedProjectId("");
    setError(null);
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      resetForm();
    }
    onOpenChange(newOpen);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent>
        <form onSubmit={(e) => void handleSubmit(e)}>
          <DialogHeader>
            <DialogTitle>Create a New Claw</DialogTitle>
            <DialogDescription>
              Launch a new AI-powered bot for your organization.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 space-y-4">
            {/* Name */}
            <div className="space-y-2">
              <Label htmlFor="claw-name">Name</Label>
              <Input
                id="claw-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="My Claw"
                autoFocus
                disabled={atLimit}
              />
              {name.trim() && slug && (
                <p className="text-xs text-muted-foreground">
                  Slug: <span className="font-mono">{slug}</span>
                </p>
              )}
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="claw-description">
                Description{" "}
                <span className="text-muted-foreground font-normal">
                  (optional)
                </span>
              </Label>
              <Textarea
                id="claw-description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="What does this claw do?"
                rows={2}
                disabled={atLimit}
              />
            </div>

            {/* Project selection */}
            {!atLimit && (
              <div className="space-y-2">
                <Label>Project</Label>
                {useExistingProject ? (
                  <div className="space-y-2">
                    <Select
                      value={selectedProjectId}
                      onValueChange={setSelectedProjectId}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select a project" />
                      </SelectTrigger>
                      <SelectContent>
                        {(projects ?? []).map((p) => (
                          <SelectItem key={p.id} value={p.id}>
                            {p.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <button
                      type="button"
                      className="text-xs text-muted-foreground hover:text-foreground underline"
                      onClick={() => {
                        setUseExistingProject(false);
                        setSelectedProjectId("");
                      }}
                    >
                      Create a new home project instead
                    </button>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <p className="text-sm text-muted-foreground rounded-md border p-3">
                      Will create a new home project
                      {name.trim() ? (
                        <>
                          :{" "}
                          <span className="font-medium">
                            {name.trim()} Home
                          </span>
                        </>
                      ) : (
                        " for this claw"
                      )}
                    </p>
                    {atProjectLimit && (
                      <p className="text-sm text-destructive">
                        Your plan limit of {limits.projects} project(s) has been
                        reached. Connect to an existing project or delete a
                        project to make room for a new home project.
                      </p>
                    )}
                    {projectCount > 0 && (
                      <button
                        type="button"
                        className="text-xs text-muted-foreground hover:text-foreground underline"
                        onClick={() => setUseExistingProject(true)}
                      >
                        Use an existing project instead
                      </button>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Advanced options */}
            {!atLimit && (
              <ClawAdvancedOptions
                model={model}
                onModelChange={setModel}
                useBeyondPlan={useBeyondPlan}
                onUseBeyondPlanChange={setUseBeyondPlan}
                weeklySpendingLimit={weeklySpendingLimit}
                onWeeklySpendingLimitChange={setWeeklySpendingLimit}
              />
            )}

            {/* Plan usage */}
            <p className="text-xs text-muted-foreground">
              Plan: {planTier.charAt(0).toUpperCase() + planTier.slice(1)} (
              {claws.length}/{limits.claws} claws used)
            </p>

            {atLimit && (
              <p className="text-sm text-destructive">
                You&apos;ve reached the claw limit for your plan. Upgrade to
                create more.
              </p>
            )}

            {error && <p className="text-sm text-destructive">{error}</p>}
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
              disabled={
                createClaw.isPending ||
                atLimit ||
                (atProjectLimit && !useExistingProject)
              }
            >
              {createClaw.isPending ? "Creating..." : "Create Claw"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
