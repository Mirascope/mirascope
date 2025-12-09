import { createFileRoute } from "@tanstack/react-router";
import { Protected } from "@/src/components/protected";
import { DashboardLayout } from "@/src/components/dashboard-layout";
import { useOrganization } from "@/src/contexts/organization";
import { useProject } from "@/src/contexts/project";
import { useEnvironment } from "@/src/contexts/environment";

export const Route = createFileRoute("/dashboard/")({
  component: DashboardPage,
});

function DashboardContent() {
  const { selectedOrganization } = useOrganization();
  const { selectedProject } = useProject();
  const { selectedEnvironment } = useEnvironment();

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
      <DashboardLayout>
        <DashboardContent />
      </DashboardLayout>
    </Protected>
  );
}
