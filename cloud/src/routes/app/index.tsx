import { FrontPage } from "@/src/components/FrontPage";
// Import directly to avoid circular dependencies through barrel exports
import Protected from "@/src/components/core/navigation/Protected";
import { createFileRoute } from "@tanstack/react-router";
import DashboardLayout from "@/src/components/core/layout/DashboardLayout";

export const Route = createFileRoute("/app/")({
  component: App,
});

function App() {
  return (
    <DashboardLayout>
      <Protected>
        <FrontPage />
      </Protected>
    </DashboardLayout>
  );
}
