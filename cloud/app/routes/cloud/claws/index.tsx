import { createFileRoute } from "@tanstack/react-router";

import { instanceConfig, statusConfig } from "@/app/components/claw-card";
import { CloudLayout } from "@/app/components/cloud-layout";
import { Protected } from "@/app/components/protected";
import { Badge } from "@/app/components/ui/badge";
import { useClaw } from "@/app/contexts/claw";

function ClawsIndexPage() {
  const { selectedClaw } = useClaw();

  return (
    <Protected>
      <CloudLayout>
        <div className="p-6">
          {selectedClaw ? (
            <>
              <div className="flex items-center gap-2 mb-1">
                <h1 className="text-2xl font-semibold">
                  {selectedClaw.displayName ?? selectedClaw.slug}
                </h1>
                <Badge
                  pill
                  variant="outline"
                  className="shrink-0 font-normal bg-white text-primary border-primary/40 dark:bg-primary/10 dark:text-primary-foreground dark:border-primary/40"
                >
                  {instanceConfig[selectedClaw.instanceType]}
                </Badge>
                <Badge
                  pill
                  variant="outline"
                  className={`shrink-0 ${statusConfig[selectedClaw.status].pill}`}
                >
                  {statusConfig[selectedClaw.status].label}
                </Badge>
              </div>
              <p className="text-muted-foreground mb-6">Chat</p>
            </>
          ) : (
            <>
              <h1 className="text-2xl font-semibold mb-1">Chat</h1>
              <p className="text-muted-foreground mb-6">
                Select a claw from the sidebar to get started
              </p>
            </>
          )}
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
