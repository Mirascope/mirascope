import { createFileRoute } from "@tanstack/react-router";
import { useOrganization } from "@/app/contexts/organization";
import { ApiKeysSection } from "@/app/components/api-keys-section";

function ApiKeysSettingsPage() {
  const { selectedOrganization } = useOrganization();

  // Organization OWNER/ADMIN have implicit project ADMIN access to all projects
  const orgRole = selectedOrganization?.role;
  const canManageApiKeys = orgRole === "OWNER" || orgRole === "ADMIN";

  const header = (
    <div className="mb-6">
      <h1 className="text-2xl font-semibold">API Keys</h1>
      <p className="text-muted-foreground mt-1">
        Manage API keys for accessing your projects and environments
      </p>
    </div>
  );

  if (!selectedOrganization) {
    return (
      <div className="max-w-4xl">
        {header}
        <div className="flex justify-center pt-12">
          <div className="text-muted-foreground">
            Please select an organization first
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl space-y-6">
      {header}

      <ApiKeysSection
        organizationId={selectedOrganization.id}
        canManageApiKeys={canManageApiKeys}
      />
    </div>
  );
}

export const Route = createFileRoute("/cloud/settings/api-keys")({
  component: ApiKeysSettingsPage,
});
