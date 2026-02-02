import { useQueryClient } from "@tanstack/react-query";
import { AlertTriangle } from "lucide-react";
import { useState, type FormEvent } from "react";

import type { PublicProject } from "@/db/schema";

import { useDeleteProject } from "@/app/api/projects";
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
import { useProject } from "@/app/contexts/project";
import { getErrorMessage } from "@/app/lib/errors";

export function DeleteProjectModal({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [confirmName, setConfirmName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const queryClient = useQueryClient();
  const deleteProject = useDeleteProject();
  const { selectedOrganization } = useOrganization();
  const { selectedProject, setSelectedProject } = useProject();
  const analytics = useAnalytics();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!selectedProject) {
      setError("No project selected");
      return;
    }

    if (!selectedOrganization) {
      setError("No organization selected");
      return;
    }

    if (confirmName !== selectedProject.name) {
      setError("Project name does not match");
      return;
    }

    try {
      await deleteProject.mutateAsync({
        organizationId: selectedOrganization.id,
        projectId: selectedProject.id,
      });
      analytics.trackEvent("project_deleted", {
        project_id: selectedProject.id,
        organization_id: selectedOrganization.id,
      });

      // Wait for the projects query to refetch and get fresh data
      await queryClient.invalidateQueries({
        queryKey: ["projects", selectedOrganization.id],
      });
      const freshProjects =
        queryClient.getQueryData<readonly PublicProject[]>([
          "projects",
          selectedOrganization.id,
        ]) ?? [];

      // Select another project after deletion
      if (freshProjects.length > 0) {
        setSelectedProject(freshProjects[0]);
      } else {
        setSelectedProject(null);
      }

      setConfirmName("");
      onOpenChange(false);
    } catch (err: unknown) {
      setError(getErrorMessage(err, "Failed to delete project"));
    }
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      setConfirmName("");
      setError(null);
    }
    onOpenChange(newOpen);
  };

  if (!selectedProject) {
    return null;
  }

  const isNameMatch = confirmName === selectedProject.name;

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent>
        <form onSubmit={(e) => void handleSubmit(e)}>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-destructive">
              <AlertTriangle className="h-5 w-5" />
              Delete Project
            </DialogTitle>
            <DialogDescription>
              This action cannot be undone. This will permanently delete the
              project <strong>{selectedProject.name}</strong> and all of its
              data.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 mb-4">
              <p className="text-sm text-destructive">
                All prompts, generations, and associated data will be
                permanently deleted.
              </p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirm-name">
                Type <strong>{selectedProject.name}</strong> to confirm
              </Label>
              <Input
                id="confirm-name"
                value={confirmName}
                onChange={(e) => setConfirmName(e.target.value)}
                placeholder="Enter project name"
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
              disabled={!isNameMatch || deleteProject.isPending}
            >
              {deleteProject.isPending ? "Deleting..." : "Delete Project"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
