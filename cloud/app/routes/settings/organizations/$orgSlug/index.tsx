import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { Trash2 } from "lucide-react";
import { useState } from "react";

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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/app/components/ui/select";
import { useOrganization } from "@/app/contexts/organization";

function OrganizationSettingsPage() {
  const { orgSlug } = Route.useParams();
  const navigate = useNavigate();
  const { organizations, selectedOrganization } = useOrganization();
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const handleOrgChange = (value: string) => {
    const org = organizations.find((o) => o.id === value);
    if (org) {
      void navigate({
        to: "/settings/organizations/$orgSlug",
        params: { orgSlug: org.slug },
      });
    }
  };

  const header = (
    <div className="mb-6 flex items-start justify-between">
      <div>
        <h1 className="text-2xl font-semibold">Organization</h1>
        <p className="text-muted-foreground mt-1">
          Manage your organization settings
        </p>
      </div>
      {organizations.length > 1 && (
        <Select
          value={selectedOrganization?.id || ""}
          onValueChange={handleOrgChange}
        >
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Select organization" />
          </SelectTrigger>
          <SelectContent>
            {organizations.map((org) => (
              <SelectItem key={org.id} value={org.id}>
                {org.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )}
    </div>
  );

  if (!selectedOrganization) {
    return (
      <div className="max-w-2xl">
        {header}
        <div className="flex justify-center pt-12">
          <div className="text-muted-foreground">
            Organization not found: {orgSlug}
          </div>
        </div>
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

      <DeleteOrganizationModal
        open={showDeleteModal}
        onOpenChange={setShowDeleteModal}
      />
    </div>
  );
}

export const Route = createFileRoute("/settings/organizations/$orgSlug/")({
  component: OrganizationSettingsPage,
});
