import { MoreHorizontal, Trash2, Loader2 } from "lucide-react";
import { useState } from "react";

import type { ApiKeyWithContext } from "@/api/api-keys.schemas";

import { DeleteApiKeyModal } from "@/app/components/delete-api-key-modal";
import { Button } from "@/app/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
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

interface ApiKeysTableProps {
  apiKeys: readonly ApiKeyWithContext[];
  organizationId: string;
  canManageApiKeys: boolean;
  isLoading: boolean;
}

export function ApiKeysTable({
  apiKeys,
  organizationId,
  canManageApiKeys,
  isLoading,
}: ApiKeysTableProps) {
  const [deleteTarget, setDeleteTarget] = useState<ApiKeyWithContext | null>(
    null,
  );

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  // Empty state
  if (apiKeys.length === 0) {
    return (
      <div className="text-muted-foreground flex items-center justify-center rounded-lg border border-dashed py-12 text-center">
        <p>No API keys yet. Create one to get started!</p>
      </div>
    );
  }

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "Never";
    return new Date(dateString).toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  return (
    <>
      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Key</TableHead>
              <TableHead>Project</TableHead>
              <TableHead>Environment</TableHead>
              <TableHead>Created</TableHead>
              <TableHead>Last Used</TableHead>
              {canManageApiKeys && <TableHead className="w-[50px]"></TableHead>}
            </TableRow>
          </TableHeader>
          <TableBody>
            {apiKeys.map((apiKey) => (
              <TableRow key={apiKey.id}>
                <TableCell>
                  <span className="font-medium">{apiKey.name}</span>
                </TableCell>
                <TableCell>
                  <code className="text-sm text-muted-foreground">
                    {apiKey.keyPrefix}
                  </code>
                </TableCell>
                <TableCell>
                  <span className="text-sm">{apiKey.projectName}</span>
                </TableCell>
                <TableCell>
                  <span className="text-sm">{apiKey.environmentName}</span>
                </TableCell>
                <TableCell>
                  <span className="text-sm text-muted-foreground">
                    {formatDate(apiKey.createdAt)}
                  </span>
                </TableCell>
                <TableCell>
                  <span className="text-sm text-muted-foreground">
                    {formatDate(apiKey.lastUsedAt)}
                  </span>
                </TableCell>
                {canManageApiKeys && (
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem
                          className="text-destructive focus:text-destructive"
                          onClick={() => setDeleteTarget(apiKey)}
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete
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

      <DeleteApiKeyModal
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        apiKey={deleteTarget}
        organizationId={organizationId}
      />
    </>
  );
}
