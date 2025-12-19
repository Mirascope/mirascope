import { createFileRoute } from "@tanstack/react-router";
import { Protected } from "@/app/components/protected";
import { DashboardLayout } from "@/app/components/dashboard-layout";

export const Route = createFileRoute("/dashboard/settings")({
  component: SettingsPage,
});

function SettingsPage() {
  return (
    <Protected>
      <DashboardLayout>
        <div className="p-6">
          <h1 className="text-2xl font-semibold mb-4">Settings</h1>
          <p className="text-muted-foreground">Settings page coming soon...</p>
        </div>
      </DashboardLayout>
    </Protected>
  );
}
