import { createFileRoute } from "@tanstack/react-router";

import { ClawHeader } from "@/app/components/claw-header";
import { CloudLayout } from "@/app/components/cloud-layout";
import { Protected } from "@/app/components/protected";

function ClawsIndexPage() {
  return (
    <Protected>
      <CloudLayout>
        <div className="p-6">
          <ClawHeader />
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
