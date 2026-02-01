import { useQueryClient } from "@tanstack/react-query";
import { AlertTriangle } from "lucide-react";
import { useState, type FormEvent } from "react";

import type { PublicOrganizationWithMembership } from "@/db/schema";

import { useDeleteOrganization } from "@/app/api/organizations";
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
import { useOrganization } from "@/app/contexts/organization";
import { getErrorMessage } from "@/app/lib/errors";

export function DeleteOrganizationModal({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [confirmName, setConfirmName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const queryClient = useQueryClient();
  const deleteOrganization = useDeleteOrganization();
  const { selectedOrganization, setSelectedOrganization } = useOrganization();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!selectedOrganization) {
      setError("No organization selected");
      return;
    }

    if (confirmName !== selectedOrganization.name) {
      setError("Organization name does not match");
      return;
    }

    try {
      await deleteOrganization.mutateAsync(selectedOrganization.id);

      // Wait for the organizations query to refetch and get fresh data
      await queryClient.invalidateQueries({ queryKey: ["organizations"] });
      const freshOrgs =
        queryClient.getQueryData<readonly PublicOrganizationWithMembership[]>([
          "organizations",
        ]) ?? [];

      // Select another organization after deletion
      if (freshOrgs.length > 0) {
        setSelectedOrganization(freshOrgs[0]);
      } else {
        setSelectedOrganization(null);
      }

      setConfirmName("");
      onOpenChange(false);
    } catch (err: unknown) {
      setError(getErrorMessage(err, "Failed to delete organization"));
    }
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      setConfirmName("");
      setError(null);
    }
    onOpenChange(newOpen);
  };

  if (!selectedOrganization) {
    return null;
  }

  const isNameMatch = confirmName === selectedOrganization.name;

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent>
        <form onSubmit={(e) => void handleSubmit(e)}>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-destructive">
              <AlertTriangle className="h-5 w-5" />
              Delete Organization
            </DialogTitle>
            <DialogDescription>
              This action cannot be undone. This will permanently delete the
              organization <strong>{selectedOrganization.name}</strong> and all
              of its data.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 mb-4">
              <p className="text-sm text-destructive">
                All projects, prompts, and associated data will be permanently
                deleted.
              </p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirm-name">
                Type <strong>{selectedOrganization.name}</strong> to confirm
              </Label>
              <Input
                id="confirm-name"
                value={confirmName}
                onChange={(e) => setConfirmName(e.target.value)}
                placeholder="Enter organization name"
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
              disabled={!isNameMatch || deleteOrganization.isPending}
            >
              {deleteOrganization.isPending
                ? "Deleting..."
                : "Delete Organization"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
