import { useState, type FormEvent } from "react";

import { useCreateEnvironment } from "@/app/api/environments";
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
import { useEnvironment } from "@/app/contexts/environment";
import { useOrganization } from "@/app/contexts/organization";
import { useProject } from "@/app/contexts/project";
import { getErrorMessage } from "@/app/lib/errors";
import { generateSlug } from "@/db/slug";

export function CreateEnvironmentModal({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const createEnvironment = useCreateEnvironment();
  const { selectedOrganization } = useOrganization();
  const { selectedProject } = useProject();
  const { setSelectedEnvironment } = useEnvironment();

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

    try {
      const newEnvironment = await createEnvironment.mutateAsync({
        organizationId: selectedOrganization.id,
        projectId: selectedProject.id,
        data: {
          name: name.trim(),
          slug: generateSlug(name.trim()),
        },
      });
      setSelectedEnvironment(newEnvironment);
      setName("");
      onOpenChange(false);
    } catch (err: unknown) {
      setError(getErrorMessage(err, "Failed to create environment"));
    }
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      setName("");
      setError(null);
    }
    onOpenChange(newOpen);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent>
        <form onSubmit={(e) => void handleSubmit(e)}>
          <DialogHeader>
            <DialogTitle>Create Environment</DialogTitle>
            <DialogDescription>
              Create a new environment for your project (e.g., development,
              staging, production).
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
            <Button type="submit" disabled={createEnvironment.isPending}>
              {createEnvironment.isPending ? "Creating..." : "Create"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
