import { createFileRoute } from "@tanstack/react-router";

import { CloudLayout } from "@/app/components/cloud-layout";
import { Protected } from "@/app/components/protected";

function ClawsIndexPage() {
  return (
    <Protected>
      <CloudLayout>
        <div className="p-6">
          <h1 className="text-2xl font-semibold mb-2">Claws</h1>
          <p className="text-muted-foreground mb-6">
            Deploy and manage AI-powered claws for your organization
          </p>
          <div className="flex h-24 items-center justify-center rounded-lg border border-dashed bg-muted/30">
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
