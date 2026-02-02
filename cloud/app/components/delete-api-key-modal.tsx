import { AlertTriangle } from "lucide-react";
import { useState, type FormEvent } from "react";

import type { ApiKeyWithContext } from "@/api/api-keys.schemas";

import { useDeleteApiKey } from "@/app/api/api-keys";
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
import { getErrorMessage } from "@/app/lib/errors";

export function DeleteApiKeyModal({
  open,
  onOpenChange,
  apiKey,
  organizationId,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  apiKey: ApiKeyWithContext | null;
  organizationId: string;
}) {
  const [confirmName, setConfirmName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const deleteApiKey = useDeleteApiKey();
  const analytics = useAnalytics();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!apiKey) {
      setError("No API key selected");
      return;
    }

    if (confirmName !== apiKey.name) {
      setError("API key name does not match");
      return;
    }

    try {
      await deleteApiKey.mutateAsync({
        organizationId,
        projectId: apiKey.projectId,
        environmentId: apiKey.environmentId,
        apiKeyId: apiKey.id,
      });
      analytics.trackEvent("api_key_deleted", {
        api_key_id: apiKey.id,
        environment_id: apiKey.environmentId,
        project_id: apiKey.projectId,
        organization_id: organizationId,
      });

      setConfirmName("");
      onOpenChange(false);
    } catch (err: unknown) {
      setError(getErrorMessage(err, "Failed to delete API key"));
    }
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      setConfirmName("");
      setError(null);
    }
    onOpenChange(newOpen);
  };

  if (!apiKey) {
    return null;
  }

  const isNameMatch = confirmName === apiKey.name;

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent>
        <form onSubmit={(e) => void handleSubmit(e)}>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-destructive">
              <AlertTriangle className="h-5 w-5" />
              Delete API Key
            </DialogTitle>
            <DialogDescription>
              This action cannot be undone. This will permanently delete the API
              key <strong>{apiKey.name}</strong>.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 mb-4">
              <p className="text-sm text-destructive">
                Any applications using this API key will no longer be able to
                authenticate.
              </p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirm-name">
                Type <strong>{apiKey.name}</strong> to confirm
              </Label>
              <Input
                id="confirm-name"
                value={confirmName}
                onChange={(e) => setConfirmName(e.target.value)}
                placeholder="Enter API key name"
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
              disabled={!isNameMatch || deleteApiKey.isPending}
            >
              {deleteApiKey.isPending ? "Deleting..." : "Delete API Key"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
