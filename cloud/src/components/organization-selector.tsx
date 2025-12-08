import { useState } from "react";
import { Cause } from "effect";
import { Button } from "@/src/components/ui/button";
import { Input } from "@/src/components/ui/input";
import {
  Modal,
  ModalHeader,
  ModalBody,
  ModalFooter,
} from "@/src/components/ui/modal";
import { useOrganization } from "@/src/contexts/organization";
import {
  useCreateOrganization,
  useDeleteOrganization,
} from "@/src/api/organizations";
import type { OrganizationWithRole } from "@/api/api";

export function OrganizationSelector() {
  const {
    organization,
    organizations,
    isLoading,
    selectOrganization,
    refetch,
  } = useOrganization();

  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [newOrgName, setNewOrgName] = useState("");
  const [createError, setCreateError] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const createOrgMutation = useCreateOrganization();
  const deleteOrgMutation = useDeleteOrganization();

  const handleSelectOrg = (org: OrganizationWithRole) => {
    selectOrganization(org);
    setIsDropdownOpen(false);
  };

  const handleCreateOrg = async () => {
    if (!newOrgName.trim()) {
      setCreateError("Organization name is required");
      return;
    }

    try {
      setCreateError(null);
      const newOrg = await createOrgMutation.mutateAsync({
        name: newOrgName.trim(),
      });
      selectOrganization(newOrg);
      setIsCreateModalOpen(false);
      setNewOrgName("");
      refetch();
    } catch (error) {
      const err = error as {
        match?: (handlers: Record<string, unknown>) => void;
      };
      if (err.match) {
        err.match({
          AlreadyExistsError: (e: { message?: string }) =>
            setCreateError(
              e.message || "An organization with that name already exists",
            ),
          UnauthorizedError: () => setCreateError("Please log in to continue"),
          DatabaseError: () => setCreateError("A database error occurred"),
          OrElse: (cause: Cause.Cause<unknown>) =>
            setCreateError(
              `Failed to create organization: ${Cause.pretty(cause)}`,
            ),
        });
      } else {
        setCreateError("Failed to create organization");
      }
    }
  };

  const handleDeleteOrg = async () => {
    if (!organization) return;

    try {
      setDeleteError(null);
      await deleteOrgMutation.mutateAsync(organization.id);
      setIsDeleteModalOpen(false);
      refetch();
    } catch (error) {
      const err = error as {
        match?: (handlers: Record<string, unknown>) => void;
      };
      if (err.match) {
        err.match({
          NotFoundError: () => setDeleteError("Organization not found"),
          PermissionDeniedError: (e: { message?: string }) =>
            setDeleteError(
              e.message ||
                "You don't have permission to delete this organization",
            ),
          UnauthorizedError: () => setDeleteError("Please log in to continue"),
          DatabaseError: () => setDeleteError("A database error occurred"),
          OrElse: (cause: Cause.Cause<unknown>) =>
            setDeleteError(
              `Failed to delete organization: ${Cause.pretty(cause)}`,
            ),
        });
      } else {
        setDeleteError("Failed to delete organization");
      }
    }
  };

  const openCreateModal = () => {
    setIsDropdownOpen(false);
    setCreateError(null);
    setNewOrgName("");
    setIsCreateModalOpen(true);
  };

  const openDeleteModal = () => {
    setDeleteError(null);
    setIsDeleteModalOpen(true);
  };

  if (isLoading) {
    return (
      <div className="flex items-center gap-2">
        <div className="h-10 w-48 animate-pulse rounded-md bg-muted" />
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <div className="relative">
        <Button
          variant="outline"
          onClick={() => setIsDropdownOpen(!isDropdownOpen)}
          className="min-w-48 justify-between"
        >
          <span className="truncate">
            {organization?.name || "Select organization"}
          </span>
          <ChevronDownIcon className="ml-2 h-4 w-4 shrink-0" />
        </Button>

        {isDropdownOpen && (
          <>
            <div
              className="fixed inset-0 z-40"
              onClick={() => setIsDropdownOpen(false)}
            />
            <div className="absolute left-0 top-full z-50 mt-1 w-full min-w-48 rounded-md border border-border bg-popover shadow-lg">
              <div className="max-h-60 overflow-y-auto py-1">
                {organizations.map((org) => (
                  <button
                    key={org.id}
                    onClick={() => handleSelectOrg(org)}
                    className={`flex w-full items-center px-3 py-2 text-left text-sm hover:bg-accent ${
                      org.id === organization?.id ? "bg-accent font-medium" : ""
                    }`}
                  >
                    <span className="truncate">{org.name}</span>
                    <span className="ml-auto text-xs text-muted-foreground">
                      {org.role.toLowerCase()}
                    </span>
                  </button>
                ))}
              </div>
              <div className="border-t border-border">
                <button
                  onClick={openCreateModal}
                  className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm hover:bg-accent"
                >
                  <PlusIcon className="h-4 w-4" />
                  Create new organization
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {organization && (
        <Button
          variant="ghost"
          size="sm"
          onClick={openDeleteModal}
          className="text-destructive hover:bg-destructive/10 hover:text-destructive"
          title="Delete organization"
        >
          <TrashIcon className="h-4 w-4" />
        </Button>
      )}

      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
      >
        <ModalHeader>Create Organization</ModalHeader>
        <ModalBody>
          <div className="space-y-4">
            <div>
              <label
                htmlFor="org-name"
                className="block text-sm font-medium text-foreground mb-2"
              >
                Organization Name
              </label>
              <Input
                id="org-name"
                type="text"
                value={newOrgName}
                onChange={(e) => setNewOrgName(e.target.value)}
                placeholder="My Organization"
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    void handleCreateOrg();
                  }
                }}
              />
            </div>
            {createError && (
              <p className="text-sm text-destructive">{createError}</p>
            )}
          </div>
        </ModalBody>
        <ModalFooter>
          <Button
            variant="outline"
            onClick={() => setIsCreateModalOpen(false)}
            disabled={createOrgMutation.isPending}
          >
            Cancel
          </Button>
          <Button
            onClick={() => void handleCreateOrg()}
            disabled={createOrgMutation.isPending}
          >
            {createOrgMutation.isPending ? "Creating..." : "Create"}
          </Button>
        </ModalFooter>
      </Modal>

      <Modal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
      >
        <ModalHeader>Delete Organization</ModalHeader>
        <ModalBody>
          <p>
            Are you sure you want to delete{" "}
            <strong>{organization?.name}</strong>?
          </p>
          <p className="mt-2 text-sm">
            This action cannot be undone. All data associated with this
            organization will be permanently deleted.
          </p>
          {deleteError && (
            <p className="mt-4 text-sm text-destructive">{deleteError}</p>
          )}
        </ModalBody>
        <ModalFooter>
          <Button
            variant="outline"
            onClick={() => setIsDeleteModalOpen(false)}
            disabled={deleteOrgMutation.isPending}
          >
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={() => void handleDeleteOrg()}
            disabled={deleteOrgMutation.isPending}
          >
            {deleteOrgMutation.isPending ? "Deleting..." : "Delete"}
          </Button>
        </ModalFooter>
      </Modal>
    </div>
  );
}

function ChevronDownIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 20 20"
      fill="currentColor"
      className={className}
    >
      <path
        fillRule="evenodd"
        d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z"
        clipRule="evenodd"
      />
    </svg>
  );
}

function PlusIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 20 20"
      fill="currentColor"
      className={className}
    >
      <path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z" />
    </svg>
  );
}

function TrashIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 20 20"
      fill="currentColor"
      className={className}
    >
      <path
        fillRule="evenodd"
        d="M8.75 1A2.75 2.75 0 006 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 10.23 1.482l.149-.022.841 10.518A2.75 2.75 0 007.596 19h4.807a2.75 2.75 0 002.742-2.53l.841-10.519.149.023a.75.75 0 00.23-1.482A41.03 41.03 0 0014 4.193V3.75A2.75 2.75 0 0011.25 1h-2.5zM10 4c.84 0 1.673.025 2.5.075V3.75c0-.69-.56-1.25-1.25-1.25h-2.5c-.69 0-1.25.56-1.25 1.25v.325C8.327 4.025 9.16 4 10 4zM8.58 7.72a.75.75 0 00-1.5.06l.3 7.5a.75.75 0 101.5-.06l-.3-7.5zm4.34.06a.75.75 0 10-1.5-.06l-.3 7.5a.75.75 0 101.5.06l.3-7.5z"
        clipRule="evenodd"
      />
    </svg>
  );
}
