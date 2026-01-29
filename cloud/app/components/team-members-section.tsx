import type { OrganizationRole } from "@/api/organization-memberships.schemas";

import { useOrganizationInvitations } from "@/app/api/organization-invitations";
import { useOrganizationMembers } from "@/app/api/organization-memberships";
import { TeamMembersTable } from "@/app/components/team-members-table";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";

interface TeamMembersSectionProps {
  organizationId: string;
  currentUserRole: OrganizationRole;
  currentUserId: string;
  canManageTeam: boolean;
}

export function TeamMembersSection({
  organizationId,
  currentUserRole,
  currentUserId,
  canManageTeam,
}: TeamMembersSectionProps) {
  const { data: members, isLoading: membersLoading } =
    useOrganizationMembers(organizationId);
  const { data: invitations, isLoading: invitationsLoading } =
    useOrganizationInvitations(organizationId);

  const isLoading = membersLoading || invitationsLoading;

  // Filter to only pending invitations
  const pendingInvitations = (invitations ?? []).filter(
    (inv) => inv.status === "pending",
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>Team Members</CardTitle>
        <CardDescription>
          View and manage your organization's team members
        </CardDescription>
      </CardHeader>
      <CardContent>
        <TeamMembersTable
          members={members ?? []}
          pendingInvitations={pendingInvitations}
          organizationId={organizationId}
          currentUserRole={currentUserRole}
          currentUserId={currentUserId}
          canManageTeam={canManageTeam}
          isLoading={isLoading}
        />
      </CardContent>
    </Card>
  );
}
