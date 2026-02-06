import { useQueryClient } from "@tanstack/react-query";
import { AlertTriangle } from "lucide-react";
import { useState, type FormEvent } from "react";

import type { Claw } from "@/api/claws.schemas";

import { useDeleteClaw } from "@/app/api/claws";
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
import { useClaw } from "@/app/contexts/claw";
import { useOrganization } from "@/app/contexts/organization";
import { getErrorMessage } from "@/app/lib/errors";

export function DeleteClawModal({
  open,
  onOpenChange,
  claw,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  claw: Claw;
}) {
  const [confirmName, setConfirmName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const queryClient = useQueryClient();
  const deleteClaw = useDeleteClaw();
  const { selectedOrganization } = useOrganization();
  const { setSelectedClaw } = useClaw();
  const analytics = useAnalytics();

  const clawDisplayName = claw.displayName || claw.slug;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!selectedOrganization) {
      setError("No organization selected");
      return;
    }

    if (confirmName !== clawDisplayName) {
      setError("Name does not match");
      return;
    }

    try {
      await deleteClaw.mutateAsync({
        organizationId: selectedOrganization.id,
        clawId: claw.id,
      });
      analytics.trackEvent("claw_deleted", {
        claw_id: claw.id,
        organization_id: selectedOrganization.id,
      });

      await queryClient.invalidateQueries({
        queryKey: ["claws", selectedOrganization.id],
      });
      const freshClaws =
        queryClient.getQueryData<readonly Claw[]>([
          "claws",
          selectedOrganization.id,
        ]) ?? [];

      if (freshClaws.length > 0) {
        setSelectedClaw(freshClaws[0]);
      } else {
        setSelectedClaw(null);
      }

      setConfirmName("");
      onOpenChange(false);
    } catch (err: unknown) {
      setError(getErrorMessage(err, "Failed to delete claw"));
    }
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      setConfirmName("");
      setError(null);
    }
    onOpenChange(newOpen);
  };

  const isNameMatch = confirmName === clawDisplayName;

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent>
        <form onSubmit={(e) => void handleSubmit(e)}>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-destructive">
              <AlertTriangle className="h-5 w-5" />
              Delete Claw
            </DialogTitle>
            <DialogDescription>
              This action cannot be undone. This will permanently delete the
              claw <strong>{clawDisplayName}</strong> and all of its data.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 mb-4">
              <p className="text-sm text-destructive">
                All claw configuration, memberships, and associated data will be
                permanently deleted.
              </p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirm-name">
                Type <strong>{clawDisplayName}</strong> to confirm
              </Label>
              <Input
                id="confirm-name"
                value={confirmName}
                onChange={(e) => setConfirmName(e.target.value)}
                placeholder="Enter claw name"
                autoFocus
              />
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
              variant="destructive"
              disabled={!isNameMatch || deleteClaw.isPending}
            >
              {deleteClaw.isPending ? "Deleting..." : "Delete Claw"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
