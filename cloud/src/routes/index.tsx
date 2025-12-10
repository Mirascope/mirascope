import { FrontPage } from "@/src/components/FrontPage";
import { Protected } from "@/src/components/core";
import { createFileRoute } from "@tanstack/react-router";
import { DashboardLayout } from "../components/core";

export const Route = createFileRoute("/")({
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
