import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Protected } from "@/app/components/protected";
import { DashboardLayout } from "@/app/components/dashboard-layout";
import { useOrganization } from "@/app/contexts/organization";
import { useProject } from "@/app/contexts/project";
import { useEnvironment } from "@/app/contexts/environment";
import {
  useApiKeys,
  useCreateApiKey,
  useDeleteApiKey,
} from "@/app/api/api-keys";
import { Button } from "@/app/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/app/components/ui/card";

export const Route = createFileRoute("/dashboard/settings")({
  component: SettingsPage,
});

function SettingsPage() {
  const { selectedOrganization } = useOrganization();
  const { selectedProject } = useProject();
  const { selectedEnvironment } = useEnvironment();

  return (
    <Protected>
      <DashboardLayout>
        <div className="p-6 max-w-4xl">
          <h1 className="text-2xl font-semibold mb-6">Settings</h1>

          <div className="space-y-6">
            <ApiKeysSection
              organizationId={selectedOrganization?.id ?? null}
              projectId={selectedProject?.id ?? null}
              environmentId={selectedEnvironment?.id ?? null}
            />
          </div>
        </div>
      </DashboardLayout>
    </Protected>
  );
}

function ApiKeysSection({
  organizationId,
  projectId,
  environmentId,
}: {
  organizationId: string | null;
  projectId: string | null;
  environmentId: string | null;
}) {
  const [newKeyName, setNewKeyName] = useState("");
  const [createdKey, setCreatedKey] = useState<string | null>(null);

  const { data: apiKeys, isLoading } = useApiKeys(
    organizationId,
    projectId,
    environmentId,
  );
  const createApiKey = useCreateApiKey();
  const deleteApiKey = useDeleteApiKey();

  const handleCreate = async () => {
    if (!organizationId || !projectId || !environmentId || !newKeyName.trim()) {
      return;
    }

    const result = await createApiKey.mutateAsync({
      organizationId,
      projectId,
      environmentId,
      data: { name: newKeyName.trim() },
    });

    setCreatedKey(result.key);
    setNewKeyName("");
  };

  const handleDelete = async (apiKeyId: string) => {
    if (!organizationId || !projectId || !environmentId) return;

    if (!window.confirm("Are you sure you want to delete this API key?")) {
      return;
    }

    await deleteApiKey.mutateAsync({
      organizationId,
      projectId,
      environmentId,
      apiKeyId,
    });
  };

  const copyToClipboard = (text: string) => {
    void navigator.clipboard.writeText(text);
  };

  if (!organizationId || !projectId || !environmentId) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>API Keys</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Select an organization, project, and environment to manage API keys.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>API Keys</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Create new API key */}
        <div className="flex gap-2">
          <input
            type="text"
            value={newKeyName}
            onChange={(e) => setNewKeyName(e.target.value)}
            placeholder="API key name"
            className="flex-1 px-3 py-2 border rounded-md bg-background"
          />
          <Button
            onClick={() => void handleCreate()}
            disabled={!newKeyName.trim() || createApiKey.isPending}
          >
            {createApiKey.isPending ? "Creating..." : "Create Key"}
          </Button>
        </div>

        {/* Show newly created key */}
        {createdKey && (
          <div className="p-4 bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800 rounded-md">
            <p className="text-sm font-medium text-green-800 dark:text-green-200 mb-2">
              API key created! Copy it now — you won't be able to see it again.
            </p>
            <div className="flex items-center gap-2">
              <code className="flex-1 p-2 bg-background rounded text-sm font-mono break-all">
                {createdKey}
              </code>
              <Button
                variant="outline"
                size="sm"
                onClick={() => copyToClipboard(createdKey)}
              >
                Copy
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setCreatedKey(null)}
              >
                Dismiss
              </Button>
            </div>
          </div>
        )}

        {/* List existing keys */}
        {isLoading ? (
          <p className="text-muted-foreground">Loading API keys...</p>
        ) : apiKeys && apiKeys.length > 0 ? (
          <div className="space-y-2">
            {apiKeys.map((key) => (
              <div
                key={key.id}
                className="flex items-center justify-between p-3 border rounded-md"
              >
                <div>
                  <p className="font-medium">{key.name}</p>
                  <p className="text-sm text-muted-foreground font-mono">
                    {key.keyPrefix}
                  </p>
                </div>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => void handleDelete(key.id)}
                  disabled={deleteApiKey.isPending}
                >
                  Delete
                </Button>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground">
            No API keys yet. Create one to get started.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
