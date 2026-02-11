import { createFileRoute } from "@tanstack/react-router";
import {
  Loader2,
  MoreHorizontal,
  Pencil,
  Plus,
  RefreshCw,
  Trash,
} from "lucide-react";
import { useState } from "react";

import {
  useClawSecrets,
  useRestartClaw,
  useUpdateClawSecrets,
} from "@/app/api/claws";
import { ClawHeader } from "@/app/components/claw-header";
import { CloudLayout } from "@/app/components/cloud-layout";
import { Protected } from "@/app/components/protected";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/app/components/ui/alert-dialog";
import { Button } from "@/app/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/app/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/app/components/ui/dropdown-menu";
import { Input } from "@/app/components/ui/input";
import { Label } from "@/app/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/app/components/ui/table";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/app/components/ui/tabs";
import { Textarea } from "@/app/components/ui/textarea";
import { useClaw } from "@/app/contexts/claw";
import { useOrganization } from "@/app/contexts/organization";

function ClawsSecretsPage() {
  const { selectedOrganization } = useOrganization();
  const { selectedClaw } = useClaw();

  const organizationId = selectedOrganization?.id ?? null;
  const clawId = selectedClaw?.id ?? null;

  const { data: secrets = {}, isLoading } = useClawSecrets(
    organizationId,
    clawId,
  );
  const updateSecrets = useUpdateClawSecrets();
  const restartClaw = useRestartClaw();

  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editKey, setEditKey] = useState<string | null>(null);
  const [deleteKey, setDeleteKey] = useState<string | null>(null);
  const [restartDialogOpen, setRestartDialogOpen] = useState(false);
  const [rawJson, setRawJson] = useState("");
  const [rawError, setRawError] = useState<string | null>(null);

  const mutate = (next: Record<string, string>) => {
    if (!organizationId || !clawId) return;
    updateSecrets.mutate({
      organizationId,
      clawId,
      secrets: next,
    });
  };

  const handleAdd = (name: string, value: string) => {
    mutate({ ...secrets, [name]: value });
    setAddDialogOpen(false);
  };

  const handleEdit = (value: string) => {
    if (editKey) {
      mutate({ ...secrets, [editKey]: value });
    }
    setEditKey(null);
    setEditDialogOpen(false);
  };

  const handleDelete = () => {
    if (deleteKey) {
      const next = { ...secrets };
      delete next[deleteKey];
      mutate(next);
    }
    setDeleteKey(null);
  };

  const handleRestart = () => {
    if (!organizationId || !clawId) return;
    restartClaw.mutate(
      { organizationId, clawId },
      {
        onSuccess: () => setRestartDialogOpen(false),
      },
    );
  };

  const handleSaveRaw = () => {
    try {
      const parsed: unknown = JSON.parse(rawJson);
      if (
        typeof parsed !== "object" ||
        parsed === null ||
        Array.isArray(parsed)
      ) {
        setRawError(
          "JSON must be an object with string keys and string values",
        );
        return;
      }
      for (const [key, value] of Object.entries(
        parsed as Record<string, unknown>,
      )) {
        if (typeof key !== "string" || typeof value !== "string") {
          setRawError(
            "JSON must be an object with string keys and string values",
          );
          return;
        }
      }
      mutate(parsed as Record<string, string>);
      setRawError(null);
    } catch {
      setRawError("Invalid JSON");
    }
  };

  const entries = Object.entries(secrets);

  if (!selectedClaw) {
    return (
      <Protected>
        <CloudLayout>
          <div className="p-6">
            <ClawHeader />
            <div className="flex items-center justify-center rounded-lg border border-dashed py-12 text-center text-muted-foreground">
              <p>Select a claw to manage its secrets.</p>
            </div>
          </div>
        </CloudLayout>
      </Protected>
    );
  }

  if (isLoading) {
    return (
      <Protected>
        <CloudLayout>
          <div className="p-6">
            <ClawHeader />
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          </div>
        </CloudLayout>
      </Protected>
    );
  }

  return (
    <Protected>
      <CloudLayout>
        <div className="p-6">
          <ClawHeader />
          <Tabs
            defaultValue="table"
            onValueChange={(value) => {
              if (value === "raw") {
                setRawJson(JSON.stringify(secrets, null, 2));
                setRawError(null);
              }
            }}
          >
            <div className="flex items-center justify-between">
              <TabsList>
                <TabsTrigger value="table">Table</TabsTrigger>
                <TabsTrigger value="raw">Raw</TabsTrigger>
              </TabsList>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  onClick={() => setRestartDialogOpen(true)}
                  disabled={restartClaw.isPending}
                >
                  {restartClaw.isPending ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <RefreshCw className="mr-2 h-4 w-4" />
                  )}
                  Restart claw
                </Button>
                <Button onClick={() => setAddDialogOpen(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Add variable
                </Button>
              </div>
            </div>

            <TabsContent value="table">
              <div className="space-y-4">
                {entries.length === 0 ? (
                  <div className="flex items-center justify-center rounded-lg border border-dashed py-12 text-center text-muted-foreground">
                    <p>No environment variables yet. Add one to get started.</p>
                  </div>
                ) : (
                  <div className="rounded-lg border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Name</TableHead>
                          <TableHead>Value</TableHead>
                          <TableHead className="w-[50px]" />
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {entries.map(([key]) => (
                          <TableRow key={key}>
                            <TableCell className="font-mono text-sm">
                              {key}
                            </TableCell>
                            <TableCell className="font-mono text-sm text-muted-foreground">
                              {
                                "\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022"
                              }
                            </TableCell>
                            <TableCell>
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <Button variant="ghost" size="icon">
                                    <MoreHorizontal className="h-4 w-4" />
                                  </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end">
                                  <DropdownMenuItem
                                    onClick={() => {
                                      setEditKey(key);
                                      setEditDialogOpen(true);
                                    }}
                                  >
                                    <Pencil className="mr-2 h-4 w-4" />
                                    Edit
                                  </DropdownMenuItem>
                                  <DropdownMenuItem
                                    onClick={() => setDeleteKey(key)}
                                    className="text-destructive focus:text-destructive"
                                  >
                                    <Trash className="mr-2 h-4 w-4" />
                                    Delete
                                  </DropdownMenuItem>
                                </DropdownMenuContent>
                              </DropdownMenu>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </div>
            </TabsContent>

            <TabsContent value="raw">
              <div className="space-y-4">
                <Textarea
                  value={rawJson}
                  onChange={(e) => {
                    setRawJson(e.target.value);
                    setRawError(null);
                  }}
                  className="min-h-[300px] font-mono text-sm"
                />
                {rawError && (
                  <p className="text-sm text-destructive">{rawError}</p>
                )}
                <div className="flex justify-end">
                  <Button onClick={handleSaveRaw}>Save</Button>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </CloudLayout>

      <AddVariableDialog
        open={addDialogOpen}
        onOpenChange={setAddDialogOpen}
        existingKeys={Object.keys(secrets)}
        onAdd={handleAdd}
      />

      <EditVariableDialog
        open={editDialogOpen}
        onOpenChange={(open) => {
          setEditDialogOpen(open);
          if (!open) setEditKey(null);
        }}
        name={editKey}
        onSave={handleEdit}
      />

      <AlertDialog
        open={deleteKey !== null}
        onOpenChange={(open) => {
          if (!open) setDeleteKey(null);
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete variable</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete{" "}
              <span className="font-mono font-semibold">{deleteKey}</span>? This
              action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog open={restartDialogOpen} onOpenChange={setRestartDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Restart claw gateway?</AlertDialogTitle>
            <AlertDialogDescription>
              This will restart the gateway process for this claw. Use this
              after updating secrets so the running process picks up fresh
              configuration.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={restartClaw.isPending}>
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleRestart}
              disabled={restartClaw.isPending}
            >
              {restartClaw.isPending ? "Restarting…" : "Restart"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Protected>
  );
}

function AddVariableDialog({
  open,
  onOpenChange,
  existingKeys,
  onAdd,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  existingKeys: string[];
  onAdd: (name: string, value: string) => void;
}) {
  const [name, setName] = useState("");
  const [value, setValue] = useState("");

  const handleClose = (isOpen: boolean) => {
    if (!isOpen) {
      setName("");
      setValue("");
    }
    onOpenChange(isOpen);
  };

  const trimmedName = name.trim();
  const nameExists = existingKeys.includes(trimmedName);
  const canSubmit = trimmedName !== "" && value.trim() !== "" && !nameExists;

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[425px]">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (canSubmit) {
              onAdd(trimmedName, value);
              setName("");
              setValue("");
            }
          }}
        >
          <DialogHeader>
            <DialogTitle>Add variable</DialogTitle>
            <DialogDescription>
              Add a new environment variable.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 px-6 py-4">
            <div className="grid gap-2">
              <Label htmlFor="var-name">Name</Label>
              <Input
                id="var-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="VARIABLE_NAME"
                className="font-mono"
                autoFocus
              />
              {nameExists && (
                <p className="text-sm text-destructive">
                  A variable with this name already exists.
                </p>
              )}
            </div>
            <div className="grid gap-2">
              <Label htmlFor="var-value">Value</Label>
              <Input
                id="var-value"
                autoComplete="off"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                placeholder="Enter value"
                className="font-mono"
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => handleClose(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={!canSubmit}>
              Add
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function EditVariableDialog({
  open,
  onOpenChange,
  name,
  onSave,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  name: string | null;
  onSave: (value: string) => void;
}) {
  const [value, setValue] = useState("");

  const handleClose = (isOpen: boolean) => {
    if (!isOpen) {
      setValue("");
    }
    onOpenChange(isOpen);
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[425px]">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (value.trim() !== "") {
              onSave(value);
              setValue("");
            }
          }}
        >
          <DialogHeader>
            <DialogTitle>Edit variable</DialogTitle>
            <DialogDescription>
              Update the value for{" "}
              <span className="font-mono font-semibold">{name}</span>.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 px-6 py-4">
            <div className="grid gap-2">
              <Label htmlFor="edit-name">Name</Label>
              <Input
                id="edit-name"
                value={name ?? ""}
                disabled
                className="font-mono"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="edit-value">Value</Label>
              <Input
                id="edit-value"
                autoComplete="off"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                placeholder="Enter new value"
                className="font-mono"
                autoFocus
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => handleClose(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={value.trim() === ""}>
              Save
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export const Route = createFileRoute("/$orgSlug/claws/$clawSlug/secrets")({
  component: ClawsSecretsPage,
});
