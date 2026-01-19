import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { Protected } from "@/app/components/protected";

function CloudIndexPage() {
  const navigate = useNavigate();

  useEffect(() => {
    void navigate({ to: "/cloud/dashboard", replace: true });
  }, [navigate]);

  return null;
}

export const Route = createFileRoute("/cloud/")({
  component: () => (
    <Protected>
      <CloudIndexPage />
    </Protected>
  ),
});
