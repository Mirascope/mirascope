import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";
import { Button } from "@/app/components/ui/button";
import { UserPlus } from "lucide-react";
import { ProjectMembersTable } from "@/app/components/project-members-table";
import { AddProjectMemberDialog } from "@/app/components/add-project-member-dialog";
import { useProjectMembers } from "@/app/api/project-memberships";

interface ProjectMembersSectionProps {
  organizationId: string;
  projectId: string;
  currentUserId: string;
  canManageMembers: boolean;
}

export function ProjectMembersSection({
  organizationId,
  projectId,
  currentUserId,
  canManageMembers,
}: ProjectMembersSectionProps) {
  const [showAddDialog, setShowAddDialog] = useState(false);

  const { data: members, isLoading } = useProjectMembers(
    organizationId,
    projectId,
  );

  return (
    <>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <div>
            <CardTitle>Project Members</CardTitle>
            <CardDescription>
              Manage who has access to this project
            </CardDescription>
          </div>
          {canManageMembers && (
            <Button onClick={() => setShowAddDialog(true)}>
              <UserPlus className="h-4 w-4 mr-2" />
              Add Member
            </Button>
          )}
        </CardHeader>
        <CardContent>
          <ProjectMembersTable
            members={members ?? []}
            organizationId={organizationId}
            projectId={projectId}
            currentUserId={currentUserId}
            canManageMembers={canManageMembers}
            isLoading={isLoading}
          />
        </CardContent>
      </Card>

      <AddProjectMemberDialog
        open={showAddDialog}
        onOpenChange={setShowAddDialog}
        organizationId={organizationId}
        projectId={projectId}
        existingMembers={members ?? []}
      />
    </>
  );
}
