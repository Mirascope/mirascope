import { MoreHorizontal, UserMinus, Shield, Loader2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import type {
  ProjectMemberWithUser,
  ProjectRole,
} from "@/api/project-memberships.schemas";

import {
  useUpdateProjectMemberRole,
  useRemoveProjectMember,
} from "@/app/api/project-memberships";
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

interface ProjectMembersTableProps {
  members: readonly ProjectMemberWithUser[];
  organizationId: string;
  projectId: string;
  currentUserId: string;
  canManageMembers: boolean;
  isLoading: boolean;
}

const PROJECT_ROLES: ProjectRole[] = [
  "ADMIN",
  "DEVELOPER",
  "VIEWER",
  "ANNOTATOR",
];

const ROLE_LABELS: Record<ProjectRole, string> = {
  ADMIN: "Admin",
  DEVELOPER: "Developer",
  VIEWER: "Viewer",
  ANNOTATOR: "Annotator",
};

type ConfirmDialogState = {
  type: "remove";
  target: { id: string; name: string };
} | null;

export function ProjectMembersTable({
  members,
  organizationId,
  projectId,
  currentUserId,
  canManageMembers,
  isLoading,
}: ProjectMembersTableProps) {
  const [confirmDialog, setConfirmDialog] = useState<ConfirmDialogState>(null);

  const updateRole = useUpdateProjectMemberRole();
  const removeMember = useRemoveProjectMember();

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  // Empty state
  if (members.length === 0) {
    return (
      <div className="text-muted-foreground flex items-center justify-center rounded-lg border border-dashed py-12 text-center">
        <p>No project members yet. Add someone to get started!</p>
      </div>
    );
  }

  const handleRoleChange = async (memberId: string, newRole: ProjectRole) => {
    try {
      await updateRole.mutateAsync({
        organizationId,
        projectId,
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
        projectId,
        memberId: confirmDialog.target.id,
      });
      toast.success("Member removed from project");
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
              const assignableRoles = PROJECT_ROLES.filter(
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
                            Remove from project
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

      {/* Confirmation Dialog */}
      <AlertDialog
        open={!!confirmDialog}
        onOpenChange={() => setConfirmDialog(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Remove project member?</AlertDialogTitle>
            <AlertDialogDescription>
              This will remove {confirmDialog?.target.name} from the project.
              They will lose access to project resources immediately.
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
