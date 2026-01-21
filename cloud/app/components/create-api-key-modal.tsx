import { useState, type FormEvent } from "react";
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
import { Alert, AlertDescription } from "@/app/components/ui/alert";
import { Loader2, AlertTriangle, Copy, Check } from "lucide-react";
import { useProjects } from "@/app/api/projects";
import { useEnvironments } from "@/app/api/environments";
import { useCreateApiKey } from "@/app/api/api-keys";
import { getErrorMessage } from "@/app/lib/errors";

interface CreateApiKeyModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  organizationId: string;
}

export function CreateApiKeyModal({
  open,
  onOpenChange,
  organizationId,
}: CreateApiKeyModalProps) {
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [selectedEnvironmentId, setSelectedEnvironmentId] =
    useState<string>("");
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [createdKey, setCreatedKey] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const { data: projects, isLoading: loadingProjects } =
    useProjects(organizationId);
  const { data: environments, isLoading: loadingEnvironments } =
    useEnvironments(organizationId, selectedProjectId || null);
  const createApiKey = useCreateApiKey();

  const handleProjectChange = (projectId: string) => {
    setSelectedProjectId(projectId);
    setSelectedEnvironmentId(""); // Reset environment when project changes
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!selectedProjectId) {
      setError("Please select a project");
      return;
    }

    if (!selectedEnvironmentId) {
      setError("Please select an environment");
      return;
    }

    if (!name.trim()) {
      setError("API key name is required");
      return;
    }

    try {
      const result = await createApiKey.mutateAsync({
        organizationId,
        projectId: selectedProjectId,
        environmentId: selectedEnvironmentId,
        data: { name: name.trim() },
      });

      // Show the created key
      setCreatedKey(result.key);
    } catch (err: unknown) {
      setError(getErrorMessage(err, "Failed to create API key"));
    }
  };

  const copyToClipboard = async () => {
    if (!createdKey) return;
    await navigator.clipboard.writeText(createdKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleClose = () => {
    // Reset form state
    setSelectedProjectId("");
    setSelectedEnvironmentId("");
    setName("");
    setError(null);
    setCreatedKey(null);
    setCopied(false);
    onOpenChange(false);
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      handleClose();
    } else {
      onOpenChange(newOpen);
    }
  };

  // If key was created, show success state
  if (createdKey) {
    return (
      <Dialog open={open} onOpenChange={handleOpenChange}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>API Key Created</DialogTitle>
            <DialogDescription>
              Your API key has been created successfully.
            </DialogDescription>
          </DialogHeader>

          <div className="py-4">
            <Alert className="bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800">
              <AlertTriangle className="h-4 w-4 text-green-600 dark:text-green-400" />
              <AlertDescription className="text-green-800 dark:text-green-200">
                <p className="font-medium mb-2">
                  Copy this key now. You won't be able to see it again!
                </p>
                <div className="flex items-center gap-2 mt-3">
                  <code className="flex-1 p-2 bg-background rounded text-sm font-mono break-all border">
                    {createdKey}
                  </code>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => void copyToClipboard()}
                    className="shrink-0"
                  >
                    {copied ? (
                      <>
                        <Check className="h-4 w-4 mr-1" />
                        Copied
                      </>
                    ) : (
                      <>
                        <Copy className="h-4 w-4 mr-1" />
                        Copy
                      </>
                    )}
                  </Button>
                </div>
              </AlertDescription>
            </Alert>
          </div>

          <DialogFooter>
            <Button onClick={handleClose}>Done</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <form onSubmit={(e) => void handleSubmit(e)}>
          <DialogHeader>
            <DialogTitle>Create API Key</DialogTitle>
            <DialogDescription>
              Create a new API key to authenticate requests to the Mirascope
              API.
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            {error && (
              <Alert variant="destructive">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="grid gap-2">
              <Label htmlFor="project">Project</Label>
              {loadingProjects ? (
                <div className="flex items-center justify-center py-4">
                  <Loader2 className="h-4 w-4 animate-spin" />
                </div>
              ) : (projects ?? []).length === 0 ? (
                <p className="text-sm text-muted-foreground py-2">
                  No projects in this organization
                </p>
              ) : (
                <Select
                  value={selectedProjectId}
                  onValueChange={handleProjectChange}
                >
                  <SelectTrigger id="project">
                    <SelectValue placeholder="Select a project" />
                  </SelectTrigger>
                  <SelectContent>
                    {(projects ?? []).map((project) => (
                      <SelectItem key={project.id} value={project.id}>
                        {project.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            </div>

            <div className="grid gap-2">
              <Label htmlFor="environment">Environment</Label>
              {!selectedProjectId ? (
                <p className="text-sm text-muted-foreground py-2">
                  Select a project first
                </p>
              ) : loadingEnvironments ? (
                <div className="flex items-center justify-center py-4">
                  <Loader2 className="h-4 w-4 animate-spin" />
                </div>
              ) : (environments ?? []).length === 0 ? (
                <p className="text-sm text-muted-foreground py-2">
                  No environments in this project
                </p>
              ) : (
                <Select
                  value={selectedEnvironmentId}
                  onValueChange={setSelectedEnvironmentId}
                >
                  <SelectTrigger id="environment">
                    <SelectValue placeholder="Select an environment" />
                  </SelectTrigger>
                  <SelectContent>
                    {(environments ?? []).map((env) => (
                      <SelectItem key={env.id} value={env.id}>
                        {env.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            </div>

            <div className="grid gap-2">
              <Label htmlFor="api-key-name">API Key Name</Label>
              <Input
                id="api-key-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g., Production API Key"
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={createApiKey.isPending}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={
                !selectedProjectId ||
                !selectedEnvironmentId ||
                !name.trim() ||
                createApiKey.isPending
              }
            >
              {createApiKey.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Creating...
                </>
              ) : (
                "Create API Key"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
