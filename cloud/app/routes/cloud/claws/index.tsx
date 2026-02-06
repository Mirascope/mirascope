import { createFileRoute } from "@tanstack/react-router";

import { CloudLayout } from "@/app/components/cloud-layout";
import { Protected } from "@/app/components/protected";
import { useClaw } from "@/app/contexts/claw";

function ClawsIndexPage() {
  const { selectedClaw } = useClaw();

  return (
    <Protected>
      <CloudLayout>
        <div className="p-6">
          <h1 className="text-2xl font-semibold mb-1">Chat</h1>
          <p className="text-muted-foreground mb-6">
            {selectedClaw
              ? (selectedClaw.displayName ?? selectedClaw.slug)
              : "Select a claw from the sidebar to get started"}
          </p>
          <div className="flex h-64 items-center justify-center rounded-lg border border-dashed bg-muted/30">
            <p className="text-sm text-muted-foreground">Coming soon</p>
          </div>
        </div>
      </CloudLayout>
    </Protected>
  );
}

export const Route = createFileRoute("/cloud/claws/")({
  component: ClawsIndexPage,
});
