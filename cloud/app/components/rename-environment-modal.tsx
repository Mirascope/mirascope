import { useState, useEffect, type FormEvent } from "react";

import type { PublicEnvironment } from "@/db/schema";

import { useUpdateEnvironment } from "@/app/api/environments";
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
import { getErrorMessage } from "@/app/lib/errors";
import { generateSlug } from "@/db/slug";

export function RenameEnvironmentModal({
  open,
  onOpenChange,
  environment,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  environment: PublicEnvironment | null;
}) {
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const updateEnvironment = useUpdateEnvironment();
  const { selectedOrganization } = useOrganization();
  const { selectedProject } = useProject();

  // Reset name when environment changes or modal opens
  useEffect(() => {
    if (environment && open) {
      setName(environment.name);
    }
  }, [environment, open]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError("Environment name is required");
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

    if (!environment) {
      setError("No environment selected");
      return;
    }

    // Don't submit if name hasn't changed
    if (name.trim() === environment.name) {
      onOpenChange(false);
      return;
    }

    try {
      await updateEnvironment.mutateAsync({
        organizationId: selectedOrganization.id,
        projectId: selectedProject.id,
        environmentId: environment.id,
        data: {
          name: name.trim(),
          slug: generateSlug(name.trim()),
        },
      });
      onOpenChange(false);
    } catch (err: unknown) {
      setError(getErrorMessage(err, "Failed to rename environment"));
    }
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      setName("");
      setError(null);
    }
    onOpenChange(newOpen);
  };

  if (!environment) {
    return null;
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent>
        <form onSubmit={(e) => void handleSubmit(e)}>
          <DialogHeader>
            <DialogTitle>Rename Environment</DialogTitle>
            <DialogDescription>
              Change the name of the <strong>{environment.name}</strong>{" "}
              environment.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <div className="space-y-2">
              <Label htmlFor="environment-name">Environment Name</Label>
              <Input
                id="environment-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="production"
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
            <Button type="submit" disabled={updateEnvironment.isPending}>
              {updateEnvironment.isPending ? "Saving..." : "Save"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
