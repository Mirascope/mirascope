import { createFileRoute } from "@tanstack/react-router";
import { Loader2 } from "lucide-react";
import { useOrganization } from "@/app/contexts/organization";
import { useAuth } from "@/app/contexts/auth";
import { BatchInviteSection } from "@/app/components/batch-invite-section";
import { TeamMembersSection } from "@/app/components/team-members-section";

function TeamSettingsPage() {
  const { selectedOrganization, isLoading } = useOrganization();
  const { user } = useAuth();

  const header = (
    <div className="mb-6">
      <h1 className="text-2xl font-semibold">Team</h1>
      <p className="text-muted-foreground mt-1">
        Manage your organization's team members and invitations
      </p>
    </div>
  );

  if (isLoading) {
    return (
      <div className="max-w-3xl">
        {header}
        <div className="flex justify-center pt-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    );
  }

  if (!selectedOrganization) {
    return (
      <div className="max-w-3xl">
        {header}
        <div className="flex justify-center pt-12">
          <div className="text-muted-foreground">
            Please select an organization
          </div>
        </div>
      </div>
    );
  }

  const userRole = selectedOrganization.role;
  const canManageTeam = userRole === "OWNER" || userRole === "ADMIN";
  const canInviteAdmin = userRole === "OWNER";

  return (
    <div className="max-w-3xl space-y-6">
      {header}

      {canManageTeam && (
        <BatchInviteSection
          organizationId={selectedOrganization.id}
          canInviteAdmin={canInviteAdmin}
        />
      )}

      <TeamMembersSection
        organizationId={selectedOrganization.id}
        currentUserRole={userRole}
        currentUserId={user?.id ?? ""}
        canManageTeam={canManageTeam}
      />
    </div>
  );
}

export const Route = createFileRoute("/cloud/settings/team")({
  component: TeamSettingsPage,
});
