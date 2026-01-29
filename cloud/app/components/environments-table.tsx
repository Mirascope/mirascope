import { MoreHorizontal, Pencil, Trash2, Loader2 } from "lucide-react";
import { useState } from "react";

import type { PublicEnvironment } from "@/db/schema";

import { DeleteEnvironmentModal } from "@/app/components/delete-environment-modal";
import { RenameEnvironmentModal } from "@/app/components/rename-environment-modal";
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

interface EnvironmentsTableProps {
  environments: readonly PublicEnvironment[];
  canManageEnvironments: boolean;
  isLoading: boolean;
}

export function EnvironmentsTable({
  environments,
  canManageEnvironments,
  isLoading,
}: EnvironmentsTableProps) {
  const [renameTarget, setRenameTarget] = useState<PublicEnvironment | null>(
    null,
  );
  const [deleteTarget, setDeleteTarget] = useState<PublicEnvironment | null>(
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
  if (environments.length === 0) {
    return (
      <div className="text-muted-foreground flex items-center justify-center rounded-lg border border-dashed py-12 text-center">
        <p>No environments yet. Create one to get started!</p>
      </div>
    );
  }

  return (
    <>
      <div className="rounded-lg border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Slug</TableHead>
              {canManageEnvironments && (
                <TableHead className="w-[50px]"></TableHead>
              )}
            </TableRow>
          </TableHeader>
          <TableBody>
            {environments.map((environment) => (
              <TableRow key={environment.id}>
                <TableCell>
                  <span className="font-medium">{environment.name}</span>
                </TableCell>
                <TableCell>
                  <code className="text-sm text-muted-foreground">
                    {environment.slug}
                  </code>
                </TableCell>
                {canManageEnvironments && (
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem
                          onClick={() => setRenameTarget(environment)}
                        >
                          <Pencil className="h-4 w-4 mr-2" />
                          Rename
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                          className="text-destructive focus:text-destructive"
                          onClick={() => setDeleteTarget(environment)}
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

      <RenameEnvironmentModal
        open={!!renameTarget}
        onOpenChange={(open) => !open && setRenameTarget(null)}
        environment={renameTarget}
      />

      <DeleteEnvironmentModal
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        environment={deleteTarget}
      />
    </>
  );
}
