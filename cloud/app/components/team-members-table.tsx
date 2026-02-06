import {
  MoreHorizontal,
  RefreshCw,
  UserMinus,
  Shield,
  Loader2,
} from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import type { OrganizationInvitation } from "@/api/organization-invitations.schemas";
import type {
  OrganizationMemberWithUser,
  OrganizationRole,
} from "@/api/organization-memberships.schemas";

import {
  useResendInvitation,
  useRevokeInvitation,
} from "@/app/api/organization-invitations";
import {
  useUpdateMemberRole,
  useRemoveMember,
} from "@/app/api/organization-memberships";
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

interface TeamMembersTableProps {
  members: readonly OrganizationMemberWithUser[];
  pendingInvitations: readonly OrganizationInvitation[];
  organizationId: string;
  currentUserRole: OrganizationRole;
  currentUserId: string;
  canManageTeam: boolean;
  isLoading: boolean;
}

// Role hierarchy for permission checks
const CAN_OPERATE_ON: Record<OrganizationRole, OrganizationRole[]> = {
  OWNER: ["ADMIN", "MEMBER"],
  ADMIN: ["MEMBER"],
  MEMBER: [],
  BOT: [],
};

// Display labels for roles
const ROLE_LABELS: Record<OrganizationRole, string> = {
  OWNER: "Owner",
  ADMIN: "Admin",
  MEMBER: "Member",
  BOT: "Bot",
};

type ConfirmDialogState = {
  type: "remove" | "revoke";
  target: { id: string; name: string };
} | null;

export function TeamMembersTable({
  members,
  pendingInvitations,
  organizationId,
  currentUserRole,
  currentUserId,
  canManageTeam,
  isLoading,
}: TeamMembersTableProps) {
  const [confirmDialog, setConfirmDialog] = useState<ConfirmDialogState>(null);

  const updateRole = useUpdateMemberRole();
  const removeMember = useRemoveMember();
  const resendInvitation = useResendInvitation();
  const revokeInvitation = useRevokeInvitation();

  const canOperateOn = (targetRole: OrganizationRole) =>
    CAN_OPERATE_ON[currentUserRole].includes(targetRole);

  const getAssignableRoles = (): OrganizationRole[] => {
    return CAN_OPERATE_ON[currentUserRole];
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  // Empty state
  if (members.length === 0 && pendingInvitations.length === 0) {
    return (
      <div className="text-muted-foreground flex items-center justify-center rounded-lg border border-dashed py-12 text-center">
        <p>No team members yet. Invite someone to get started!</p>
      </div>
    );
  }

  const handleRoleChange = async (
    memberId: string,
    newRole: OrganizationRole,
  ) => {
    try {
      await updateRole.mutateAsync({
        organizationId,
        memberId,
        data: { role: newRole as "ADMIN" | "MEMBER" },
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
        memberId: confirmDialog.target.id,
      });
      toast.success("Member removed successfully");
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Failed to remove member",
      );
    }
    setConfirmDialog(null);
  };

  const handleResendInvitation = async (invitationId: string) => {
    try {
      await resendInvitation.mutateAsync({ organizationId, invitationId });
      toast.success("Invitation resent");
    } catch {
      toast.error("Failed to resend invitation");
    }
  };

  const handleRevokeInvitation = async () => {
    if (!confirmDialog || confirmDialog.type !== "revoke") return;
    try {
      await revokeInvitation.mutateAsync({
        organizationId,
        invitationId: confirmDialog.target.id,
      });
      toast.success("Invitation revoked");
    } catch {
      toast.error("Failed to revoke invitation");
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
              <TableHead>Status</TableHead>
              {canManageTeam && <TableHead className="w-[50px]"></TableHead>}
            </TableRow>
          </TableHeader>
          <TableBody>
            {/* Active members */}
            {members.map((member) => {
              const isSelf = member.memberId === currentUserId;
              const canOperate = canOperateOn(member.role) && !isSelf;
              const assignableRoles = getAssignableRoles().filter(
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
                  <TableCell>
                    <Badge
                      variant="outline"
                      className="bg-green-50 text-green-700 border-green-200 dark:bg-green-950 dark:text-green-300 dark:border-green-800"
                    >
                      Active
                    </Badge>
                  </TableCell>
                  {canManageTeam && (
                    <TableCell>
                      {canOperate && (
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
                              Remove member
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      )}
                    </TableCell>
                  )}
                </TableRow>
              );
            })}

            {/* Pending invitations */}
            {pendingInvitations.map((invitation) => (
              <TableRow key={invitation.id} className="opacity-60">
                <TableCell>
                  <div className="flex flex-col">
                    <span className="font-medium text-muted-foreground">—</span>
                    <span className="text-sm text-muted-foreground">
                      {invitation.recipientEmail}
                    </span>
                  </div>
                </TableCell>
                <TableCell>
                  <Badge variant="secondary">
                    {ROLE_LABELS[invitation.role as OrganizationRole] ||
                      invitation.role}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Badge
                    variant="outline"
                    className="bg-yellow-50 text-yellow-700 border-yellow-200 dark:bg-yellow-950 dark:text-yellow-300 dark:border-yellow-800"
                  >
                    Pending
                  </Badge>
                </TableCell>
                {canManageTeam && (
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem
                          onClick={() =>
                            void handleResendInvitation(invitation.id)
                          }
                        >
                          <RefreshCw className="h-4 w-4 mr-2" />
                          Resend invitation
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                          className="text-destructive focus:text-destructive"
                          onClick={() =>
                            setConfirmDialog({
                              type: "revoke",
                              target: {
                                id: invitation.id,
                                name: invitation.recipientEmail,
                              },
                            })
                          }
                        >
                          <UserMinus className="h-4 w-4 mr-2" />
                          Revoke invitation
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                )}
              </TableRow>
            ))}
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
            <AlertDialogTitle>
              {confirmDialog?.type === "remove"
                ? "Remove team member?"
                : "Revoke invitation?"}
            </AlertDialogTitle>
            <AlertDialogDescription>
              {confirmDialog?.type === "remove"
                ? `This will remove ${confirmDialog.target.name} from the organization. They will lose access immediately.`
                : `This will cancel the invitation to ${confirmDialog?.target.name}. They will no longer be able to accept it.`}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              onClick={
                confirmDialog?.type === "remove"
                  ? () => void handleRemoveMember()
                  : () => void handleRevokeInvitation()
              }
            >
              {confirmDialog?.type === "remove" ? "Remove" : "Revoke"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
