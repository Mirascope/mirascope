import type { OrganizationRole } from "@/db/schema";

import { useOrganizationInvitations } from "@/app/api/organization-invitations";
import { OrganizationInvitationDialog } from "@/app/components/organization-invitation-dialog";
import { OrganizationInvitationsTable } from "@/app/components/organization-invitations-table";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/app/components/ui/card";

interface OrganizationInvitationsSectionProps {
  organizationId: string | null;
  userRole?: OrganizationRole;
}

export function OrganizationInvitationsSection({
  organizationId,
  userRole,
}: OrganizationInvitationsSectionProps) {
  const { data: invitations, isLoading } = useOrganizationInvitations(
    organizationId ?? "",
  );

  // Only OWNER and ADMIN can access invitations
  if (!userRole || (userRole !== "OWNER" && userRole !== "ADMIN")) {
    return null;
  }

  if (!organizationId) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Team Invitations</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            Select an organization to manage invitations.
          </p>
        </CardContent>
      </Card>
    );
  }

  const canInviteAdmin = userRole === "OWNER";

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Team Invitations</CardTitle>
          <OrganizationInvitationDialog
            organizationId={organizationId}
            canInviteAdmin={canInviteAdmin}
          />
        </div>
      </CardHeader>
      <CardContent>
        <OrganizationInvitationsTable
          invitations={invitations ?? []}
          organizationId={organizationId}
          isLoading={isLoading}
        />
      </CardContent>
    </Card>
  );
}
