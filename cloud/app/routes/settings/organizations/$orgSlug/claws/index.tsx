import { createFileRoute, Navigate } from "@tanstack/react-router";
import { Loader2 } from "lucide-react";
import { useState } from "react";

import { CreateClawModal } from "@/app/components/create-claw-modal";
import { Button } from "@/app/components/ui/button";
import { useClaw } from "@/app/contexts/claw";
import { useOrganization } from "@/app/contexts/organization";

function ClawsIndexRedirect() {
  const { orgSlug } = Route.useParams();
  const { selectedOrganization } = useOrganization();
  const { claws, selectedClaw, isLoading } = useClaw();
  const [showCreateModal, setShowCreateModal] = useState(false);

  if (!selectedOrganization || isLoading) {
    return (
      <div className="flex justify-center pt-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const defaultClaw = selectedClaw || claws[0];
  if (defaultClaw) {
    return (
      <Navigate
        to="/settings/organizations/$orgSlug/claws/$clawSlug"
        params={{ orgSlug, clawSlug: defaultClaw.slug }}
        replace
      />
    );
  }

  return (
    <div className="max-w-3xl">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold">Claws</h1>
        <p className="text-muted-foreground mt-1">
          Manage your claw settings and members
        </p>
      </div>
      <div className="flex flex-col items-center gap-4 pt-12">
        <p className="text-muted-foreground">
          No claws yet. Create one to get started!
        </p>
        <Button onClick={() => setShowCreateModal(true)}>Create Claw</Button>
      </div>
      <CreateClawModal
        open={showCreateModal}
        onOpenChange={setShowCreateModal}
      />
    </div>
  );
}

export const Route = createFileRoute("/settings/organizations/$orgSlug/claws/")(
  {
    component: ClawsIndexRedirect,
  },
);
