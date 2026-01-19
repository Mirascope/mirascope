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
import { ApiKeysTable } from "@/app/components/api-keys-table";
import { CreateApiKeyModal } from "@/app/components/create-api-key-modal";
import { useAllApiKeys } from "@/app/api/api-keys";

interface ApiKeysSectionProps {
  organizationId: string;
  canManageApiKeys: boolean;
}

export function ApiKeysSection({
  organizationId,
  canManageApiKeys,
}: ApiKeysSectionProps) {
  const [showCreateModal, setShowCreateModal] = useState(false);

  const { data: apiKeys, isLoading } = useAllApiKeys(organizationId);

  return (
    <>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <div>
            <CardTitle>API Keys</CardTitle>
            <CardDescription>
              Used to authenticate requests to the Mirascope API.
              <br />
              Each key is scoped to a specific project and environment.
            </CardDescription>
          </div>
          {canManageApiKeys && (
            <Button onClick={() => setShowCreateModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create API Key
            </Button>
          )}
        </CardHeader>
        <CardContent>
          <ApiKeysTable
            apiKeys={apiKeys ?? []}
            organizationId={organizationId}
            canManageApiKeys={canManageApiKeys}
            isLoading={isLoading}
          />
        </CardContent>
      </Card>

      <CreateApiKeyModal
        open={showCreateModal}
        onOpenChange={setShowCreateModal}
        organizationId={organizationId}
      />
    </>
  );
}
