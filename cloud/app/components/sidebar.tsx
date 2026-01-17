import { useState, type FormEvent } from "react";
import { Link, useRouterState } from "@tanstack/react-router";
import { Button } from "@/app/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/app/components/ui/select";
import { useOrganization } from "@/app/contexts/organization";
import { useCreateOrganization } from "@/app/api/organizations";
import { generateSlug } from "@/db/slug";

function CreateOrganizationDialog({ onClose }: { onClose: () => void }) {
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
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to create organization",
      );
    }
  };

  return (
    <div className="p-3 border-t border-border">
      <form onSubmit={(e) => void handleSubmit(e)} className="space-y-2">
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Organization name"
          className="w-full px-2 py-1.5 text-sm border border-input rounded-md bg-background"
          autoFocus
        />
        {error && <p className="text-xs text-destructive">{error}</p>}
        <div className="flex gap-2">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            size="sm"
            disabled={createOrganization.isPending}
            className="flex-1"
          >
            {createOrganization.isPending ? "..." : "Create"}
          </Button>
        </div>
      </form>
    </div>
  );
}

export function Sidebar() {
  const {
    organizations,
    selectedOrganization,
    setSelectedOrganization,
    isLoading: orgsLoading,
  } = useOrganization();

  const [showCreateOrg, setShowCreateOrg] = useState(false);

  const router = useRouterState();
  const currentPath = router.location.pathname;

  const handleSelectChange = (value: string) => {
    if (value === "__create_new__") {
      setShowCreateOrg(true);
    } else {
      const org = organizations.find((o) => o.id === value);
      setSelectedOrganization(org || null);
    }
  };

  const isActive = (path: string) => currentPath === path;

  return (
    <aside className="w-48 h-full flex flex-col bg-background border-r border-border">
      {/* Dashboard link at top */}
      <div className="px-2 pt-4">
        <Link
          to="/cloud/dashboard"
          className={`relative flex items-center justify-center px-3 py-2 text-lg rounded-md text-foreground font-handwriting-descent ${
            isActive("/cloud/dashboard")
              ? "bg-muted font-medium"
              : "hover:bg-muted"
          }`}
        >
          <svg
            className="w-5 h-5 absolute left-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
            />
          </svg>
          Dashboard
        </Link>
      </div>

      {/* Main content area - empty for now */}
      <div className="flex-1 overflow-y-auto px-2">
        {/* Future: Navigation items will go here */}
      </div>

      {/* Settings link */}
      <div className="px-2 pb-2">
        <Link
          to="/cloud/settings"
          className={`relative flex items-center justify-center px-3 py-2 text-lg rounded-md text-foreground font-handwriting-descent ${
            isActive("/cloud/settings")
              ? "bg-muted font-medium"
              : "hover:bg-muted"
          }`}
        >
          <svg
            className="w-5 h-5 absolute left-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
            />
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            />
          </svg>
          Settings
        </Link>
      </div>

      {/* Organization selector at bottom */}
      <div className="px-2 pb-3 border-t border-border pt-3">
        {orgsLoading ? (
          <div className="text-sm text-muted-foreground">Loading...</div>
        ) : (
          <Select
            value={selectedOrganization?.id || ""}
            onValueChange={handleSelectChange}
          >
            <SelectTrigger className="bg-background">
              <SelectValue placeholder="Select organization" />
            </SelectTrigger>
            <SelectContent>
              {organizations.map((org) => (
                <SelectItem key={org.id} value={org.id}>
                  {org.name}
                </SelectItem>
              ))}
              <SelectItem
                value="__create_new__"
                className="text-primary font-medium"
              >
                + Create New Organization
              </SelectItem>
            </SelectContent>
          </Select>
        )}
      </div>

      {showCreateOrg && (
        <CreateOrganizationDialog onClose={() => setShowCreateOrg(false)} />
      )}
    </aside>
  );
}
