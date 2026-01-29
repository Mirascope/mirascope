import { Link } from "@tanstack/react-router";
import { useState, type FormEvent } from "react";

import type { PublicOrganizationWithMembership } from "@/db/schema/organization-memberships";

import {
  useOrganizations,
  useCreateOrganization,
  useDeleteOrganization,
} from "@/app/api/organizations";
import { Button } from "@/app/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";
import { getErrorMessage } from "@/app/lib/errors";
import { generateSlug } from "@/db/slug";

function CreateOrganizationForm({ onClose }: { onClose: () => void }) {
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const createOrganization = useCreateOrganization();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError("Organization name is required");
      return;
    }

    try {
      await createOrganization.mutateAsync({
        name: name.trim(),
        slug: generateSlug(name.trim()),
      });
      onClose();
    } catch (err: unknown) {
      setError(getErrorMessage(err, "Failed to create organization"));
    }
  };

  return (
    <form onSubmit={(e) => void handleSubmit(e)} className="space-y-4">
      <div className="space-y-2">
        <label htmlFor="org-name" className="text-sm font-medium">
          Organization Name
        </label>
        <input
          id="org-name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter organization name"
          className="w-full px-3 py-2 border border-input rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          autoFocus
        />
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
      <div className="flex gap-2 justify-end">
        <Button type="button" variant="outline" onClick={onClose}>
          Cancel
        </Button>
        <Button type="submit" disabled={createOrganization.isPending}>
          {createOrganization.isPending ? "Creating..." : "Create"}
        </Button>
      </div>
    </form>
  );
}

function OrganizationCard({
  organization,
}: {
  organization: PublicOrganizationWithMembership;
}) {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const deleteOrganization = useDeleteOrganization();

  const handleDelete = async () => {
    try {
      await deleteOrganization.mutateAsync(organization.id);
    } catch {
      // Error is handled by the mutation
    }
  };

  const roleColors: Record<string, string> = {
    OWNER:
      "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300",
    ADMIN:
      "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300",
    MEMBER: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300",
  };

  return (
    <Card className="group hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-lg">{organization.name}</CardTitle>
          <span
            className={`text-xs px-2 py-1 rounded-full font-medium ${roleColors[organization.role] || "bg-muted text-muted-foreground"}`}
          >
            {organization.role}
          </span>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <p className="text-xs text-muted-foreground font-mono">
            {organization.id}
          </p>
          {organization.role === "OWNER" && (
            <div className="flex gap-2">
              {showDeleteConfirm ? (
                <>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setShowDeleteConfirm(false)}
                    disabled={deleteOrganization.isPending}
                  >
                    Cancel
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="text-destructive hover:text-destructive hover:bg-destructive/10"
                    onClick={() => void handleDelete()}
                    disabled={deleteOrganization.isPending}
                  >
                    {deleteOrganization.isPending ? "Deleting..." : "Confirm"}
                  </Button>
                </>
              ) : (
                <Button
                  size="sm"
                  variant="ghost"
                  className="opacity-0 group-hover:opacity-100 transition-opacity text-destructive hover:text-destructive hover:bg-destructive/10"
                  onClick={() => setShowDeleteConfirm(true)}
                >
                  Delete
                </Button>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export function OrganizationsPage() {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const { data: organizations, isLoading, error } = useOrganizations();

  if (isLoading) {
    return (
      <div className="text-muted-foreground">Loading organizations...</div>
    );
  }

  if (error) {
    return <div className="text-destructive">Failed to load organizations</div>;
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              to="/"
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              ← Back
            </Link>
            <h1 className="text-xl font-semibold">Organizations</h1>
          </div>
          <Button onClick={() => setShowCreateForm(true)}>
            New Organization
          </Button>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {showCreateForm && (
          <Card className="mb-8 max-w-md mx-auto">
            <CardHeader>
              <CardTitle>Create Organization</CardTitle>
            </CardHeader>
            <CardContent>
              <CreateOrganizationForm
                onClose={() => setShowCreateForm(false)}
              />
            </CardContent>
          </Card>
        )}

        {!organizations || organizations.length === 0 ? (
          <div className="text-center py-16">
            <p className="text-muted-foreground mb-4">
              You don't have any organizations yet.
            </p>
            {!showCreateForm && (
              <Button onClick={() => setShowCreateForm(true)}>
                Create your first organization
              </Button>
            )}
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {organizations.map((org) => (
              <OrganizationCard key={org.id} organization={org} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
