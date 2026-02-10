import { createFileRoute, Navigate } from "@tanstack/react-router";

import { useClaw } from "@/app/contexts/claw";

function ClawsRedirect() {
  const { orgSlug } = Route.useParams();
  const { selectedClaw, isLoading } = useClaw();

  if (isLoading) return null;

  if (selectedClaw) {
    return (
      <Navigate
        to="/$orgSlug/claws/$clawSlug/chat"
        params={{ orgSlug, clawSlug: selectedClaw.slug }}
        replace
      />
    );
  }

  // No claw selected, go to org dashboard
  return <Navigate to="/$orgSlug" params={{ orgSlug }} replace />;
}

export const Route = createFileRoute("/$orgSlug/claws/")({
  component: ClawsRedirect,
});
