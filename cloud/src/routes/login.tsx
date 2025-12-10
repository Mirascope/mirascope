import { createFileRoute } from "@tanstack/react-router";
import { LoginPage } from "@/src/components/dashboard";
import { DashboardLayout } from "@/src/components/core";

export const Route = createFileRoute("/login")({
  component: () => (
    <DashboardLayout>
      <LoginPage />
    </DashboardLayout>
  ),
});
