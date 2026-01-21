import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/app/components/ui/table";
import { Button } from "@/app/components/ui/button";
import { InvitationStatusBadge } from "@/app/components/ui/invitation-status-badge";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/app/components/ui/alert-dialog";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/app/components/ui/tooltip";
import { RefreshCw, X, Loader2 } from "lucide-react";
import type { OrganizationInvitation } from "@/api/organization-invitations.schemas";
import {
  useResendInvitation,
  useRevokeInvitation,
} from "@/app/api/organization-invitations";
import { toast } from "sonner";

interface OrganizationInvitationsTableProps {
  invitations: readonly OrganizationInvitation[];
  organizationId: string;
  isLoading?: boolean;
}

function formatDate(date: Date): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(date);
}

function getDaysUntilExpiration(expiresAt: Date): string {
  const now = new Date();
  const diffTime = expiresAt.getTime() - now.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    return "Expired";
  } else if (diffDays === 0) {
    return "Today";
  } else if (diffDays === 1) {
    return "1 day";
  } else {
    return `${diffDays} days`;
  }
}

export function OrganizationInvitationsTable({
  invitations,
  organizationId,
  isLoading = false,
}: OrganizationInvitationsTableProps) {
  const resendInvitation = useResendInvitation();
  const revokeInvitation = useRevokeInvitation();

  const handleResend = async (invitationId: string) => {
    try {
      await resendInvitation.mutateAsync({
        organizationId,
        invitationId,
      });
      toast.success("Invitation resent successfully");
    } catch (error) {
      toast.error("Failed to resend invitation");
      console.error("Resend error:", error);
    }
  };

  const handleRevoke = async (invitationId: string) => {
    try {
      await revokeInvitation.mutateAsync({
        organizationId,
        invitationId,
      });
      toast.success("Invitation revoked successfully");
    } catch (error) {
      toast.error("Failed to revoke invitation");
      console.error("Revoke error:", error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (invitations.length === 0) {
    return (
      <div className="text-muted-foreground flex items-center justify-center rounded-lg border border-dashed py-12 text-center">
        <p>No pending invitations</p>
      </div>
    );
  }

  return (
    <TooltipProvider>
      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Email</TableHead>
              <TableHead>Role</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Sent</TableHead>
              <TableHead>Expires In</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {invitations.map((invitation) => (
              <TableRow key={invitation.id}>
                <TableCell className="font-medium">
                  {invitation.recipientEmail}
                </TableCell>
                <TableCell>{invitation.role}</TableCell>
                <TableCell>
                  <InvitationStatusBadge status={invitation.status} />
                </TableCell>
                <TableCell>{formatDate(invitation.createdAt)}</TableCell>
                <TableCell>
                  {getDaysUntilExpiration(invitation.expiresAt)}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex items-center justify-end gap-1">
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => void handleResend(invitation.id)}
                          disabled={resendInvitation.isPending}
                        >
                          <RefreshCw className="h-4 w-4" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>Resend invitation</TooltipContent>
                    </Tooltip>

                    <AlertDialog>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <AlertDialogTrigger asChild>
                            <Button
                              variant="ghost"
                              size="icon"
                              disabled={revokeInvitation.isPending}
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          </AlertDialogTrigger>
                        </TooltipTrigger>
                        <TooltipContent>Revoke invitation</TooltipContent>
                      </Tooltip>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>
                            Revoke invitation?
                          </AlertDialogTitle>
                          <AlertDialogDescription>
                            This will cancel the invitation to{" "}
                            <strong>{invitation.recipientEmail}</strong>. They
                            will no longer be able to accept it.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          <AlertDialogAction
                            onClick={() => void handleRevoke(invitation.id)}
                          >
                            Revoke
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </TooltipProvider>
  );
}
