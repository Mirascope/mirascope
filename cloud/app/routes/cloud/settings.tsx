import { DashboardLayout } from "@/app/components/dashboard-layout";
import { createFileRoute } from "@tanstack/react-router";
import { Protected } from "@/app/components/protected";

function CloudSettingsPage() {
  return (
    <Protected>
      <DashboardLayout>
        <div className="flex items-center justify-center h-full">
          <div className="text-2xl font-semibold">Settings Coming Soon...</div>
        </div>
      </DashboardLayout>
    </Protected>
  );
}

export const Route = createFileRoute("/cloud/settings")({
  component: CloudSettingsPage,
});
