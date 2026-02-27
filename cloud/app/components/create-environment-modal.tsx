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
import { useAnalytics } from "@/app/contexts/analytics";
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
  const slug = generateSlug(name.trim());
  const slugTooShort = slug.length > 0 && slug.length < 3;
  const [error, setError] = useState<string | null>(null);
  const createEnvironment = useCreateEnvironment();
  const { selectedOrganization } = useOrganization();
  const { selectedProject } = useProject();
  const { setSelectedEnvironment } = useEnvironment();
  const analytics = useAnalytics();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError("Environment name is required");
      return;
    }

    if (slug.length < 3) {
      setError("Name must generate a slug of at least 3 characters");
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
          slug,
        },
      });
      analytics.trackEvent("environment_created", {
        environment_id: newEnvironment.id,
        project_id: selectedProject.id,
        organization_id: selectedOrganization.id,
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
          <div className="px-6 py-4">
            <div className="space-y-2">
              <Label htmlFor="environment-name">Environment Name</Label>
              <Input
                id="environment-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="production"
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
              disabled={createEnvironment.isPending || slugTooShort}
            >
              {createEnvironment.isPending ? "Creating..." : "Create"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
