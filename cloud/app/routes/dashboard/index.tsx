import { createFileRoute } from "@tanstack/react-router";
import { Loader2 } from "lucide-react";
import { Protected } from "@/app/components/protected";
import { CloudLayout } from "@/app/components/cloud-layout";
import { useOrganization } from "@/app/contexts/organization";
import { useProject } from "@/app/contexts/project";
import { useEnvironment } from "@/app/contexts/environment";
import { useOrganizationRouterBalance } from "@/app/api/organizations";
import { centicentsToDollars } from "@/api/router/cost-utils";
import { PurchaseRouterCreditsDialog } from "@/app/components/purchase-router-credits-dialog";

export const Route = createFileRoute("/dashboard/")({
  component: DashboardPage,
});

function DashboardContent() {
  const { selectedOrganization } = useOrganization();
  const { selectedProject } = useProject();
  const { selectedEnvironment } = useEnvironment();

  const { data: routerBalance, isLoading: routerBalanceLoading } =
    useOrganizationRouterBalance(selectedOrganization?.id);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-4">Dashboard</h1>
      <div className="grid gap-4">
        <div className="p-4 rounded-lg border border-border bg-card">
          <h2 className="text-sm font-medium text-muted-foreground mb-1">
            Organization
          </h2>
          <p className="text-lg">
            {selectedOrganization?.name || "No organization selected"}
          </p>
        </div>
        {selectedOrganization && (
          <div className="p-4 rounded-lg border border-border bg-card">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-sm font-medium text-muted-foreground">
                Router Credits
              </h2>
              {routerBalance && (
                <PurchaseRouterCreditsDialog
                  organizationId={selectedOrganization.id}
                  currentBalance={centicentsToDollars(routerBalance.balance)}
                />
              )}
            </div>
            <p className="text-lg font-semibold">
              {routerBalanceLoading ? (
                <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
              ) : routerBalance ? (
                `$${centicentsToDollars(routerBalance.balance).toFixed(2)}`
              ) : (
                <span className="text-muted-foreground">—</span>
              )}
            </p>
          </div>
        )}
        <div className="p-4 rounded-lg border border-border bg-card">
          <h2 className="text-sm font-medium text-muted-foreground mb-1">
            Project
          </h2>
          <p className="text-lg">
            {selectedProject?.name || "No project selected"}
          </p>
        </div>
        <div className="p-4 rounded-lg border border-border bg-card">
          <h2 className="text-sm font-medium text-muted-foreground mb-1">
            Environment
          </h2>
          <p className="text-lg">
            {selectedEnvironment?.name || "No environment selected"}
          </p>
        </div>
      </div>
    </div>
  );
}

function DashboardPage() {
  return (
    <Protected>
      <CloudLayout>
        <DashboardContent />
      </CloudLayout>
    </Protected>
  );
}
