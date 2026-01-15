import { createFileRoute, useNavigate } from "@tanstack/react-router";
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
import {
  useProjects,
  useCreateProject,
  useDeleteProject,
} from "@/app/api/projects";
import {
  useEnvironments,
  useCreateEnvironment,
  useDeleteEnvironment,
} from "@/app/api/environments";
import {
  useDeleteOrganization,
  useCancelScheduledDowngrade,
} from "@/app/api/organizations";
import { Button } from "@/app/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/app/components/ui/card";
import { generateSlug } from "@/db/slug";
import { BillingSettings } from "@/app/components/billing-settings";
import { BillingErrorBoundary } from "@/app/components/billing-error-boundary";
import { UpgradePlanDialog } from "@/app/components/upgrade-plan-dialog";
import { DowngradePlanDialog } from "@/app/components/downgrade-plan-dialog";
import { useSubscription } from "@/app/api/organizations";
import type { PlanTier } from "@/payments/subscriptions";
import { OrganizationInvitationsSection } from "@/app/components/organization-invitations-section";

export const Route = createFileRoute("/dashboard/settings")({
  component: SettingsPage,
});

function SettingsContent() {
  const { selectedOrganization } = useOrganization();
  const { selectedProject } = useProject();
  const { selectedEnvironment } = useEnvironment();
  const [upgradeDialogOpen, setUpgradeDialogOpen] = useState(false);
  const [downgradeDialogOpen, setDowngradeDialogOpen] = useState(false);
  const [selectedTargetPlan, setSelectedTargetPlan] = useState<PlanTier | null>(
    null,
  );

  const { data: subscription } = useSubscription(selectedOrganization?.id);
  const cancelDowngradeMutation = useCancelScheduledDowngrade();

  const handleUpgrade = (targetPlan: PlanTier) => {
    setSelectedTargetPlan(targetPlan);
    setUpgradeDialogOpen(true);
  };

  const handleDowngrade = (targetPlan: PlanTier) => {
    setSelectedTargetPlan(targetPlan);
    setDowngradeDialogOpen(true);
  };

  const handleCancelDowngrade = async () => {
    if (!selectedOrganization?.id) return;
    try {
      await cancelDowngradeMutation.mutateAsync(selectedOrganization.id);
    } catch (error) {
      console.error("Failed to cancel downgrade:", error);
    }
  };

  return (
    <div className="p-6 max-w-4xl">
      <h1 className="text-2xl font-semibold mb-6">Settings</h1>

      <div className="space-y-6">
        <ProjectsSection organizationId={selectedOrganization?.id ?? null} />

        <EnvironmentsSection
          organizationId={selectedOrganization?.id ?? null}
          projectId={selectedProject?.id ?? null}
        />

        <ApiKeysSection
          organizationId={selectedOrganization?.id ?? null}
          projectId={selectedProject?.id ?? null}
          environmentId={selectedEnvironment?.id ?? null}
        />

        <OrganizationInvitationsSection
          organizationId={selectedOrganization?.id ?? null}
          userRole={selectedOrganization?.role}
        />

        {selectedOrganization?.id && (
          <BillingErrorBoundary>
            <BillingSettings
              organizationId={selectedOrganization.id}
              onUpgrade={handleUpgrade}
              onDowngrade={handleDowngrade}
              onCancelDowngrade={() => void handleCancelDowngrade()}
            />
          </BillingErrorBoundary>
        )}

        <OrganizationSection
          organizationId={selectedOrganization?.id ?? null}
        />
      </div>

      {selectedOrganization?.id && selectedTargetPlan && (
        <>
          <UpgradePlanDialog
            organizationId={selectedOrganization.id}
            targetPlan={selectedTargetPlan}
            open={upgradeDialogOpen}
            onOpenChange={setUpgradeDialogOpen}
          />
          {subscription && (
            <DowngradePlanDialog
              organizationId={selectedOrganization.id}
              currentPlan={subscription.currentPlan}
              targetPlan={selectedTargetPlan}
              periodEnd={subscription.currentPeriodEnd}
              open={downgradeDialogOpen}
              onOpenChange={setDowngradeDialogOpen}
            />
          )}
        </>
      )}
    </div>
  );
}

function SettingsPage() {
  return (
    <Protected>
      <DashboardLayout>
        <SettingsContent />
      </DashboardLayout>
    </Protected>
  );
}

