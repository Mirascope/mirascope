import { createFileRoute, Outlet } from "@tanstack/react-router";
import { Loader2 } from "lucide-react";
import { useEffect } from "react";

import { ClawHeader } from "@/app/components/claw-header";
import { useClaw } from "@/app/contexts/claw";

function ClawLayout() {
  const { clawSlug } = Route.useParams();
  const { claws, setSelectedClaw, isLoading } = useClaw();

  // Sync claw from URL slug
  useEffect(() => {
    if (isLoading) return;
    const claw = claws.find((c) => c.slug === clawSlug);
    if (claw) {
      setSelectedClaw(claw);
    }
  }, [clawSlug, claws, isLoading, setSelectedClaw]);

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const claw = claws.find((c) => c.slug === clawSlug);
  if (!claw) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-semibold">Not Found</h1>
          <p className="text-muted-foreground mt-2">Claw not found.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <div className="shrink-0 px-6 pt-6">
        <ClawHeader />
      </div>
      <div className="min-h-0 flex-1">
        <Outlet />
      </div>
    </div>
  );
}

export const Route = createFileRoute("/$orgSlug/claws/$clawSlug")({
  component: ClawLayout,
});
