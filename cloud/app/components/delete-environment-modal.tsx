import { useState, type FormEvent } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { AlertTriangle } from "lucide-react";
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
import { useProject } from "@/app/contexts/project";
import { useEnvironment } from "@/app/contexts/environment";
import { useDeleteEnvironment } from "@/app/api/environments";
import { getErrorMessage } from "@/app/lib/errors";
import type { PublicEnvironment } from "@/db/schema";

export function DeleteEnvironmentModal({
  open,
  onOpenChange,
  environment,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  environment: PublicEnvironment | null;
}) {
  const [confirmName, setConfirmName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const queryClient = useQueryClient();
  const deleteEnvironment = useDeleteEnvironment();
  const { selectedOrganization } = useOrganization();
  const { selectedProject } = useProject();
  const { selectedEnvironment, setSelectedEnvironment } = useEnvironment();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!environment) {
      setError("No environment selected");
      return;
    }

    if (!selectedOrganization) {
      setError("No organization selected");
      return;
    }

    if (!selectedProject) {
      setError("No project selected");
      return;
    }

    if (confirmName !== environment.name) {
      setError("Environment name does not match");
      return;
    }

    try {
      await deleteEnvironment.mutateAsync({
        organizationId: selectedOrganization.id,
        projectId: selectedProject.id,
        environmentId: environment.id,
      });

      // Wait for the environments query to refetch and get fresh data
      await queryClient.invalidateQueries({
        queryKey: ["environments", selectedOrganization.id, selectedProject.id],
      });
      const freshEnvironments =
        queryClient.getQueryData<readonly PublicEnvironment[]>([
          "environments",
          selectedOrganization.id,
          selectedProject.id,
        ]) ?? [];

      // Select another environment if we deleted the selected one
      if (selectedEnvironment?.id === environment.id) {
        if (freshEnvironments.length > 0) {
          setSelectedEnvironment(freshEnvironments[0]);
        } else {
          setSelectedEnvironment(null);
        }
      }

      setConfirmName("");
      onOpenChange(false);
    } catch (err: unknown) {
      setError(getErrorMessage(err, "Failed to delete environment"));
    }
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      setConfirmName("");
      setError(null);
    }
    onOpenChange(newOpen);
  };

  if (!environment) {
    return null;
  }

  const isNameMatch = confirmName === environment.name;

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent>
        <form onSubmit={(e) => void handleSubmit(e)}>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-destructive">
              <AlertTriangle className="h-5 w-5" />
              Delete Environment
            </DialogTitle>
            <DialogDescription>
              This action cannot be undone. This will permanently delete the
              environment <strong>{environment.name}</strong> and all of its
              data.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 mb-4">
              <p className="text-sm text-destructive">
                All API keys and associated data will be permanently deleted.
              </p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirm-name">
                Type <strong>{environment.name}</strong> to confirm
              </Label>
              <Input
                id="confirm-name"
                value={confirmName}
                onChange={(e) => setConfirmName(e.target.value)}
                placeholder="Enter environment name"
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
              disabled={!isNameMatch || deleteEnvironment.isPending}
            >
              {deleteEnvironment.isPending
                ? "Deleting..."
                : "Delete Environment"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
