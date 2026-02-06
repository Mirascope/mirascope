import { createFileRoute } from "@tanstack/react-router";

import { CloudLayout } from "@/app/components/cloud-layout";
import { Protected } from "@/app/components/protected";
import { useClaw } from "@/app/contexts/claw";

function ClawsConfigPage() {
  const { selectedClaw } = useClaw();

  return (
    <Protected>
      <CloudLayout>
        <div className="p-6">
          <h1 className="text-2xl font-semibold mb-1">Config</h1>
          <p className="text-muted-foreground mb-6">
            {selectedClaw
              ? `Configuration for ${selectedClaw.displayName ?? selectedClaw.slug}`
              : "Select a claw from the sidebar to manage configuration"}
          </p>
          <div className="flex h-24 items-center justify-center rounded-lg border border-dashed bg-muted/30">
            <p className="text-sm text-muted-foreground">Coming soon</p>
          </div>
        </div>
      </CloudLayout>
    </Protected>
  );
}

export const Route = createFileRoute("/cloud/claws/config")({
  component: ClawsConfigPage,
});
