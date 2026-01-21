import { useState } from "react";
import { Button } from "@/app/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/app/components/ui/dialog";
import { Label } from "@/app/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/app/components/ui/select";
import { Alert, AlertDescription } from "@/app/components/ui/alert";
import { Loader2, AlertTriangle } from "lucide-react";
import { useOrganizationMembers } from "@/app/api/organization-memberships";
import { useAddProjectMember } from "@/app/api/project-memberships";
import { toast } from "sonner";
import type { ProjectRole } from "@/api/project-memberships.schemas";
import type { ProjectMemberWithUser } from "@/api/project-memberships.schemas";

interface AddProjectMemberDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  organizationId: string;
  projectId: string;
  existingMembers: readonly ProjectMemberWithUser[];
}

const PROJECT_ROLES: {
  value: ProjectRole;
  label: string;
  description: string;
}[] = [
  {
    value: "ADMIN",
    label: "Admin",
    description: "Can manage project members and settings",
  },
  {
    value: "DEVELOPER",
    label: "Developer",
    description: "Can view and use the project",
  },
  {
    value: "VIEWER",
    label: "Viewer",
    description: "Read-only access to the project",
  },
  {
    value: "ANNOTATOR",
    label: "Annotator",
    description: "Access to annotation queues",
  },
];

export function AddProjectMemberDialog({
  open,
  onOpenChange,
  organizationId,
  projectId,
  existingMembers,
}: AddProjectMemberDialogProps) {
  const [selectedMemberId, setSelectedMemberId] = useState<string>("");
  const [selectedRole, setSelectedRole] = useState<ProjectRole>("DEVELOPER");
  const [apiError, setApiError] = useState<string | null>(null);

  const { data: orgMembers, isLoading: loadingOrgMembers } =
    useOrganizationMembers(organizationId);
  const addMember = useAddProjectMember();

  // Filter out members already in the project
  const existingMemberIds = new Set(existingMembers.map((m) => m.memberId));
  const availableMembers = (orgMembers ?? []).filter(
    (m) => !existingMemberIds.has(m.memberId),
  );

  const handleSubmit = async () => {
    if (!selectedMemberId) return;
    setApiError(null);

    try {
      await addMember.mutateAsync({
        organizationId,
        projectId,
        data: { memberId: selectedMemberId, role: selectedRole },
      });
      toast.success("Member added to project");
      handleClose();
    } catch (error) {
      if (error instanceof Error) {
        setApiError(error.message);
      } else {
        setApiError("Failed to add member");
      }
    }
  };

  const handleClose = () => {
    onOpenChange(false);
    // Reset form after dialog closes
    setTimeout(() => {
      setSelectedMemberId("");
      setSelectedRole("DEVELOPER");
      setApiError(null);
    }, 300);
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Add Project Member</DialogTitle>
          <DialogDescription>
            Add an organization member to this project with a specific role.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          {apiError && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{apiError}</AlertDescription>
            </Alert>
          )}

          <div className="grid gap-2">
            <Label htmlFor="member">Organization Member</Label>
            {loadingOrgMembers ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="h-4 w-4 animate-spin" />
              </div>
            ) : availableMembers.length === 0 ? (
              <p className="text-sm text-muted-foreground py-2">
                All organization members are already in this project.
              </p>
            ) : (
              <Select
                value={selectedMemberId}
                onValueChange={setSelectedMemberId}
              >
                <SelectTrigger id="member" className="py-6">
                  <SelectValue placeholder="Select a member" />
                </SelectTrigger>
                <SelectContent>
                  {availableMembers.map((member) => (
                    <SelectItem key={member.memberId} value={member.memberId}>
                      <div className="flex flex-col items-start py-0.5">
                        <span className="font-medium">
                          {member.name || member.email}
                        </span>
                        {member.name && (
                          <span className="text-xs text-muted-foreground">
                            {member.email}
                          </span>
                        )}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </div>

          <div className="grid gap-2">
            <Label htmlFor="role">Project Role</Label>
            <Select
              value={selectedRole}
              onValueChange={(v) => setSelectedRole(v as ProjectRole)}
            >
              <SelectTrigger id="role" className="py-6">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {PROJECT_ROLES.map((role) => (
                  <SelectItem key={role.value} value={role.value}>
                    <div className="flex flex-col items-start py-1">
                      <span className="font-medium">{role.label}</span>
                      <span className="text-xs text-muted-foreground">
                        {role.description}
                      </span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={handleClose}
            disabled={addMember.isPending}
          >
            Cancel
          </Button>
          <Button
            onClick={() => void handleSubmit()}
            disabled={!selectedMemberId || addMember.isPending}
          >
            {addMember.isPending ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Adding...
              </>
            ) : (
              "Add Member"
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
