import { useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { Plus } from "lucide-react";
import { useOrganization } from "@/app/contexts/organization";
import { Button } from "@/app/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";
import { CreateOrganizationModal } from "@/app/components/create-organization-modal";
import { Input } from "@/app/components/ui/input";
import { Label } from "@/app/components/ui/label";

function OrganizationSettingsPage() {
  const { selectedOrganization, organizations, isLoading } = useOrganization();
  const [showCreateModal, setShowCreateModal] = useState(false);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    );
  }

  if (!selectedOrganization) {
    const hasOrganizations = organizations.length > 0;
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4">
        {hasOrganizations && (
          <div className="text-muted-foreground">
            Please select an organization
          </div>
        )}
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Create New Organization
        </Button>
        <CreateOrganizationModal
          open={showCreateModal}
          onOpenChange={setShowCreateModal}
        />
      </div>
    );
  }

  return (
    <div className="max-w-2xl">
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Organization</h1>
          <p className="text-muted-foreground mt-1">
            Manage your organization settings
          </p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="h-4 w-4 mr-2" />
          New Organization
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Organization Details</CardTitle>
          <CardDescription>
            Basic information about your organization
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="org-name">Name</Label>
            <Input
              id="org-name"
              value={selectedOrganization.name}
              readOnly
              className="bg-muted"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="org-slug">Slug</Label>
            <Input
              id="org-slug"
              value={selectedOrganization.slug}
              readOnly
              className="bg-muted"
            />
          </div>
        </CardContent>
      </Card>

      <CreateOrganizationModal
        open={showCreateModal}
        onOpenChange={setShowCreateModal}
      />
    </div>
  );
}

export const Route = createFileRoute("/cloud/settings/organization")({
  component: OrganizationSettingsPage,
});
