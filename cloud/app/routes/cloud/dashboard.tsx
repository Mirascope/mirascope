import { CenteredLayout } from "@/app/components/centered-layout";
import { createFileRoute } from "@tanstack/react-router";
import { Protected } from "@/app/components/protected";

function CloudDashboardPage() {
  return (
    <Protected>
      <CenteredLayout>
        <div className="text-2xl font-semibold">Dashboard Coming Soon...</div>
      </CenteredLayout>
    </Protected>
  );
}

export const Route = createFileRoute("/cloud/dashboard")({
  component: CloudDashboardPage,
});
