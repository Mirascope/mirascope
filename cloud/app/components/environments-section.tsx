import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";
import { Button } from "@/app/components/ui/button";
import { Plus } from "lucide-react";
import { EnvironmentsTable } from "@/app/components/environments-table";
import { CreateEnvironmentModal } from "@/app/components/create-environment-modal";
import { useEnvironments } from "@/app/api/environments";

interface EnvironmentsSectionProps {
  organizationId: string;
  projectId: string;
  canManageEnvironments: boolean;
}

export function EnvironmentsSection({
  organizationId,
  projectId,
  canManageEnvironments,
}: EnvironmentsSectionProps) {
  const [showCreateModal, setShowCreateModal] = useState(false);

  const { data: environments, isLoading } = useEnvironments(
    organizationId,
    projectId,
  );

  return (
    <>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <div>
            <CardTitle>Environments</CardTitle>
            <CardDescription>
              Manage environments for this project (e.g., development, staging,
              production)
            </CardDescription>
          </div>
          {canManageEnvironments && (
            <Button onClick={() => setShowCreateModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Environment
            </Button>
          )}
        </CardHeader>
        <CardContent>
          <EnvironmentsTable
            environments={environments ?? []}
            canManageEnvironments={canManageEnvironments}
            isLoading={isLoading}
          />
        </CardContent>
      </Card>

      <CreateEnvironmentModal
        open={showCreateModal}
        onOpenChange={setShowCreateModal}
      />
    </>
  );
}
