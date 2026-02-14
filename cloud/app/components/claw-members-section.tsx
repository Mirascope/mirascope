import { UserPlus } from "lucide-react";
import { useState } from "react";

import { useClawMembers } from "@/app/api/claw-memberships";
import { AddClawMemberDialog } from "@/app/components/add-claw-member-dialog";
import { ClawMembersTable } from "@/app/components/claw-members-table";
import { Button } from "@/app/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";

interface ClawMembersSectionProps {
  organizationId: string;
  clawId: string;
  currentUserId: string;
  canManageMembers: boolean;
}

export function ClawMembersSection({
  organizationId,
  clawId,
  currentUserId,
  canManageMembers,
}: ClawMembersSectionProps) {
  const [showAddDialog, setShowAddDialog] = useState(false);

  const { data: members, isLoading } = useClawMembers(organizationId, clawId);

  return (
    <>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <div>
            <CardTitle>Claw Members</CardTitle>
            <CardDescription>
              Manage who has access to this claw
            </CardDescription>
          </div>
          {canManageMembers && (
            <Button variant="outline" onClick={() => setShowAddDialog(true)}>
              <UserPlus className="h-4 w-4 mr-2" />
              Add Member
            </Button>
          )}
        </CardHeader>
        <CardContent>
          <ClawMembersTable
            members={members ?? []}
            organizationId={organizationId}
            clawId={clawId}
            currentUserId={currentUserId}
            canManageMembers={canManageMembers}
            isLoading={isLoading}
          />
        </CardContent>
      </Card>

      <AddClawMemberDialog
        open={showAddDialog}
        onOpenChange={setShowAddDialog}
        organizationId={organizationId}
        clawId={clawId}
        existingMembers={members ?? []}
      />
    </>
  );
}
