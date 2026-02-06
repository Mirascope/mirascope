import { MoreHorizontal, UserMinus, Shield, Loader2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import type {
  ClawMemberWithUser,
  ClawRole,
} from "@/api/claw-memberships.schemas";

import {
  useUpdateClawMemberRole,
  useRemoveClawMember,
} from "@/app/api/claw-memberships";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/app/components/ui/alert-dialog";
import { Badge } from "@/app/components/ui/badge";
import { Button } from "@/app/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/app/components/ui/dropdown-menu";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/app/components/ui/table";

interface ClawMembersTableProps {
  members: readonly ClawMemberWithUser[];
  organizationId: string;
  clawId: string;
  currentUserId: string;
  canManageMembers: boolean;
  isLoading: boolean;
}

const CLAW_ROLES: ClawRole[] = ["ADMIN", "DEVELOPER", "VIEWER", "ANNOTATOR"];

const ROLE_LABELS: Record<ClawRole, string> = {
  ADMIN: "Admin",
  DEVELOPER: "Developer",
  VIEWER: "Viewer",
  ANNOTATOR: "Annotator",
};

type ConfirmDialogState = {
  type: "remove";
  target: { id: string; name: string };
} | null;

export function ClawMembersTable({
  members,
  organizationId,
  clawId,
  currentUserId,
  canManageMembers,
  isLoading,
}: ClawMembersTableProps) {
  const [confirmDialog, setConfirmDialog] = useState<ConfirmDialogState>(null);

  const updateRole = useUpdateClawMemberRole();
  const removeMember = useRemoveClawMember();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (members.length === 0) {
    return (
      <div className="text-muted-foreground flex items-center justify-center rounded-lg border border-dashed py-12 text-center">
        <p>No claw members yet. Add someone to get started!</p>
      </div>
    );
  }

  const handleRoleChange = async (memberId: string, newRole: ClawRole) => {
    try {
      await updateRole.mutateAsync({
        organizationId,
        clawId,
        memberId,
        data: { role: newRole },
      });
      toast.success("Role updated successfully");
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Failed to update role",
      );
    }
  };

  const handleRemoveMember = async () => {
    if (!confirmDialog || confirmDialog.type !== "remove") return;
    try {
      await removeMember.mutateAsync({
        organizationId,
        clawId,
        memberId: confirmDialog.target.id,
      });
      toast.success("Member removed from claw");
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Failed to remove member",
      );
    }
    setConfirmDialog(null);
  };

  return (
    <>
      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Role</TableHead>
              {canManageMembers && <TableHead className="w-[50px]"></TableHead>}
            </TableRow>
          </TableHeader>
          <TableBody>
            {members.map((member) => {
              const isSelf = member.memberId === currentUserId;
              const assignableRoles = CLAW_ROLES.filter(
                (r) => r !== member.role,
              );

              return (
                <TableRow key={member.memberId}>
                  <TableCell>
                    <div className="flex flex-col">
                      <span className="font-medium">
                        {member.name || "—"}
                        {isSelf && (
                          <span className="text-muted-foreground ml-1">
                            (you)
                          </span>
                        )}
                      </span>
                      <span className="text-sm text-muted-foreground">
                        {member.email}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="secondary">
                      {ROLE_LABELS[member.role]}
                    </Badge>
                  </TableCell>
                  {canManageMembers && (
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          {assignableRoles.map((role) => (
                            <DropdownMenuItem
                              key={role}
                              onClick={() =>
                                void handleRoleChange(member.memberId, role)
                              }
                            >
                              <Shield className="h-4 w-4 mr-2" />
                              Change to {ROLE_LABELS[role]}
                            </DropdownMenuItem>
                          ))}
                          {assignableRoles.length > 0 && (
                            <DropdownMenuSeparator />
                          )}
                          <DropdownMenuItem
                            className="text-destructive focus:text-destructive"
                            onClick={() =>
                              setConfirmDialog({
                                type: "remove",
                                target: {
                                  id: member.memberId,
                                  name: member.name || member.email,
                                },
                              })
                            }
                          >
                            <UserMinus className="h-4 w-4 mr-2" />
                            Remove from claw
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  )}
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>

      <AlertDialog
        open={!!confirmDialog}
        onOpenChange={() => setConfirmDialog(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Remove claw member?</AlertDialogTitle>
            <AlertDialogDescription>
              This will remove {confirmDialog?.target.name} from the claw. They
              will lose access to claw resources immediately.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              onClick={() => void handleRemoveMember()}
            >
              Remove
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
