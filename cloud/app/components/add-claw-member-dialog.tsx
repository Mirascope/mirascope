import { Loader2, AlertTriangle } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import type { ClawRole } from "@/api/claw-memberships.schemas";
import type { ClawMemberWithUser } from "@/api/claw-memberships.schemas";

import { useAddClawMember } from "@/app/api/claw-memberships";
import { useOrganizationMembers } from "@/app/api/organization-memberships";
import { Alert, AlertDescription } from "@/app/components/ui/alert";
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

interface AddClawMemberDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  organizationId: string;
  clawId: string;
  existingMembers: readonly ClawMemberWithUser[];
}

const CLAW_ROLES: {
  value: ClawRole;
  label: string;
  description: string;
}[] = [
  {
    value: "ADMIN",
    label: "Admin",
    description: "Can manage claw members and settings",
  },
  {
    value: "DEVELOPER",
    label: "Developer",
    description: "Can view and configure the claw",
  },
  {
    value: "VIEWER",
    label: "Viewer",
    description: "Read-only access to the claw",
  },
  {
    value: "ANNOTATOR",
    label: "Annotator",
    description: "Access to annotation features",
  },
];

export function AddClawMemberDialog({
  open,
  onOpenChange,
  organizationId,
  clawId,
  existingMembers,
}: AddClawMemberDialogProps) {
  const [selectedMemberId, setSelectedMemberId] = useState<string>("");
  const [selectedRole, setSelectedRole] = useState<ClawRole>("DEVELOPER");
  const [apiError, setApiError] = useState<string | null>(null);

  const { data: orgMembers, isLoading: loadingOrgMembers } =
    useOrganizationMembers(organizationId);
  const addMember = useAddClawMember();

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
        clawId,
        data: { memberId: selectedMemberId, role: selectedRole },
      });
      toast.success("Member added to claw");
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
          <DialogTitle>Add Claw Member</DialogTitle>
          <DialogDescription>
            Add an organization member to this claw with a specific role.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 px-6 py-4">
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
                All organization members are already in this claw.
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
            <Label htmlFor="role">Claw Role</Label>
            <Select
              value={selectedRole}
              onValueChange={(v) => setSelectedRole(v as ClawRole)}
            >
              <SelectTrigger id="role" className="py-6">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {CLAW_ROLES.map((role) => (
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
