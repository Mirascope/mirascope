import { createFileRoute } from "@tanstack/react-router";
import { Loader2, Trash2 } from "lucide-react";
import { useState } from "react";

import { useSubscription } from "@/app/api/organizations";
import { ClawMembersSection } from "@/app/components/claw-members-section";
import { CreateClawModal } from "@/app/components/create-claw-modal";
import { DeleteClawModal } from "@/app/components/delete-claw-modal";
import { Button } from "@/app/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";
import { Input } from "@/app/components/ui/input";
import { Label } from "@/app/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/app/components/ui/select";
import { useAuth } from "@/app/contexts/auth";
import { useClaw } from "@/app/contexts/claw";
import { useOrganization } from "@/app/contexts/organization";
import { PLAN_LIMITS } from "@/payments/plans";

const STATUS_LABELS: Record<string, string> = {
  active: "Active",
  pending: "Pending",
  provisioning: "Provisioning",
  error: "Error",
  paused: "Paused",
};

function ClawsSettingsPage() {
  const { selectedOrganization } = useOrganization();
  const { claws, selectedClaw, setSelectedClaw, isLoading } = useClaw();
  const { user } = useAuth();
  const { data: subscription } = useSubscription(selectedOrganization?.id);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const orgRole = selectedOrganization?.role;
  const canManageMembers = orgRole === "OWNER" || orgRole === "ADMIN";

  const planTier = subscription?.currentPlan ?? "free";
  const limits = PLAN_LIMITS[planTier];

  const handleClawChange = (value: string) => {
    if (value === "__create_new__") {
      setShowCreateModal(true);
    } else {
      const claw = claws.find((c) => c.id === value);
      setSelectedClaw(claw ?? null);
    }
  };

  const header = (
    <div className="mb-6 flex items-start justify-between">
      <div>
        <h1 className="text-2xl font-semibold">Claws</h1>
        <p className="text-muted-foreground mt-1">
          Manage your claw settings and members
        </p>
      </div>
      {selectedOrganization && !isLoading && (
        <Select value={selectedClaw?.id || ""} onValueChange={handleClawChange}>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Select claw" />
          </SelectTrigger>
          <SelectContent>
            {claws.map((claw) => (
              <SelectItem key={claw.id} value={claw.id}>
                {claw.displayName ?? claw.slug}
              </SelectItem>
            ))}
            <SelectItem
              value="__create_new__"
              className="text-primary font-medium"
            >
              + Create New Claw
            </SelectItem>
          </SelectContent>
        </Select>
      )}
    </div>
  );

  if (!selectedOrganization) {
    return (
      <div className="max-w-2xl">
        {header}
        <div className="flex justify-center pt-12">
          <div className="text-muted-foreground">
            Please select an organization first
          </div>
        </div>
        <CreateClawModal
          open={showCreateModal}
          onOpenChange={setShowCreateModal}
        />
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="max-w-2xl">
        {header}
        <div className="flex justify-center pt-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
        <CreateClawModal
          open={showCreateModal}
          onOpenChange={setShowCreateModal}
        />
      </div>
    );
  }

  if (!selectedClaw) {
    return (
      <div className="max-w-2xl">
        {header}
        <div className="flex justify-center pt-12">
          <div className="text-muted-foreground">
            {claws.length === 0
              ? "No claws yet. Create one to get started!"
              : "Please select a claw"}
          </div>
        </div>
        <CreateClawModal
          open={showCreateModal}
          onOpenChange={setShowCreateModal}
        />
      </div>
    );
  }

  return (
    <div className="max-w-3xl space-y-6">
      {header}

      {/* Plan usage summary */}
      <p className="text-sm text-muted-foreground">
        Plan: {planTier.charAt(0).toUpperCase() + planTier.slice(1)} (
        {claws.length}/{limits.claws} claws used)
      </p>

      {/* Claw details */}
      <Card>
        <CardHeader>
          <CardTitle>Claw Details</CardTitle>
          <CardDescription>Basic information about this claw</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="claw-name">Name</Label>
            <Input
              id="claw-name"
              value={selectedClaw.displayName ?? ""}
              readOnly
              className="bg-muted"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="claw-slug">Slug</Label>
            <Input
              id="claw-slug"
              value={selectedClaw.slug}
              readOnly
              className="bg-muted"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="claw-status">Status</Label>
            <Input
              id="claw-status"
              value={STATUS_LABELS[selectedClaw.status] ?? selectedClaw.status}
              readOnly
              className="bg-muted"
            />
          </div>
        </CardContent>
      </Card>

      {/* Members */}
      <ClawMembersSection
        organizationId={selectedOrganization.id}
        clawId={selectedClaw.id}
        currentUserId={user?.id ?? ""}
        canManageMembers={canManageMembers}
      />

      {/* Danger zone */}
      <Card className="border-destructive">
        <CardHeader>
          <CardTitle className="text-destructive">Danger Zone</CardTitle>
          <CardDescription>
            Irreversible and destructive actions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Delete this claw</p>
              <p className="text-sm text-muted-foreground">
                Once you delete a claw, there is no going back. Please be
                certain.
              </p>
            </div>
            <Button
              variant="destructive"
              onClick={() => setShowDeleteModal(true)}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete
            </Button>
          </div>
        </CardContent>
      </Card>

      <CreateClawModal
        open={showCreateModal}
        onOpenChange={setShowCreateModal}
      />
      <DeleteClawModal
        open={showDeleteModal}
        onOpenChange={setShowDeleteModal}
        claw={selectedClaw}
      />
    </div>
  );
}

export const Route = createFileRoute("/cloud/settings/claws")({
  component: ClawsSettingsPage,
});
