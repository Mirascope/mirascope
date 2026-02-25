import { createFileRoute } from "@tanstack/react-router";
import { Loader2, Plus, Trash2 } from "lucide-react";
import { useState } from "react";

import { CreateOrganizationModal } from "@/app/components/create-organization-modal";
import { DeleteOrganizationModal } from "@/app/components/delete-organization-modal";
import { Button } from "@/app/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";
import { Input } from "@/app/components/ui/input";
import { Label } from "@/app/components/ui/label";
import { useOrganization } from "@/app/contexts/organization";

function OrganizationSettingsPage() {
  const { selectedOrganization, isLoading } = useOrganization();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const header = (
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
  );

  if (isLoading) {
    return (
      <div className="max-w-2xl">
        {header}
        <div className="flex justify-center pt-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
        <CreateOrganizationModal
          open={showCreateModal}
          onOpenChange={setShowCreateModal}
        />
      </div>
    );
  }

  if (!selectedOrganization) {
    return (
      <div className="max-w-2xl">
        {header}
        <div className="flex justify-center pt-12">
          <div className="text-muted-foreground">
            Please select an organization
          </div>
        </div>
        <CreateOrganizationModal
          open={showCreateModal}
          onOpenChange={setShowCreateModal}
        />
      </div>
    );
  }

  return (
    <div className="max-w-2xl">
      {header}

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

      <Card className="mt-6 border-destructive">
        <CardHeader>
          <CardTitle className="text-destructive">Danger Zone</CardTitle>
          <CardDescription>
            Irreversible and destructive actions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Delete this organization</p>
              <p className="text-sm text-muted-foreground">
                Once you delete an organization, there is no going back. Please
                be certain.
              </p>
            </div>
            <Button
              variant="destructive"
              onClick={() => setShowDeleteModal(true)}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete
            </Button>
          </div>
        </CardContent>
      </Card>

      <CreateOrganizationModal
        open={showCreateModal}
        onOpenChange={setShowCreateModal}
      />
      <DeleteOrganizationModal
        open={showDeleteModal}
        onOpenChange={setShowDeleteModal}
      />
    </div>
  );
}

export const Route = createFileRoute("/cloud/settings/organization")({
  component: OrganizationSettingsPage,
});