function OrganizationSection({
  organizationId,
}: {
  organizationId: string | null;
}) {
  const [confirmDelete, setConfirmDelete] = useState("");
  const navigate = useNavigate();
  const { selectedOrganization, setSelectedOrganization } = useOrganization();
  const deleteOrganization = useDeleteOrganization();

  const handleDelete = async () => {
    if (!organizationId || confirmDelete !== selectedOrganization?.name) {
      return;
    }

    await deleteOrganization.mutateAsync(organizationId);
    setSelectedOrganization(null);
    void navigate({ to: "/dashboard" });
  };

  if (!organizationId || !selectedOrganization) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Organization</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Select an organization to manage.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-destructive/50">
      <CardHeader>
        <CardTitle>Danger Zone</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="p-4 border border-destructive/50 rounded-md">
          <h3 className="font-medium text-destructive mb-2">
            Delete Organization
          </h3>
          <p className="text-sm text-muted-foreground mb-4">
            This will permanently delete the organization{" "}
            <strong>{selectedOrganization.name}</strong> and all its projects,
            environments, and API keys. This action cannot be undone.
          </p>
          <div className="space-y-2">
            <input
              type="text"
              value={confirmDelete}
              onChange={(e) => setConfirmDelete(e.target.value)}
              placeholder={`Type "${selectedOrganization.name}" to confirm`}
              className="w-full px-3 py-2 border rounded-md bg-background"
            />
            <Button
              variant="destructive"
              onClick={() => void handleDelete()}
              disabled={
                confirmDelete !== selectedOrganization.name ||
                deleteOrganization.isPending
              }
            >
              {deleteOrganization.isPending
                ? "Deleting..."
                : "Delete Organization"}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function ProjectsSection({
  organizationId,
}: {
  organizationId: string | null;
}) {
  const [newProjectName, setNewProjectName] = useState("");
  const { setSelectedProject } = useProject();

  const { data: projects, isLoading } = useProjects(organizationId);
  const createProject = useCreateProject();
  const deleteProject = useDeleteProject();

  const handleCreate = async () => {
    if (!organizationId || !newProjectName.trim()) return;

    await createProject.mutateAsync({
      organizationId,
      name: newProjectName.trim(),
    });
    setNewProjectName("");
  };

  const handleDelete = async (projectId: string, projectName: string) => {
    if (!organizationId) return;

    if (
      !window.confirm(
        `Are you sure you want to delete project "${projectName}"? This will also delete all environments and API keys.`,
      )
    ) {
      return;
    }

    await deleteProject.mutateAsync({ organizationId, projectId });
    setSelectedProject(null);
  };

  if (!organizationId) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Projects</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Select an organization to manage projects.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Projects</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={newProjectName}
            onChange={(e) => setNewProjectName(e.target.value)}
            placeholder="Project name"
            className="flex-1 px-3 py-2 border rounded-md bg-background"
          />
          <Button
            onClick={() => void handleCreate()}
            disabled={!newProjectName.trim() || createProject.isPending}
          >
            {createProject.isPending ? "Creating..." : "Create Project"}
          </Button>
        </div>

        {isLoading ? (
          <p className="text-muted-foreground">Loading projects...</p>
        ) : projects && projects.length > 0 ? (
          <div className="space-y-2">
            {projects.map((project) => (
              <div
                key={project.id}
                className="flex items-center justify-between p-3 border rounded-md"
              >
                <p className="font-medium">{project.name}</p>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => void handleDelete(project.id, project.name)}
                  disabled={deleteProject.isPending}
                >
                  Delete
                </Button>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground">
            No projects yet. Create one to get started.
          </p>
        )}
      </CardContent>
    </Card>
  );
}

function EnvironmentsSection({
  organizationId,
  projectId,
}: {
  organizationId: string | null;
  projectId: string | null;
}) {
  const [newEnvName, setNewEnvName] = useState("");
  const { selectedEnvironment, setSelectedEnvironment } = useEnvironment();

  const { data: environments, isLoading } = useEnvironments(
    organizationId,
    projectId,
  );
  const createEnvironment = useCreateEnvironment();
  const deleteEnvironment = useDeleteEnvironment();

  const handleCreate = async () => {
    if (!organizationId || !projectId || !newEnvName.trim()) return;

    await createEnvironment.mutateAsync({
      organizationId,
      projectId,
      data: { name: newEnvName.trim(), slug: generateSlug(newEnvName.trim()) },
    });
    setNewEnvName("");
  };

  const handleDelete = async (environmentId: string, envName: string) => {
    if (!organizationId || !projectId) return;

    if (
      !window.confirm(
        `Are you sure you want to delete environment "${envName}"? This will also delete all API keys.`,
      )
    ) {
      return;
    }

    await deleteEnvironment.mutateAsync({
      organizationId,
      projectId,
      environmentId,
    });
    if (selectedEnvironment?.id === environmentId) {
      setSelectedEnvironment(null);
    }
  };

  if (!organizationId || !projectId) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Environments</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Select an organization and project to manage environments.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Environments</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={newEnvName}
            onChange={(e) => setNewEnvName(e.target.value)}
            placeholder="Environment name"
            className="flex-1 px-3 py-2 border rounded-md bg-background"
          />
          <Button
            onClick={() => void handleCreate()}
            disabled={!newEnvName.trim() || createEnvironment.isPending}
          >
            {createEnvironment.isPending ? "Creating..." : "Create Environment"}
          </Button>
        </div>

        {isLoading ? (
          <p className="text-muted-foreground">Loading environments...</p>
        ) : environments && environments.length > 0 ? (
          <div className="space-y-2">
            {environments.map((env) => (
              <div
                key={env.id}
                className="flex items-center justify-between p-3 border rounded-md"
              >
                <p className="font-medium">{env.name}</p>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => void handleDelete(env.id, env.name)}
                  disabled={deleteEnvironment.isPending}
                >
                  Delete
                </Button>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground">
            No environments yet. Create one to get started.
          </p>
        )}
      </CardContent>
    </Card>
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
  const [copied, setCopied] = useState(false);

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
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
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
                {copied ? "Copied!" : "Copy"}
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
